import serial
import cv2
import pytesseract
import time

arduino = serial.Serial('COM3', 115200)
time.sleep(2)

image_data = b""
capturing = False

while True:
    line = arduino.readline()

    if b'STARTIMG' in line:
        print("Receiving image from Arduino...")
        capturing = True
        image_data = b""

    elif b'ENDIMG' in line:
        print("Image transfer complete. Saving file...")
        with open("vehicle.jpg", "wb") as f:
            f.write(image_data)
        capturing = False

        img = cv2.imread("vehicle.jpg")
        if img is None:
            print("No image captured")
            continue

        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        gray = cv2.bilateralFilter(gray, 11, 17, 17)
        edged = cv2.Canny(gray, 30, 200)

        text = pytesseract.image_to_string(gray)
        print("Detected Vehicle Number:", text.strip())

        cv2.imshow("Captured Vehicle", img)
        cv2.waitKey(3000)
        cv2.destroyAllWindows()

    elif b'Vehicle Detected' in line:
        print("Vehicle detected near gate... capturing image.")

    elif capturing:
        image_data += line
