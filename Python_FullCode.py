from flask import Flask, request
import cv2
import pytesseract
import mysql.connector
import numpy as np
import base64
from datetime import datetime

app = Flask(__name__)
# 1️⃣ CONNECT TO DATABASE
db = mysql.connector.connect(
    host="localhost",
    user="root",
    password="password",     # update if changed
    database="smart_gate_v2" # ✅ NEW database name
)
cursor = db.cursor()
# 2️⃣ MAIN API ENDPOINT

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

    
    # 3️⃣ DATABASE CHECKS 
    
    cursor.execute("SELECT * FROM vehicles2 WHERE vehicle_number=%s", (vehicle_number,))
    vehicle = cursor.fetchone()

    
    # 4️⃣ HANDLE VEHICLE STATUS
   
    if vehicle and vehicle[3] == 'allowed':  # status column = index 3
        cursor.execute("""
            INSERT INTO access_logs3 (vehicle_id, action, image_url, request_status)
            VALUES (%s, 'allowed', %s, 'approved')
        """, (vehicle[0], filename))
        db.commit()
        return "AUTHORIZED"

    elif vehicle and vehicle[3] == 'denied':
        cursor.execute("""
            INSERT INTO access_logs3 (vehicle_id, action, image_url, request_status)
            VALUES (%s, 'denied', %s, 'denied')
        """, (vehicle[0], filename))
        db.commit()
        return "UNAUTHORIZED"

    else:
        # Vehicle not found — add to temp_requests4 for admin approval
        cursor.execute("""
            INSERT INTO temp_requests4 (image_url, response_status)
            VALUES (%s, 'pending')
        """, (filename,))
        db.commit()
        return "UNAUTHORIZED"


# 5️⃣ START SERVER

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
