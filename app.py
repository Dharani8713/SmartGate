import urllib.parse
from pymongo import MongoClient

username = urllib.parse.quote_plus('smartgate')
password = urllib.parse.quote_plus('Project@87$')
import os

MONGO_URI = f"mongodb+srv://{username}:{password}@smartgate.kxptek5.mongodb.net/?appName=SmartGate"
db = MongoClient(MONGO_URI)
pending = db.pending
approved = db.approved
rejected = db.rejected
temp_access = db.temp_access
logs = db.logs
from flask import Flask, request, jsonify, render_template, send_from_directory
import os, json, uuid, datetime
from utils.plate_recognition import extract_plate_text
from utils.notify_admin import send_email, send_sms
import config
from bson.objectid import ObjectId

app = Flask(__name__, static_folder='static', template_folder='templates')
UPLOAD_DIR = os.path.join(os.getcwd(), 'uploads')
os.makedirs(UPLOAD_DIR, exist_ok=True)

# Admin UI
@app.route('/')
def index():
    # Fetch approved vehicles with plate info to show on dashboard
    vehicles = list(approved.find({}, {'_id': 0, 'plate': 1, 'owner_name': 1, 'access_type':1, 'registered_on': 1}))
    
    # Fetch recent logs
    recent_logs = list(logs.find().sort('timestamp', -1).limit(50))
    
    return render_template('admin_dashboard.html', vehicles=vehicles, logs=recent_logs)

@app.route('/api/register', methods=['POST'])
def register():
    data = request.get_json()
    plate = data.get('plate')
    owner = data.get('owner_name')
    access_type = data.get('access_type', 'permanent')

    if not plate or not owner:
        return jsonify({'error': 'Plate and owner name required'}), 400

    # Insert into approved collection (or pending if workflow requires)
    approved.insert_one({
        'plate': plate,
        'owner_name': owner,
        'access_type': access_type,
        'registered_on': datetime.datetime.utcnow()
    })

    return jsonify({'status': 'registered', 'plate': plate})


# Upload snapshot endpoint (ESP32 posts raw image body)
@app.route('/api/snapshot', methods=['POST'])
def snapshot():
    # Accept multipart or raw image
    file = None
    if 'file' in request.files:
        f = request.files['file']
        filename = f.filename or f"snap_{uuid.uuid4().hex}.jpg"
        path = os.path.join(UPLOAD_DIR, filename)
        f.save(path)
    else:
        # raw body
        data = request.data
        filename = f"snap_{uuid.uuid4().hex}.jpg"
        path = os.path.join(UPLOAD_DIR, filename)
        with open(path, 'wb') as fh:
            fh.write(data)

    # Run plate recognition
    plate = extract_plate_text(path)
    doc = {
        'imagePath': path,
        'plateCandidate': plate,
        'status': 'pending',
        'createdAt': datetime.datetime.utcnow()
    }
    rid = pending.insert_one(doc).inserted_id
    image_url = f"{config.BACKEND_PUBLIC_URL}/uploads/{os.path.basename(path)}"
    # notify admin (both email and sms depending on settings)
    try:
        send_email(plate, image_url, str(rid))
    except Exception as e:
        print('Email error', e)
    try:
        send_sms(plate, str(rid))
    except Exception as e:
        print('SMS error', e)

    return jsonify({'id': str(rid), 'status': 'pending', 'plate': plate})

# Serve uploaded images
@app.route('/uploads/<path:filename>')
def uploaded_file(filename):
    return send_from_directory(UPLOAD_DIR, filename)

# Admin approve/deny
@app.route('/api/approve/<rid>', methods=['POST'])
def approve(rid):
    # simple token auth
    token = request.headers.get('x-admin-token')
    if token != config.ADMIN_SECRET:
        return jsonify({'error':'unauthorized'}), 401
    doc = pending.find_one({'_id': ObjectId(rid)})
    if not doc: return jsonify({'error':'not_found'}), 404
    doc['approvedAt'] = datetime.datetime.utcnow()
    approved.insert_one(doc)
    pending.delete_one({'_id': ObjectId(rid)})
    return jsonify({'result':'ok'})

@app.route('/api/deny/<rid>', methods=['POST'])
def deny(rid):
    token = request.headers.get('x-admin-token')
    if token != config.ADMIN_SECRET:
        return jsonify({'error':'unauthorized'}), 401
    doc = pending.find_one({'_id': ObjectId(rid)})
    if not doc: return jsonify({'error':'not_found'}), 404
    doc['deniedAt'] = datetime.datetime.utcnow()
    rejected.insert_one(doc)
    pending.delete_one({'_id': ObjectId(rid)})
    return jsonify({'result':'ok'})

# Poll status for ESP32
@app.route('/status', methods=['GET', 'POST'])
def status():
    if request.method == 'POST':
        event = request.form.get('event')
        print("Received event:", event)
        # You can add logic here to update status, control servos, log events, etc.
        return jsonify({'result': 'status received'})

    # GET requests return overall app health status
    status_info={
        'status': 'OK',
        'database': 'connected',
        'message': 'Opening gate',
        'time': datetime.datetime.utcnow().isoformat()
    }
    return render_template('status.html', **status_info)

# Verify plate (ESP32 can call this with plate text)
@app.route('/api/verify_plate/<plate>', methods=['GET'])
def verify_plate(plate):
    if approved.find_one({'plate': plate}):
        logs.insert_one({'plate':plate, 'timestamp': datetime.datetime.utcnow(), 'status':'permanent'})
        return jsonify({'access':True, 'type':'permanent'})
    if temp_access.find_one({'plate': plate}):
        temp_access.delete_one({'plate': plate})
        logs.insert_one({'plate':plate, 'timestamp': datetime.datetime.utcnow(), 'status':'one_time'})
        return jsonify({'access':True, 'type':'one_time'})
    logs.insert_one({'plate':plate, 'timestamp': datetime.datetime.utcnow(), 'status':'unknown'})
    return jsonify({'access':False, 'type':'unknown'})

# Stream page (server proxies or displays central camera)
@app.route('/stream_page')
def stream_page():
    return render_template('stream.html')

# Static admin pages (templates exist in templates/)
# Run server
if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
