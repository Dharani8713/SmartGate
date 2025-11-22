# streamlit_app.py
import streamlit as st
from PIL import Image
import requests
import pytesseract
import firebase_admin
from firebase_admin import credentials, firestore
import smtplib
from email.message import EmailMessage

# Firebase init
cred = credentials.Certificate("firebase_key.json")
firebase_admin.initialize_app(cred)
db = firestore.client()

st.title("Smart Gate System")

uploaded_file = st.file_uploader("Upload image from Pi", type=["jpg", "png"])

if uploaded_file:
    image = Image.open(uploaded_file)
    st.image(image, caption="Captured Image", use_column_width=True)
    
    # OCR
    plate_text = pytesseract.image_to_string(image)
    st.text(f"Detected Plate: {plate_text}")

    # Store image locally & in Firestore with timestamp
    import time
    timestamp = int(time.time())
    img_name = f"plate_{timestamp}.jpg"
    image.save(img_name)

    db.collection("pending_plates").document(str(timestamp)).set({
        "plate": plate_text.strip(),
        "image": img_name,
        "timestamp": timestamp,
        "status": "pending"
    })

    st.success("Plate logged in Firestore!")

    # Send notification via Email (example)
    notify = st.checkbox("Notify user?")
    if notify:
        msg = EmailMessage()
        msg.set_content(f"New vehicle detected: {plate_text}. Approve at your Streamlit dashboard.")
        msg["Subject"] = "Smart Gate Alert"
        msg["From"] = "youremail@gmail.com"
        msg["To"] = "user@example.com"

        # Send email via Gmail SMTP
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.login("youremail@gmail.com", "app_password")
            server.send_message(msg)

    # Approve/Deny Buttons
    if st.button("Approve"):
        db.collection("pending_plates").document(str(timestamp)).update({"status": "approved"})
        requests.post("http://<esp32_ip>/action", json={"action": "open"})
    if st.button("Deny"):
        db.collection("pending_plates").document(str(timestamp)).update({"status": "denied"})
        requests.post("http://<esp32_ip>/action", json={"action": "close"})
