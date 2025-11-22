import streamlit as st
from PIL import Image
import pytesseract
import numpy as np
from ultralytics import YOLO
import firebase_admin
from firebase_admin import credentials, storage
import io
import base64
import datetime

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
# Streamlit UI
# ----------------------------
st.title("Smart Gate License Plate OCR")
uploaded_file = st.file_uploader("Upload an image", type=["jpg", "png", "jpeg"])

if uploaded_file:
    # Load image
    img = Image.open(uploaded_file).convert("RGB")
    st.image(img, caption="Uploaded Image", use_column_width=True)

    # Convert to numpy array for YOLO
    img_array = np.array(img)

    # ----------------------------
    # YOLOv8 Detection
    # ----------------------------
    st.info("Detecting license plate...")
    model = YOLO("yolov8n.pt")  # YOLOv8 Nano model
    results = model(img_array)

    # Crop detected plate and OCR
    if results and results[0].boxes.xyxy.shape[0] > 0:
        # Take first detection
        box = results[0].boxes.xyxy[0].cpu().numpy()
        x1, y1, x2, y2 = map(int, box)
        plate_img = img.crop((x1, y1, x2, y2))
        st.image(plate_img, caption="Detected Plate", use_column_width=True)

        # OCR using pytesseract
        st.info("Running OCR...")
        text = pytesseract.image_to_string(plate_img, config="--psm 7")
        st.text_area("Detected Text", text.strip())

        # ----------------------------
        # Save to Firebase Storage
        # ----------------------------
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        blob = bucket.blob(f"plates/{timestamp}.png")
        buffer = io.BytesIO()
        plate_img.save(buffer, format="PNG")
        blob.upload_from_string(buffer.getvalue(), content_type="image/png")
        st.success("Plate image uploaded to Firebase Storage!")

    else:
        st.warning("No license plate detected in the image.")
