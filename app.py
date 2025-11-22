import streamlit as st
from PIL import Image
import numpy as np
import io
from datetime import datetime

import torch
from ultralytics import YOLO
import ultralytics.nn.tasks

import firebase_admin
from firebase_admin import credentials, storage

# ---------------- Firebase Initialization ----------------
if not firebase_admin._apps:
    cred = credentials.Certificate("serviceAccountKey.json")  # path to your Firebase key
    firebase_admin.initialize_app(cred, {
        "storageBucket": "smart-gate-52e2d.appspot.com"
    })
bucket = storage.bucket()

# ---------------- YOLO Initialization ----------------
# Safe unpickling for PyTorch 2.6+
with torch.serialization.safe_globals([ultralytics.nn.tasks.DetectionModel]):
    model = YOLO("yolov8n.pt")  # Replace with your local or downloaded YOLOv8 checkpoint

# ---------------- Streamlit UI ----------------
st.title("Smart Gate License Plate Detection")

uploaded_file = st.file_uploader("Upload an image", type=["jpg", "jpeg", "png"])
if uploaded_file:
    image = Image.open(uploaded_file).convert("RGB")
    st.image(image, caption="Uploaded Image", use_column_width=True)

    img_array = np.array(image)

    # ---------------- YOLO Detection ----------------
    results = model(img_array)
    annotated_frame = results[0].plot()
    st.image(annotated_frame, caption="Detected Plates", use_column_width=True)

    # ---------------- Save Annotated Image to Firebase ----------------
    buf = io.BytesIO()
    Image.fromarray(annotated_frame).save(buf, format="JPEG")
    buf.seek(0)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    blob = bucket.blob(f"detected/{timestamp}.jpg")
    blob.upload_from_file(buf, content_type="image/jpeg")
    st.success(f"Saved annotated image to Firebase Storage as detected/{timestamp}.jpg")

    # ---------------- OCR ----------------
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
        else:
            st.info("No plate text detected.")
    except Exception as e:
        st.warning(f"OCR skipped or failed: {e}")
