# Must be at the very top, before importing cv2 or ultralytics
import os
os.environ["OPENCV_VIDEOIO_PRIORITY_MSMF"] = "0"  # disable Windows video backend
os.environ["OPENCV_OPENGL_RUNTIME"] = "0"         # disable OpenGL loading

# Now safe to import OpenCV and ultralytics
import cv2
import streamlit as st
from PIL import Image
import numpy as np
import io
from datetime import datetime
import firebase_admin
from firebase_admin import credentials, storage
from ultralytics import YOLO
import pytesseract


# ---------------- Firebase Initialization ----------------
if not firebase_admin._apps:
    cred = credentials.Certificate("serviceAccountKey.json")  # your Firebase key
    firebase_admin.initialize_app(cred, {
        "storageBucket": "smart-gate-52e2d.appspot.com"  # replace with your bucket
    })
bucket = storage.bucket()

# ---------------- YOLO Initialization ----------------
# Let Ultralytics automatically download yolov8n if needed
model = YOLO("yolov8n")  # no .pt, avoids PyTorch 2.6+ unpickling issues

# ---------------- Streamlit UI ----------------
st.set_page_config(page_title="Smart Gate OCR", layout="wide")
st.title("Smart Gate License Plate Detection")

uploaded_file = st.file_uploader("Upload an image", type=["jpg", "jpeg", "png"])
if uploaded_file:
    image = Image.open(uploaded_file).convert("RGB")
    st.image(image, caption="Uploaded Image", use_column_width=True)

    img_array = np.array(image)

    # YOLO detection
    results = model(img_array, device="cpu")  # force CPU for simplicity
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
    plate_texts = []
    for box in results[0].boxes.xyxy:
        x1, y1, x2, y2 = map(int, box)
        cropped = img_array[y1:y2, x1:x2]
        text = pytesseract.image_to_string(cropped, config='--psm 7').strip()
        if text:
            plate_texts.append(text)

    if plate_texts:
        st.success(f"Detected Plate Texts: {plate_texts}")
    else:
        st.warning("No plate text detected.")


