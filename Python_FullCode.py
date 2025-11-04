from flask import Flask, request
import cv2
import pytesseract
import mysql.connector
import numpy as np
import base64
from datetime import datetime

app = Flask(__name__)

db = mysql.connector.connect(
    host="localhost",
    user="root",
    password="password",
    database="smart_gate_project"
)
cursor = db.cursor()

@app.route('/api/alerts', methods=['POST'])
def process_alert():
    data = request.get_json()
    image_b64 = data.get("image")
    distance = data.get("distance")

    # Decode and save image
    image_bytes = base64.b64decode(image_b64)
    np_arr = np.frombuffer(image_bytes, np.uint8)
    img = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)

    filename = f"captures/{datetime.now().strftime('%Y%m%d_%H%M%S')}.jpg"
    cv2.imwrite(filename, img)

    # OCR Processing
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    gray = cv2.bilateralFilter(gray, 11, 17, 17)
    text = pytesseract.image_to_string(gray)
    vehicle_number = ''.join(ch for ch in text if ch.isalnum()).upper()

    print(f"Detected Vehicle: {vehicle_number}")

    if not vehicle_number:
        return "UNAUTHORIZED"

    # Database Checks
    cursor.execute("SELECT * FROM allowed_vehicles WHERE vehicle_number=%s", (vehicle_number,))
    authorized = cursor.fetchone()

    cursor.execute("SELECT * FROM blocked_vehicles WHERE vehicle_number=%s", (vehicle_number,))
    blocked = cursor.fetchone()

    if authorized:
        cursor.execute("INSERT INTO gate_logs (vehicle_number, status, remarks) VALUES (%s, 'granted', 'Authorized vehicle')", (vehicle_number,))
        db.commit()
        return "AUTHORIZED"

    elif blocked:
        cursor.execute("INSERT INTO gate_logs (vehicle_number, status, remarks) VALUES (%s, 'denied', 'Blocked vehicle')", (vehicle_number,))
        db.commit()
        return "UNAUTHORIZED"

    else:
        cursor.execute("INSERT INTO waiting_vehicles (vehicle_number) VALUES (%s)", (vehicle_number,))
        db.commit()
        return "UNAUTHORIZED"

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
