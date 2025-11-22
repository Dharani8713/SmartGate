import streamlit as st
from PIL import Image
import io
import requests
import pytesseract
from datetime import datetime
import firebase_admin
from firebase_admin import credentials, firestore, storage
import json

# ---------------- Firebase Initialization ----------------
cred = credentials.Certificate("serviceAccountKey.json")
   
firebase_admin.initialize_app(cred, {
    'storageBucket': 'smart-gate-52e2d.firebasestorage.app'
})

db = firestore.client()
bucket = storage.bucket()

# ---------------- Streamlit UI ----------------
st.set_page_config(page_title="Smart Gate OCR", layout="wide")
st.title("Smart Gate: OCR & Notifications")

st.subheader("Upload car image from Raspberry Pi")
uploaded_file = st.file_uploader("Upload Image", type=["jpg", "jpeg", "png"])

# ---------------- OCR & Firestore ----------------
if uploaded_file:
    image = Image.open(uploaded_file)
    st.image(image, caption="Uploaded Image", use_column_width=True)

    # OCR using pytesseract
    plate_text = pytesseract.image_to_string(image, config='--psm 7').strip()
    st.success(f"Detected Plate: {plate_text}")

    # Save image to Firebase Storage
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    img_blob = bucket.blob(f"plates/{timestamp}.jpg")
    img_bytes = io.BytesIO()
    image.save(img_bytes, format="JPEG")
    img_blob.upload_from_string(img_bytes.getvalue(), content_type='image/jpeg')

    # Store plate info in Firestore
    doc_ref = db.collection("plates").document(str(timestamp))
    doc_ref.set({
        "plate": plate_text,
        "image_url": img_blob.public_url,
        "timestamp": datetime.now()
    })

    st.info(f"Plate info stored in Firestore! [Image URL]({img_blob.public_url})")

    # Optional: Send notification (Email/SMS)
    if st.checkbox("Send Notification"):
        user_contact = st.text_input("Enter email or phone number:")
        if user_contact:
            # Example: replace with Twilio or SMTP integration
            st.write(f"Notification sent to {user_contact} (placeholder)")







