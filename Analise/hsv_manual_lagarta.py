# HSV slider para detectar a lagarta

import cv2
import numpy as np

'''
para vídeo:
substituir cap = cv2.VideoCapture(0)
e frame no lugar de cap

L-H = 0
L-S = 31
L-V = 163
U-H = 179
U-S = 255
U-V = 255
'''

def nothing(x):
    pass

cap = cv2.imread("H:\Caio Quaglierini\Documents\TCC\Codigos_TCC\Analise\Fotos\lagarta_1_300.jpg")
cv2.namedWindow("Trackbars")

cv2.createTrackbar("L - H", "Trackbars", 0, 179, nothing)
cv2.createTrackbar("L - S", "Trackbars", 0, 255, nothing)
cv2.createTrackbar("L - V", "Trackbars", 0, 255, nothing)
cv2.createTrackbar("U - H", "Trackbars", 179, 179, nothing)
cv2.createTrackbar("U - S", "Trackbars", 255, 255, nothing)
cv2.createTrackbar("U - V", "Trackbars", 255, 255, nothing)

while True:
    #_, frame = cap.read()
    hsv = cv2.cvtColor(cap, cv2.COLOR_BGR2HSV)
    
    l_h = cv2.getTrackbarPos("L - H", "Trackbars")
    l_s = cv2.getTrackbarPos("L - S", "Trackbars")
    l_v = cv2.getTrackbarPos("L - V", "Trackbars")
    u_h = cv2.getTrackbarPos("U - H", "Trackbars")
    u_s = cv2.getTrackbarPos("U - S", "Trackbars")
    u_v = cv2.getTrackbarPos("U - V", "Trackbars")
    
    lower_blue = np.array([l_h, l_s, l_v])
    upper_blue = np.array([u_h, u_s, u_v])
    mask = cv2.inRange(hsv, lower_blue, upper_blue)
    
    result = cv2.bitwise_and(cap, cap, mask=mask)
    
    cv2.imshow("frame", cap)
    cv2.imshow("mask", mask)
    cv2.imshow("result", result)
    
    key = cv2.waitKey(1)
    
    if key == 27:
        break

cap.release()
cv2.destroyAllWindows()