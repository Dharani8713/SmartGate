import streamlit as st
from PIL import Image
import pytesseract
import numpy as np
from ultralytics import YOLO
import firebase_admin
from firebase_admin import credentials, storage
import io
from datetime import datetime
import os

# ----------------------------
# Firebase Initialization
# ----------------------------
if not firebase_admin._apps:
    cred = credentials.Certificate("serviceAccountKey.json")
    firebase_admin.initialize_app(cred, {
        "storageBucket": "your-bucket-name.appspot.com"
    })
bucket = storage.bucket()

# ----------------------------
# Streamlit App Layout
# ----------------------------
st.title("Smart Gate License Plate OCR")
st.write("Upload an image or take a snapshot to detect the license plate.")

uploaded_file = st.file_uploader("Choose an image...", type=["jpg", "png"])

if uploaded_file is not None:
    # Load image
    img = Image.open(uploaded_file)
    st.image(img, caption="Uploaded Image", use_column_width=True)

    # Convert to numpy for YOLO
    np_img = np.array(img)

    # ----------------------------
    # YOLO Detection
    # ----------------------------
    model = YOLO("yolov8n.pt")  # lightweight YOLOv8 model
    results = model(np_img)

    # Draw bounding boxes on PIL image
    result_img = img.copy()
    for box in results[0].boxes.xyxy:
        x1, y1, x2, y2 = map(int, box)
        result_img = result_img.copy()
        # Draw rectangle using PIL
        from PIL import ImageDraw
        draw = ImageDraw.Draw(result_img)
        draw.rectangle([x1, y1, x2, y2], outline="red", width=3)

    st.image(result_img, caption="Detected Plates", use_column_width=True)

    # ----------------------------
    # OCR with pytesseract
    # ----------------------------
    text = pytesseract.image_to_string(result_img)
    st.text_area("Detected Text", text)

    # ----------------------------
    # Upload to Firebase Storage
    # ----------------------------
    buffer = io.BytesIO()
    result_img.save(buffer, format="PNG")
    buffer.seek(0)

    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    blob = bucket.blob(f"captures/{timestamp}.png")
    blob.upload_from_file(buffer, content_type="image/png")
    st.success(f"Image uploaded to Firebase as {timestamp}.png")
