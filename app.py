from ultralytics import YOLO
import streamlit as st
from PIL import Image
import numpy as np
import io
from datetime import datetime
import firebase_admin
from firebase_admin import credentials, storage

# ---------------- Firebase Initialization ----------------
if not firebase_admin._apps:
    cred = credentials.Certificate("serviceAccountKey.json")
    firebase_admin.initialize_app(cred, {
        "storageBucket": "smart-gate-52e2d.appspot.com"
    })
bucket = storage.bucket()

# ---------------- YOLO Initialization ----------------
# Let Ultralytics download the official yolov8n automatically
model = YOLO("yolov8n")  # <-- no .pt, no torch.load issues

# ---------------- Streamlit UI ----------------
st.title("Smart Gate License Plate Detection")

uploaded_file = st.file_uploader("Upload an image", type=["jpg","jpeg","png"])
if uploaded_file:
    image = Image.open(uploaded_file).convert("RGB")
    st.image(image, caption="Uploaded Image", use_column_width=True)
    
    img_array = np.array(image)
    
    # Run detection
    results = model(img_array)
    annotated_frame = results[0].plot()
    st.image(annotated_frame, caption="Detected Plates", use_column_width=True)
    
    # Save annotated image to Firebase
    buf = io.BytesIO()
    Image.fromarray(annotated_frame).save(buf, format="JPEG")
    buf.seek(0)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    blob = bucket.blob(f"detected/{timestamp}.jpg")
    blob.upload_from_file(buf, content_type="image/jpeg")
    st.success(f"Saved annotated image to Firebase Storage as detected/{timestamp}.jpg")
