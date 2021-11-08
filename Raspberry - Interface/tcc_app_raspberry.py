import kivy
from kivy.app import App
from kivy.uix.label import Label
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.button import Button
from kivy.uix.widget import Widget
from kivy.properties import ObjectProperty
from kivy.lang import Builder
from kivy.uix.image import Image
from kivy.core.window import Window
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.spinner import Spinner
from datetime import datetime
from kivy.clock import Clock
from kivy.uix.popup import Popup
import socket
import os
import json
import time
import RPi.GPIO as GPIO
import cv2
import glob

# Definir telas
class WindowManager(ScreenManager):
    pass

class HomeWindow(Screen):
    def __init__(self, **kwargs):
        super(HomeWindow, self).__init__(**kwargs)
        #Cria um relógio que chamará a função 'VerificaJson' a cada 10 segundos
        Clock.schedule_interval(self.VerificaJson, 3)

    screen = "Home"

    #Função para atualizar a data    
    def VerificaJson(self, dt):
        #Exibe o IP na tela
        self.ids.labelIP.text = "IP: " + str(socket.gethostbyname(socket.gethostname()))       
        #Carrega O arquivo Json
        path = os.getcwd()+'/Comunication/to_pi.json'
        with open(path, 'r', encoding="utf-8") as config_file:
            data=config_file.read()
            JsonToPi = json.loads(data) 
            config_file.close()    
        #Verifica o status
        tela = JsonToPi['status']
        #Aletera a tela
        if (tela == 'running' and self.screen != "Ensaio"):
            self.parent.current = 'Ensaio'
            self.screen = "Ensaio"
        elif (tela != 'running' and self.screen == "Ensaio"):
            self.screen = "Home"

    #Função para abrir aplicativo de configurações de rede    
    def Abrir_Configuracoes(self):
        print("abri settings")
        pass



class EnsaioWindow(Screen):
    def __init__(self, **kwargs):
        super(EnsaioWindow, self).__init__(**kwargs)
        self.Init()
        #Cria um relógio que chamará a função 'Atualiza' a cada 10 segundos
        Clock.schedule_interval(self.Atualiza, 5)


    #Define a variável auxiliar
    running_ensaio = False

    #Função de inicialização 
    def Init(self):
        #Define as GPIOs 
        self.posicao1_pin = 37
        self.posicao2_pin = 35
        self.porta_pin = 33
        self.led_superior_pin = 29
        self.led_inferior_pin = 31
        self.mot_step = 7
        self.mot_dir = 3 
        self.mot_channels = (15, 13, 11)
        self.mot_disable = 19
        #Setup das GPIOs 
        GPIO.setmode(GPIO.BOARD)
        GPIO.setwarnings(False)
        GPIO.setup(self.posicao1_pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)
        GPIO.setup(self.posicao2_pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)
        GPIO.setup(self.porta_pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)
        GPIO.setup(self.led_inferior_pin,GPIO.OUT)
        GPIO.setup(self.led_superior_pin, GPIO.OUT)
        GPIO.setup(self.mot_dir, GPIO.OUT)
        GPIO.setup(self.mot_step, GPIO.OUT)
        GPIO.setup(self.mot_channels, GPIO.OUT)
        GPIO.setup(self.mot_disable, GPIO. OUT)

    #Função para atualizar as informações    
    def Atualiza(self, dt):
        #Carrega O arquivo Json
        path = os.getcwd()+'/Comunication/to_pi.json'
        with open(path, 'r', encoding="utf-8") as config_file:
            data=config_file.read()
            JsonToPi = json.loads(data) 
            config_file.close()    
        #Verifica o status
        tela = JsonToPi['status']
        #Atualiza a tela
        self.ids.Ensaio_ID.text = JsonToPi['ensaio_id']
        self.ids.Tecnico.text = JsonToPi['tecnico']
        self.ids.Etapa.text = JsonToPi['etapa']
        #Aletera o widget
        if (tela == 'sleeping' and self.running_ensaio == True):
            try:
                #Exibe widget botão finalizar
                self.add_widget(self.ids.FinalizaEnsaio)
                self.running_ensaio = False
            except:
                pass
    
    #Função para controle do led superior
    def led_superior(self, status):
        if status == 'On':
            GPIO.output(self.led_superior_pin, True)
        else:
            GPIO.output(self.led_superior_pin, False)
        self.Update_Logs("Status leds inferiores: "+str(status))

    #Função para controle do led inferior
    def led_inferior(self, status):
        if status == 'On':
            GPIO.output(self.led_inferior_pin, True)
        else:
            GPIO.output(self.led_inferior_pin, False)
        self.Update_Logs("Status leds inferiores: "+str(status))

    #Função para controle do motor
    def move_motor (self, posicao):
        if posicao == 1:
            pin = self.posicao1_pin
            GPIO.output (self.mot_dir, False)
        else:
            pin = self.posicao2_pin
            GPIO.output(self.mot_dir, True)
        GPIO.output(self.mot_disable, False)
        n_steps = 24000
        step = 0 
        while (step < n_steps) and (GPIO.input(pin) == 1):
            GPIO.output(self.mot_step, True)
            time.sleep(500/1000000)
            GPIO.output(self.mot_step, False)
            time.sleep(500/1000000)
            step += 1
        GPIO.output(self.mot_disable, True)
        self.Update_Logs("Posição das câmeras: "+str(posicao))

    #Função para listar câmeras disponíveis
    def list_cameras(self):
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
        if len(cameras) == 1:
            self.Update_Logs("Câmeras disponíveis: "+str(len(cameras)))
            return cameras
        else:
            self.Update_Logs("Erro ao localizar as câmeras")
            self.exito = False
            return 0

    #Função para configurar os endereço USB das câmeras disponíveis
    def address_cameras(self, camera_list):
        cameras = []
        for camera in camera_list:
            output = os.popen("udevadm info --query=path --name="+camera).read()
            usb_index = int(output.split(':')[0][-1])-1
            cameras.append([usb_index, camera])
        cameras.sort()
        self.Update_Logs("Câmeras ordenadas")
        return cameras

    #Função para configurar as câmeras disponíveis
    def setup_cameras(self):
        camera_list = self.list_cameras()
        cameras = self.address_cameras(camera_list)
        self.Update_Logs("Setup das câmeras finalizado")
        return cameras

    #Função para coletar as imagens
    def get_images(self, cameras, position):
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
        self.Update_Logs("Captura de imagens "+str(position)+" finalizada")
        return images

    #Função para salvar as imagens
    def save_images(self, images, path, extension):
        for filename, image in images:
            cv2.imwrite(path+filename+extension, image)
        self.Update_Logs("Imagens salvas")

    #Função para ler json
    def read_json(self, path, filename):
        file = open(path+filename, "r")
        data = json.load(file)
        file.close()
        return data

    #Função para escrever json
    def write_json(self, path, filename, ensaio_id, status):
        data = {'status':status, 'ensaio_id':ensaio_id} #status -> running, sleeping, error, success
        file = open(path+filename, "w")
        json.dump(data, file)
        file.close()
    
    #Função para atualizar logs
    def Update_Logs(self, NewLog):
        self.Lista_Logs.append(NewLog)
    
    #Função para exibir logs
    def Show_Logs(self):
        text = '\n'
        for log in self.Lista_Logs:
            text += log
            text += '\n'
        self.ids.Logs.text = text

    #Função para realizar o ensaio
    def RealizaEnsaio(self):
        #Limpa os logs
        self.Lista_Logs = []
        #Verificar se a porta está aberta:
        if (GPIO.input(self.porta_pin) == 1):
            #PopUp avisando que a porta está aberta
            box = BoxLayout(orientation='vertical',padding=10,spacing=10)
            popup = Popup(title='Atenção!', content=box, auto_dismiss=False, size_hint=(0.4,0.3))
            texto = Label(text='A porta está aberta')
            botao = Button(text='ok',on_release=popup.dismiss)
            box.add_widget(texto)
            box.add_widget(botao)
            popup.open()
        else:
            #Inicia o ensaio
            self.Update_Logs("Ensaio iniciado")
            self.running_ensaio = True
            self.exito = True
            #Remove widget botão iniciar
            self.remove_widget(self.ids.IniciaEnsaio)
            #Exibe widget botão finalizar
            self.remove_widget(self.ids.FinalizaEnsaio)
            #Atualiza o json "to_pc"
            data = self.read_json('/home/pi/Documents/bayer_project/Comunication/', 'to_pi.json')
            self.write_json('/home/pi/Documents/bayer_project/Comunication/', 'to_pc.json', data['ensaio_id'], 'running')
            #Acende leds inferiores
            self.led_inferior('On')
            #Acende leds superiores
            self.led_superior('On')
            #Setup das câmeras
            cameras = self.setup_cameras()
            #Retorna a barra para P1
            self.move_motor(1)
            time.sleep(1) 
            #Captura as 4 primeiras fotos
            images = self.get_images(cameras, 1)
            #Avança a barra para P2
            self.move_motor(2)
            time.sleep(1)
            #Captura as 4 últimas fotos
            images += self.get_images(cameras, 2)
            #Salva as imagens
            self.save_images(images, '/home/pi/Documents/bayer_project/Images/', '.jpg')
            #Apaga leds inferiores
            self.led_inferior('Off')
            #Apaga leds superiores
            self.led_superior('Off')
            #Atualiza o json "to_pc"
            if (self.exito == True):
                self.write_json('/home/pi/Documents/bayer_project/Comunication/', 'to_pc.json', data['ensaio_id'], 'success')
                self.Update_Logs("Ensaio finalizado com êxito")
            else:
                self.write_json('/home/pi/Documents/bayer_project/Comunication/', 'to_pc.json', data['ensaio_id'], 'error')
                self.Update_Logs("O ensaio falhou")
            #Finaliza ensaio e exibe logs
            self.Show_Logs()

    #Função para finalizar ensaio           
    def FinalizaEnsaio(self):
        #Atualiza Logs
        self.ids.Logs.text = "Realizando Ensaio"
        #Exibe widget botão finalizar
        self.remove_widget(self.ids.FinalizaEnsaio)	
        #Exibe widget botão iniciar
        self.add_widget(self.ids.IniciaEnsaio)
        #Aletera a tela
        self.parent.current = 'Home'

    

kv = Builder.load_file('design_tcc_app_raspberry.kv')

Window.clearcolor = (1, 1, 1, 1)
Window.size = (800, 480)
Window.fullscreen = 'auto'

class MyApp(App):
    def build(self):
        WindowManager()
        return kv

if __name__ == '__main__':
    MyApp().run()