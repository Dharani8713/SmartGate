import streamlit as st
from PIL import Image
import numpy as np
from ultralytics import YOLO
import pytesseract

# Load YOLO safely (automatic download)
model = YOLO("yolov8n")

st.title("Smart Gate License Plate Detection")

uploaded_file = st.file_uploader("Upload an image", type=["jpg", "jpeg", "png"])
if uploaded_file:
    image = Image.open(uploaded_file).convert("RGB")
    st.image(image, caption="Uploaded Image", use_column_width=True)
    img_array = np.array(image)

    # Run detection on CPU
    results = model(img_array, device="cpu")

    # Annotate and display
    annotated_frame = results[0].plot()
    st.image(annotated_frame, caption="Detected Plates", use_column_width=True)

    # OCR
    plate_texts = []
    for box in results[0].boxes.xyxy:
        x1, y1, x2, y2 = map(int, box)
        cropped = img_array[y1:y2, x1:x2]
        text = pytesseract.image_to_string(cropped, config='--psm 7').strip()
        if text:
            plate_texts.append(text)
    if plate_texts:
        st.success(f"Detected Plate Texts: {plate_texts}")
