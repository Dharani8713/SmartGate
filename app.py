import ultralytics.nn.tasks
import streamlit as st
from PIL import Image
import numpy as np
import cv2
from ultralytics import YOLO
import firebase_admin
from firebase_admin import credentials, storage
from datetime import datetime
import io
import os
import torch.nn.modules.container
import torch

# ---------------- Firebase Initialization ----------------
# Ensure you have uploaded serviceAccountKey.json to your repo
if not firebase_admin._apps:
    cred = credentials.Certificate("serviceAccountKey.json")
    firebase_admin.initialize_app(cred, {
        "storageBucket": "smart-gate-52e2d.appspot.com"  # replace with your bucket
    })
bucket = storage.bucket()

# ---------------- YOLO Initialization ----------------
# Allowlist globals for safe unpickling
torch.serialization.add_safe_globals([
    ultralytics.nn.tasks.DetectionModel,
    torch.nn.modules.container.Sequential,
    ultralytics.nn.modules.Conv
])

# 2️⃣ Load the YOLOv8 model safely (no device argument here)
model = YOLO("yolov8n.pt")  # no device argument here
#---------------- Streamlit UI ----------------
st.title("Smart Gate License Plate Detection")

uploaded_file = st.file_uploader("Upload an image", type=["jpg", "jpeg", "png"])
if uploaded_file:
    image = Image.open(uploaded_file).convert("RGB")
    st.image(image, caption="Uploaded Image", use_column_width=True)

    img_array = np.array(image)

    # YOLO detection
    results = model(img_array)
    annotated_frame = results[0].plot()  # image with bounding boxes
    st.image(annotated_frame, caption="Detected Plates", use_column_width=True)

    # Save annotated image to Firebase
    buf = io.BytesIO()
    annotated_pil = Image.fromarray(annotated_frame)
    annotated_pil.save(buf, format="JPEG")
    buf.seek(0)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    blob = bucket.blob(f"detected/{timestamp}.jpg")
    blob.upload_from_file(buf, content_type="image/jpeg")
    st.success(f"Saved annotated image to Firebase Storage as detected/{timestamp}.jpg")

    # Optional OCR
    try:
        import pytesseract
        plate_texts = []
        for box in results[0].boxes.xyxy:  # bounding boxes [x1, y1, x2, y2]
            x1, y1, x2, y2 = map(int, box)
            cropped = img_array[y1:y2, x1:x2]
            text = pytesseract.image_to_string(cropped, config='--psm 7').strip()
            if text:
                plate_texts.append(text)
        if plate_texts:
            st.success(f"Detected Plate Texts: {plate_texts}")
    except Exception:
        st.warning("OCR skipped: pytesseract or Tesseract not installed on this environment.")







