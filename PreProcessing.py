import cv2
import numpy as np

def preprocess(img, size=(160, 160)):
    img = cv2.imread(img)

    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
    enhanced = clahe.apply(gray)    

    blur = cv2.GaussianBlur(gray, (5, 5), 0)
    equalizer = cv2.equalizeHist(blur)


    enhanced_bgr = cv2.cvtColor(equalizer, cv2.COLOR_GRAY2BGR)

    bright = cv2.convertScaleAbs(enhanced_bgr, alpha=1.2, beta=10)

    result = cv2.resize(bright, size, interpolation=cv2.INTER_LINEAR)

    return result