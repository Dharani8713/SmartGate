import streamlit as st
from PIL import Image
import numpy as np
import io
from datetime import datetime

import torch
from ultralytics import YOLO
import ultralytics.nn.modules
import ultralytics.nn.tasks
import torch.nn.modules.container

import firebase_admin
from firebase_admin import credentials, storage

# ---------------- Firebase Initialization ----------------
if not firebase_admin._apps:
    cred = credentials.Certificate("serviceAccountKey.json")  # Your Firebase key
    firebase_admin.initialize_app(cred, {
        "storageBucket": "smart-gate-52e2d.appspot.com"  # Replace with your bucket
    })
bucket = storage.bucket()

# ---------------- YOLO Safe Loading ----------------
# Add required globals for safe unpickling
torch.serialization.add_safe_globals([
    ultralytics.nn.tasks.DetectionModel,
    torch.nn.modules.container.Sequential,
    ultralytics.nn.modules.Conv
])

# Load YOLOv8 model (do NOT pass device here)
model = YOLO("yolov8n.pt")  # replace with your model path

# ---------------- Streamlit UI ----------------
st.title("Smart Gate License Plate Detection")

uploaded_file = st.file_uploader("Upload an image", type=["jpg", "jpeg", "png"])
if uploaded_file:
    image = Image.open(uploaded_file).convert("RGB")
    st.image(image, caption="Uploaded Image", use_column_width=True)

    img_array = np.array(image)

    # Run YOLO detection on CPU explicitly
    try:
        results = model(img_array, device="cpu")
        annotated_frame = results[0].plot()  # image with bounding boxes
        st.image(annotated_frame, caption="Detected Plates", use_column_width=True)
    except Exception as e:
        st.error(f"YOLO detection failed: {e}")

    # Save annotated image to Firebase
    try:
        buf = io.BytesIO()
        annotated_pil = Image.fromarray(annotated_frame)
        annotated_pil.save(buf, format="JPEG")
        buf.seek(0)

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        blob = bucket.blob(f"detected/{timestamp}.jpg")
        blob.upload_from_file(buf, content_type="image/jpeg")
        st.success(f"Saved annotated image to Firebase Storage as detected/{timestamp}.jpg")
    except Exception as e:
        st.warning(f"Firebase upload failed: {e}")

    # Optional OCR
    try:
        import pytesseract
        plate_texts = []
        if results[0].boxes is not None and len(results[0].boxes) > 0:
            for box in results[0].boxes.xyxy:
                x1, y1, x2, y2 = map(int, box)
                cropped = img_array[y1:y2, x1:x2]
                text = pytesseract.image_to_string(cropped, config='--psm 7').strip()
                if text:
                    plate_texts.append(text)
        if plate_texts:
            st.success(f"Detected Plate Texts: {plate_texts}")
        else:
            st.info("No plate text detected.")
    except Exception:
        st.warning("OCR skipped: pytesseract or Tesseract not installed.")
