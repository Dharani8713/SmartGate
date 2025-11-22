from PIL import Image
import numpy as np
import easyocr
from ultralytics import YOLO

# Load image (Pillow)
img = Image.open("test.jpg")

# Convert to NumPy array for YOLO/EasyOCR
img_np = np.array(img)

# OCR with EasyOCR
reader = easyocr.Reader(['en'])
text = reader.readtext(img_np, detail=0)
print("Detected Text:", text)

# YOLOv8 inference
model = YOLO("yolov8n.pt")
results = model.predict(img_np)
