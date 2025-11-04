import serial
import cv2
import pytesseract
import time
import mysql.connector
import re

# --- Arduino Serial Connection ---
arduino = serial.Serial('COM3', 115200)   # 🔹 Change 'COM3' if needed
time.sleep(2)

# --- MySQL Database Connection ---
db = mysql.connector.connect(
    host="localhost",
    user="root",
    password="yourpassword",   # 🔹 Change this
    database="smart_gate_project"
)
cursor = db.cursor()

image_data = b""
capturing = False

print("🚦 Smart Gate System Ready")
print("Waiting for vehicle detection...\n")

# --- Optional: Set Tesseract path if needed (Windows example) ---
# pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

while True:
    line = arduino.readline()

    # --- Start receiving image from Arduino ---
    if b'STARTIMG' in line:
        print("📸 Receiving image from Arduino...")
        capturing = True
        image_data = b""

    # --- End of image ---
    elif b'ENDIMG' in line:
        print("✅ Image received. Saving file...")
        with open("vehicle.jpg", "wb") as f:
            f.write(image_data)
        capturing = False

        # --- Process captured image ---
        img = cv2.imread("vehicle.jpg")
        if img is None:
            print("⚠ No image captured correctly.")
            continue

        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        gray = cv2.bilateralFilter(gray, 11, 17, 17)

        # --- Extract text from number plate ---
        text = pytesseract.image_to_string(gray)
        print("🔍 OCR Result:", text.strip())

        # --- Match vehicle number (e.g., KA01AB1234) ---
        match = re.search(r'[A-Z]{2}\d{2}[A-Z]{1,2}\d{3,4}', text)
        vehicle_number = match.group() if match else None

        if vehicle_number:
            print("🚗 Detected Vehicle Number:", vehicle_number)

            # --- Check in database ---
            query = "SELECT * FROM allowed_vehicles WHERE vehicle_number = %s"
            cursor.execute(query, (vehicle_number,))
            result = cursor.fetchone()

            if result:
                print("✅ Authorized Vehicle")
                arduino.write(b'AUTHORIZED\n')
                cursor.execute("""
                    INSERT INTO gate_logs (vehicle_number, event_type, status, gate_action, remarks)
                    VALUES (%s, 'entry', 'granted', 'opened', 'Authorized vehicle entry granted')
                """, (vehicle_number,))
                db.commit()
            else:
                print("❌ Unauthorized Vehicle - Access Denied")
                arduino.write(b'UNAUTHORIZED\n')

                cursor.execute("SELECT * FROM waiting_vehicles WHERE vehicle_number = %s", (vehicle_number,))
                exists = cursor.fetchone()

                if not exists:
                    cursor.execute("INSERT INTO waiting_vehicles (vehicle_number) VALUES (%s)", (vehicle_number,))
                    db.commit()

                cursor.execute("""
                    INSERT INTO gate_logs (vehicle_number, event_type, status, gate_action,