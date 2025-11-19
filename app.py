from flask import Flask, request, jsonify
from flask_cors import CORS
from utils.plate_recognition import extract_plate_text
from utils.notify_admin import send_email, send_sms

app = Flask(__name__)
CORS(app)

@app.route('/api/recognize_plate', methods=['POST'])
def recognize_plate():
    data = request.json
    image_data = data.get("image")
    
    # Run your OCR plate recognition logic
    plate_text = extract_plate_text(image_data)
    
    # Optionally send alerts
    send_email("admin@example.com", f"Plate recognized: {plate_text}")
    send_sms("+1234567890", f"Plate recognized: {plate_text}")
    
    return jsonify({"plate_text": plate_text})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
