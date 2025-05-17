import cv2
import numpy as np

def preprocess(img, size=(160, 160)):
    img = cv2.imread(img)

    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    blur = cv2.GaussianBlur(gray, (5, 5), 0)
    equalizer = cv2.equalizeHist(blur)

    bgr = cv2.cvtColor(equalizer, cv2.COLOR_GRAY2BGR)
    result = cv2.resize(bgr, size)

    return result