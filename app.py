import os

# ----------------------------
# Environment settings for OpenCV headless mode
# ----------------------------
os.environ["OPENCV_VIDEOIO_PRIORITY_MSMF"] = "0"  # Disable Windows video backend (no-op on Linux)
os.environ["OPENCV_OPENGL_RUNTIME"] = "0"         # Disable OpenGL (avoids libGL errors)

# ----------------------------
# Imports
# ----------------------------
import cv2
import streamlit as st
from PIL import Image
import numpy as np
import pytesseract
import firebase_admin
from firebase_admin import credentials, storage
from ultralytics import YOLO
from datetime import datetime

# ----------------------------
# Firebase initialization
# ----------------------------
if not firebase_admin._apps:
    cred = credentials.Certificate("path/to/your-firebase-service-account.json")
    firebase_admin.initialize_app(cred, {
        "storageBucket": "your-bucket-name.appspot.com"
    })

# ----------------------------
# Streamlit WebApp
# ----------------------------
st.title("Smart Gate Access Control")

uploaded_file = st.file_uploader("Upload Vehicle Image", type=["jpg", "png", "jpeg"])
if uploaded_file:
    image = Image.open(uploaded_file)
    st.image(image, caption="Uploaded Image", use_column_width=True)

    # Convert to OpenCV format
    cv_image = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)

    # ----------------------------
    # YOLO Object Detection
    # ----------------------------
    model = YOLO("yolov8n.pt")  # replace with your trained model if needed
    results = model(cv_image)

    st.write("Detection Results:")
    st.write(results.pandas().xyxy[0])  # Bounding boxes and labels

    # ----------------------------
    # OCR License Plate
    # ----------------------------
    plate_text = pytesseract.image_to_string(cv_image)
    st.write("Detected Plate:", plate_text)

    # ----------------------------
    # Optional: Store image to Firebase
    # ----------------------------
    bucket = storage.bucket()
    blob = bucket.blob(f"vehicle_images/{datetime.now().strftime('%Y%m%d_%H%M%S')}.jpg")
    blob.upload_from_file(uploaded_file, content_type=uploaded_file.type)
    st.success("Image uploaded to Firebase successfully!")
