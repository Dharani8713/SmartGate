import streamlit as st
from PIL import Image
import pytesseract
import io
import firebase_admin
from firebase_admin import credentials, storage
from datetime import datetime
import numpy as np

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
# Streamlit App
# ----------------------------
st.title("Smart Gate License Plate OCR")
st.write("Upload an image to detect license plates.")

uploaded_file = st.file_uploader("Choose an image...", type=["jpg", "png"])

if uploaded_file is not None:
    # Load image
    img = Image.open(uploaded_file)
    st.image(img, caption="Uploaded Image", use_column_width=True)

    # ----------------------------
    # OCR using pytesseract
    # ----------------------------
    text = pytesseract.image_to_string(img)
    st.text_area("Detected Text", text)

    # ----------------------------
    # Upload to Firebase Storage
    # ----------------------------
    buffer = io.BytesIO()
    img.save(buffer, format="PNG")
    buffer.seek(0)

    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    blob = bucket.blob(f"captures/{timestamp}.png")
    blob.upload_from_file(buffer, content_type="image/png")
    st.success(f"Image uploaded to Firebase as {timestamp}.png")
