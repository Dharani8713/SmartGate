import streamlit as st
from PIL import Image
import numpy as np
import io
import firebase_admin
from firebase_admin import credentials, storage
from ultralytics import YOLO
import easyocr
from datetime import datetime

# ----------------------------
# Firebase Initialization
# ----------------------------
if not firebase_admin._apps:
    cred = credentials.Certificate("serviceAccountKey.json")
    firebase_admin.initialize_app(cred, {
        "storageBucket": "smart-gate-52e2d.firebasestorage.app"
    })
bucket = storage.bucket()

# ----------------------------
# Streamlit UI
# ----------------------------
st.title("Smart Gate OCR & Vehicle Detection")
uploaded_file = st.file_uploader("Upload an image", type=["jpg", "jpeg", "png"])

if uploaded_file is not None:
    img = Image.open(uploaded_file)
    st.image(img, caption="Uploaded Image", use_column_width=True)

    # Convert to numpy for YOLO/EasyOCR
    img_array = np.array(img)

    # ----------------------------
    # YOLO Detection
    # ----------------------------
    with st.spinner("Detecting objects..."):
        model = YOLO("yolov8n.pt")  # make sure this file is in repo or auto-download
        results = model(img_array)
        # Draw boxes on image
        annotated_frame = results[0].plot()
        st.image(annotated_frame, caption="YOLO Detection", use_column_width=True)

    # ----------------------------
    # OCR using EasyOCR
    # ----------------------------
    with st.spinner("Reading text from image..."):
        reader = easyocr.Reader(['en'])
        ocr_results = reader.readtext(img_array, detail=0)
        detected_text = " ".join(ocr_results)
        st.text_area("Detected Text", detected_text)

    # ----------------------------
    # Save to Firebase Storage
    # ----------------------------
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    blob = bucket.blob(f"uploads/{timestamp}.jpg")
    img_byte_arr = io.BytesIO()
    img.save(img_byte_arr, format="JPEG")
    blob.upload_from_string(img_byte_arr.getvalue(), content_type='image/jpeg')
    st.success(f"Uploaded image saved to Firebase Storage as uploads/{timestamp}.jpg")

