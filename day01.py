import sys
import cv2
import numpy as np


img = cv2.imread("./cat.jpg") 

if img is None:
    sys.exit("파일을 찾을 수 없습니다.")


B, G, R = cv2.split(img)


I = np.round(0.299 * R + 0.587 * G + 0.114 * B).astype(np.uint8)


cv2.imshow("Grayscale Image", I)
cv2.waitKey(0)
cv2.destroyAllWindows()
