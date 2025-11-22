import streamlit as st
from PIL import Image
import numpy as np
import easyocr
from ultralytics import YOLO
import firebase_admin
from firebase_admin import credentials, storage
from datetime import datetime
import io

# ----------------------------
# Firebase Initialization
# ----------------------------
if not firebase_admin._apps:
    cred = credentials.Certificate("path/to/firebase_credentials.json")
    firebase_admin.initialize_app(cred, {
        "storageBucket": "your-bucket-name.appspot.com"
    })

bucket = storage.bucket()

# ----------------------------
# Load YOLO Model
# ----------------------------
model = YOLO("yolov8n.pt")  # or your trained weights

# ----------------------------
# Streamlit App
# ----------------------------
st.title("Smart Gate - License Plate Detection & OCR")

uploaded_file = st.file_uploader("Upload vehicle image", type=["jpg", "jpeg", "png"])
if uploaded_file:
    # Read image using Pillow
    image = Image.open(uploaded_file)
    st.image(image, caption="Uploaded Image", use_column_width=True)

    # Convert to NumPy array for YOLO
    image_array = np.array(image)

    # ----------------------------
    # Run YOLO Detection
    # ----------------------------
    results = model(image_array)

    # Draw detections and display
    annotated_img = results[0].plot()
    annotated_img_pil = Image.fromarray(annotated_img)
    st.image(annotated_img_pil, caption="Detected Objects")

    # ----------------------------
    # OCR using EasyOCR
    # ----------------------------
    reader = easyocr.Reader(['en'])
    ocr_results = reader.readtext(image_array)

    st.subheader("OCR Results")
    if ocr_results:
        for bbox, text, prob in ocr_results:
            st.write(f"Text: {text}, Confidence: {prob:.2f}")
    else:
        st.write("No text detected")

    # ----------------------------
    # Save Image with Timestamp to Firebase Storage
    # ----------------------------
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    image_bytes = io.BytesIO()
    image.save(image_bytes, format='PNG')
    blob = bucket.blob(f"uploads/{timestamp}.png")
    blob.upload_from_string(image_bytes.getvalue(), content_type='image/png')
    st.success(f"Image saved to Firebase Storage: uploads/{timestamp}.png")
