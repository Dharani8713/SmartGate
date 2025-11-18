# lightweight plate extraction using EasyOCR as fallback
import easyocr
import cv2
import numpy as np

reader = easyocr.Reader(['en'])
image_path=r"D:\Studies\Project\smart_gate\server\uploads\1.jpeg"
def extract_plate_text(image_path):
    img = cv2.imread(image_path)
    if img is None:
        return ''
    # basic preprocessing
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    # run easyocr
    res = reader.readtext(gray)
    # choose best alphanumeric string
    best = ''
    for r in res:
        text = ''.join(ch for ch in r[1] if ch.isalnum())
        if len(text) >= 4 and len(text) > len(best):
            best = text
    return best
