import serial
import cv2
import pytesseract
import time
import re
# CONNECT TO ARDUINO
arduino = serial.Serial('COM3', 115200)  # Change COM port as per your setup
time.sleep(2)

image_data = b""
capturing = False

print("\n🚪 Smart Gate Camera System Active — Waiting for Vehicle Detection...\n")

# MAIN LOOP
while True:
    line = arduino.readline()

    if b'STARTIMG' in line:
        print("📸 Receiving image from Arduino...")
        capturing = True
        image_data = b""

    elif b'ENDIMG' in line:
        print("✅ Image transfer complete — saving file...")
        with open("vehicle.jpg", "wb") as f:
            f.write(image_data)
        capturing = False

        
        # IMAGE PROCESSING (OCR)
        
        img = cv2.imread("vehicle.jpg")
        if img is None:
            print("⚠ No image captured. Skipping.")
            continue

        # Convert to grayscale and enhance
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        gray = cv2.bilateralFilter(gray, 11, 17, 17)
        edged = cv2.Canny(gray, 30, 200)

        # Use pytesseract to extract text
        text = pytesseract.image_to_string(gray)
        clean_text = re.sub(r'[^A-Z0-9]', '', text.upper())

        print(f"\n🔍 Extracted Text from Image: {clean_text}")

        # Try to find a valid vehicle number format (like KA01AB1234)
        match = re.search(r'[A-Z]{2}\d{2}[A-Z]{1,2}\d{3,4}', clean_text)
        if match:
            vehicle_number = match.group()
            print(f"🚗 Detected Vehicle Number: {vehicle_number}")
        else:
            print("❌ Could not detect a valid vehicle number.\n")

        # Show the captured image
        cv2.imshow("Captured Vehicle", img)
        cv2.waitKey(2000)
        cv2.destroyAllWindows()

    elif b'Vehicle Detected' in line:
        print("🚘 Vehicle detected — capturing image...")

    elif capturing:
        image_data += line
