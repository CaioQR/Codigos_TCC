import cv2
import numpy as np
import time
import os

#https://stackoverflow.com/questions/62959030/how-do-i-access-my-usb-camera-using-opencv-with-python
#https://gist.github.com/Luxato/384a7c8a6bfdeba09d54cb5bd6b2c9fb#file-camera-py
#https://stackoverflow.com/questions/28566972/why-are-webcam-images-taken-with-python-so-dark/34687991

def tiraFoto(cam_idx):
    cap = cv2.VideoCapture(cam_idx)
    ret, frame = cap.read()
    time.sleep(1)
    (grabbed, frame) = cap.read()
    image_path = 'Raspberry/Capturas/Imagem'+str(cam_idx)+'.png'
    cv2.imwrite(image_path, frame)
    cap.release()

all_camera_idx_available = []

for camera_idx in range(10):
    cap = cv2.VideoCapture(camera_idx)
    if cap.isOpened():
        print(f'Camera index available: {camera_idx}')
        all_camera_idx_available.append(camera_idx)
        cap.release()

for cam_idx in all_camera_idx_available:
    tiraFoto(cam_idx)