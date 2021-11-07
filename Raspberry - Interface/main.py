import time
import RPi.GPIO as GPIO
import cv2
import glob
import os
import kivy
import json
from kivy.app import App
from kivy.uix.button import Button
from kivy.uix.togglebutton import ToggleButton
from kivy.uix.gridlayout import GridLayout
from kivy.uix.image import Image
from kivy.uix.slider import Slider
from kivy.clock import Clock
from kivy.graphics import Color, Rectangle


posicao1_pin = 37
posicao2_pin = 35
porta_pin = 33
led_superior_pin = 29
led_inferior_pin = 31
mot_step = 7
mot_dir = 3 
mot_channels = (15, 13, 11)
mot_disable = 19

GPIO.setmode(GPIO.BOARD)
GPIO.setwarnings(False)
GPIO.setup(posicao1_pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(posicao2_pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(porta_pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(led_inferior_pin,GPIO.OUT)
GPIO.setup(led_superior_pin, GPIO.OUT)
GPIO.setup(mot_dir, GPIO.OUT)
GPIO.setup(mot_step, GPIO.OUT)
GPIO.setup(mot_channels, GPIO.OUT)
GPIO.setup(mot_disable, GPIO. OUT)

def led_superior(status):
    if status == 'On':
        GPIO.output(led_superior_pin, True)
    else:
        GPIO.output(led_superior_pin, False)

def led_inferior(status):
    if status == 'On':
        GPIO.output(led_inferior_pin, True)
    else:
        GPIO.output(led_inferior_pin, False)

def move_motor (posicao):
    if posicao == 1:
        pin = posicao1_pin
        GPIO.output (mot_dir, True)
    else:
        pin = posicao2_pin
        GPIO.output(mot_dir, False)
    GPIO.output(mot_disable, False)
    n_steps = 24000
    step = 0 
    while (step < n_steps) and (GPIO.input(pin) == 1):
        GPIO.output(mot_step, True)
        time.sleep(500/1000000)
        GPIO.output(mot_step, False)
        time.sleep(500/1000000)
        step += 1
    GPIO.output(mot_disable, True)
    
def list_cameras():
    cameras = []
    for camera in glob.glob("/dev/video?"):
        try:
            cam = cv2.VideoCapture(camera)
            if (cam is None) or (not cam.isOpened()):
                pass
            else:
                cameras.append(camera)
        except:
            pass
    if len(cameras) == 3:
        return cameras
    else:
        print ("Error")
        return 0

def address_cameras(camera_list):
    cameras = []
    for camera in camera_list:
        output = os.popen("udevadm info --query=path --name="+camera).read()
        usb_index = int(output.split(':')[0][-1])-1
        cameras.append([usb_index, camera])
    cameras.sort()
    return cameras

def setup_cameras():
    camera_list = list_cameras()
    cameras = address_cameras(camera_list)
    return cameras

def get_images(cameras, position):
    images = []
    for usb_index, camera in cameras:
        if position == 1:
            filename = chr(usb_index+64)
        else:
            filename = chr(usb_index+68)
        cam = cv2.VideoCapture(camera)
        cam.set(cv2.CAP_PROP_FRAME_WIDTH, 10000) #set resolution to max
        cam.set(cv2.CAP_PROP_FRAME_HEIGHT, 10000)  #set resolution to max
        for i in range(25):
            r, frame = cam.read()
        cam.release
        images.append([filename, frame])
    return images

def save_images(images, path, extension):
    for filename, image in images:
        cv2.imwrite(path+filename+extension, image)

def aquisition_routine(obj):
    #data = read_json('/home/pi/Documents/bayer_project/comunication/', 'to_pi.json')
    #write_json('/home/pi/Documents/bayer_project/comunication/', 'to_pc.json', data[ensaio_id], 'running') 
    led_superior('On')
    led_inferior('On')
    cameras = setup_cameras()
    move_motor(1)
    time.sleep(1)
    images = get_images(cameras, 1)
    move_motor(2)
    time.sleep(1)
    images += get_images(cameras, 2)
    save_images(images, '/home/pi/Documents/bayer_project/images/', '.jpg')
    led_superior('Off')
    led_inferior('Off')
    #write_json('/home/pi/Documents/bayer_project/comunication/', 'to_pc.json', data[ensaio_id], 'success')
    #screen_manager()
    
def read_json(path, filename):
    file = open(path+filename, "r")
    data = json.load(file)
    file.close()
    return data

def write_json(path, filename, ensaio_id, status):
    data = {'status':status, 'ensaio_id':ensaio_id} #status -> running, sleeping, error, success
    file = open(path+filename, "w")
    json.dump(data, file)
    file.close()
    
def screen_manager(status):
    #data = read_json('/home/pi/Documents/bayer_project/comunication/', 'to_pi.json')
    #if data.status == 'running':
        #tela de ensaio
    #else
        #write_json('/home/pi/Documents/bayer_project/comunication/', 'to_pc.json', data.ensaio_id, 'sleeping')
        #tela de descanso
    pass

led_inferior("off")

class tela(App):
    
    def build(self):
        # Set up the layout:
        layout = GridLayout(cols=5, spacing=30, padding=30, row_default_height=150)

        # Make the background gray:
        with layout.canvas.before:
            Color(.2,.2,.2,1)
            self.rect = Rectangle(size=(800,600), pos=layout.pos)

        start_button = ToggleButton(text="Começar")
        start_button.bind(on_press=aquisition_routine)

        # Add the UI elements to the layout:
        layout.add_widget(start_button)

        return layout
    

