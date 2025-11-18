from pymongo import MongoClient
from datetime import datetime
import urllib.parse

# Encode username and password to handle special characters safely
username = urllib.parse.quote_plus("smartgate")
password = urllib.parse.quote_plus("Project@87$")  # Your password with $ or special chars

MONGODB_URI = f"mongodb+srv://{username}:{password}@smartgate.kxptek5.mongodb.net/?appName=SmartGate"

# Connect to MongoDB Atlas
client = MongoClient(MONGODB_URI)
db = client.smart_gate  # Database named 'smart_gate'

# Collections corresponding to SQLite tables
approved = db.approved
logs = db.logs
pending = db.pending
rejected = db.rejected
temp_access = db.temp_access


# ------------------ ADMIN FUNCTIONS ------------------

def add_admin(username, password):
    try:
        admins_col.insert_one({"username": username, "password": password})
    except Exception as e:
        print(f"Admin already exists or error: {e}")

def verify_admin(username, password):
    return admins_col.find_one({"username": username, "password": password}) is not None


# ------------------ VEHICLE FUNCTIONS ------------------

def register_vehicle(vehicle_number, owner_name, access_type="permanent"):
    try:
        vehicles_col.insert_one({
            "vehicle_number": vehicle_number,
            "owner_name": owner_name,
            "access_type": access_type,
            "registered_on": datetime.utcnow()
        })
    except Exception as e:
        print(f"Vehicle {vehicle_number} already registered or error: {e}")

def get_all_vehicles():
    return list(vehicles_col.find())


# ------------------ TEMPORARY ACCESS FUNCTIONS ------------------

def approve_temp_access(vehicle_number, approved_by, valid_until):
    try:
        temp_access.insert_one({
            "vehicle_number": vehicle_number,
            "approved_by": approved_by,
            "valid_until": valid_until
        })
    except Exception as e:
        print(f"Temporary access already exists or error: {e}")

def check_temp_access(vehicle_number):
    doc = temp_access.find_one({"vehicle_number": vehicle_number})
    if not doc:
        return False
    return doc.get("valid_until") > datetime.utcnow()

def revoke_temp_access(vehicle_number):
    temp_access.delete_one({"vehicle_number": vehicle_number})


# ------------------ ACCESS LOGGING ------------------

def log_access(vehicle_number, status, access_type):
    access_logs_col.insert_one({
        "vehicle_number": vehicle_number,
        "access_time": datetime.utcnow(),
        "status": status,
        "access_type": access_type
    })

def get_access_logs(limit=50):
    return list(access_logs_col.find().sort("access_time", -1).limit(limit))


# ------------------ UTILITY ------------------

def vehicle_exists(vehicle_number):
    return vehicles_col.find_one({"vehicle_number": vehicle_number}) is not None

def verify_access(vehicle_number):
    if vehicle_exists(vehicle_number):
        return "permanent"
    elif check_temp_access(vehicle_number):
        return "temporary"
    else:
        return None


if __name__ == "__main__":
    print("MongoDB Atlas database connection module loaded.")