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


# Definir telas
class WindowManager(ScreenManager):
    pass

class HomeWindow(Screen):
    def __init__(self, **kwargs):
        super(HomeWindow, self).__init__(**kwargs)
        #Cria um relógio que chamará a função 'VerificaJson' a cada 10 segundos
        Clock.schedule_interval(self.VerificaJson, 10)

    #Função para atualizar a data    
    def VerificaJson(self, dt):
        #Exibe o IP na tela
        self.ids.labelIP.text = "IP: " + str(socket.gethostbyname(socket.gethostname()))       
        #Carrega O arquivo Json
        path = os.getcwd()+'\\Raspberry - Interface\\Connection\\to_pi.json'
        with open(path, 'r', encoding="utf-8") as config_file:
            data=config_file.read()
            JsonToPi = json.loads(data) 
            config_file.close()    
        #Verifica o status
        tela = JsonToPi['status']
        #Seleciona a tela 
        if (tela == 'running'):
            self.parent.current = 'Ensaio'

    #Função para abrir aplicativo de configurações de rede    
    def Abrir_Configuracoes(self):
        print("abri settings")
        pass




class EnsaioWindow(Screen):
    pass



kv = Builder.load_file('design_tcc_app_raspberry.kv')

Window.clearcolor = (1, 1, 1, 1)
Window.size = (800, 480)
#Window.fullscreen = 'auto'

class MyApp(App):
    def build(self):
        WindowManager()
        return kv

if __name__ == '__main__':
    MyApp().run()