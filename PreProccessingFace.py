import cv2
import numpy as np
from deepface import DeepFace

def preprocess(img, size=(160, 160), padding=20):
    image = cv2.imread(img)

    faces = DeepFace.extract_faces(img_path=img, enforce_detection=True)
    facial_area = faces[0]["facial_area"]

    x, y, w, h = facial_area['x'], facial_area['y'], facial_area['w'], facial_area['h']
    height, width = image.shape[:2]

    x1 = max(0, x - padding)
    y1 = max(0, y - padding)
    x2 = min(width, x + w + padding)
    y2 = min(height, y + h + padding)

    face_img = image[y1:y2, x1:x2]
    gray = cv2.cvtColor(face_img, cv2.COLOR_BGR2GRAY)
    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))


    enhanced = clahe.apply(gray)
    blur = cv2.GaussianBlur(enhanced, (5, 5), 0)
    equalizer = cv2.equalizeHist(blur)
    enhanced_bgr = cv2.cvtColor(equalizer, cv2.COLOR_GRAY2BGR)

    bright = cv2.convertScaleAbs(enhanced_bgr, alpha=1.2, beta=10)
    result = cv2.resize(bright, size, interpolation=cv2.INTER_LINEAR)

    return result
