import serial
import cv2
import pytesseract
import time
import mysql.connector
import re

# ----------------------------------------------
# 1️⃣ CONNECT TO MYSQL DATABASE
# ----------------------------------------------
db = mysql.connector.connect(
    host="localhost",
    user="root",
    password="yourpassword",  # Change to your MySQL password
    database="smart_gate_project"
)
cursor = db.cursor()

# ----------------------------------------------
# 2️⃣ CONNECT TO ARDUINO
# ----------------------------------------------
arduino = serial.Serial('COM3', 115200)  # Update COM port if needed
time.sleep(2)

image_data = b""
capturing = False

print("\n🚪 Smart Gate System Ready. Waiting for vehicle...\n")

# ----------------------------------------------
# 3️⃣ MAIN LOOP
# ----------------------------------------------
while True:
    line = arduino.readline()

    if b'STARTIMG' in line:
        print("📸 Receiving image from Arduino...")
        capturing = True
        image_data = b""

    elif b'ENDIMG' in line:
        print("✅ Image received. Saving image...")
        with open("vehicle.jpg", "wb") as f:
            f.write(image_data)
        capturing = False

        # --- Process Captured Image ---
        img = cv2.imread("vehicle.jpg")
        if img is None:
            print("⚠ No image captured properly. Skipping.")
            continue

        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        gray = cv2.bilateralFilter(gray, 11, 17, 17)
        text = pytesseract.image_to_string(gray)
        print("🧾 Extracted Text:", text.strip())

        match = re.search(r'[A-Z]{2}\d{2}[A-Z]{1,2}\d{3,4}', text)
        vehicle_number = match.group() if match else None

        if not vehicle_number:
            print("❌ Vehicle number not detected properly.")
            arduino.write(b'CLOSE_GATE\n')
            continue

        print(f"🔍 Detected Vehicle Number: {vehicle_number}")

        # --- Database Check ---
        cursor.execute("SELECT * FROM allowed_vehicles WHERE vehicle_number = %s", (vehicle_number,))
        authorized = cursor.fetchone()

        cursor.execute("SELECT * FROM blocked_vehicles WHERE vehicle_number = %s", (vehicle_number,))
        blocked = cursor.fetchone()

        # --- Handle Cases ---
        if authorized:
            print(f"✅ {vehicle_number} is authorized. Opening gate...")
            arduino.write(b'OPEN_GATE\n')
            cursor.execute("""
                INSERT INTO gate_logs (vehicle_number, event_type, status, gate_action, remarks)
                VALUES (%s, 'entry', 'granted', 'opened', 'Authorized vehicle entry granted')
            """, (vehicle_number,))
            db.commit()

        elif blocked:
            print(f"🚫 {vehicle_number} is blocked. Gate remains closed.")
            arduino.write(b'CLOSE_GATE\n')
            cursor.execute("""
                INSERT INTO gate_logs (vehicle_number, event_type, status, gate_action, remarks)
                VALUES (%s, 'entry', 'denied', 'closed', 'Blocked vehicle detected')
            """, (vehicle_number,))
            db.commit()

        else:
            print(f"⚠ {vehicle_number} not found. Adding to waiting list...")
            arduino.write(b'CLOSE_GATE\n')

            try:
                cursor.execute("INSERT INTO waiting_vehicles (vehicle_number) VALUES (%s)", (vehicle_number,))
                db.commit()
            except mysql.connector.IntegrityError:
                print("ℹ Vehicle already in waiting list.")

            cursor.execute("""
                INSERT INTO gate_logs (vehicle_number, event_type, status, gate_action, remarks)
                VALUES (%s, 'entry', 'waiting', 'closed', 'Access denied - waiting for approval')
            """, (vehicle_number,))
            db.commit()

        # Show image briefly
        cv2.imshow("Captured Vehicle", img)
        cv2.waitKey(2000)
        cv2.destroyAllWindows()

    elif b'Vehicle Detected' in line:
        print("🚗 Vehicle detected... capturing image.")

    elif capturing:
        image_data += line
