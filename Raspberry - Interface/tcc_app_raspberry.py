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
        Clock.schedule_interval(self.VerificaJson, 3)

    screen = "Home"

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
        #Cria um relógio que chamará a função 'Atualiza' a cada 10 segundos
        Clock.schedule_interval(self.Atualiza, 5)


    #Função para atualizar as informações    
    def Atualiza(self, dt):
        #Carrega O arquivo Json
        path = os.getcwd()+'\\Raspberry - Interface\\Connection\\to_pi.json'
        with open(path, 'r', encoding="utf-8") as config_file:
            data=config_file.read()
            JsonToPi = json.loads(data) 
            config_file.close()    
        #Verifica o status
        tela = JsonToPi['status']
        #Aletera o widget
        if (tela == 'sleeping'):
            try:
                #Exibe widget botão finalizar
                self.add_widget(self.ids.FinalizaEnsaio)
            except:
                pass
    
    def RealizaEnsaio(self):
        #Verificar se a porta está aberta:
        if (False):
            #PopUp avisando que a porta está aberta
            box = BoxLayout(orientation='vertical',padding=10,spacing=10)
            popup = Popup(title='Atenção!', content=box, auto_dismiss=False, size_hint=(0.4,0.3))
            texto = Label(text='A porta está aberta')
            botao = Button(text='ok',on_release=popup.dismiss)
            box.add_widget(texto)
            box.add_widget(botao)
            popup.open()
        else:
            #Remove widget botão iniciar
            self.remove_widget(self.ids.IniciaEnsaio)
            #Exibe widget botão finalizar
            self.remove_widget(self.ids.FinalizaEnsaio)
            #Retorna a barra para P1
            self.ids.Logs.text = "Levando cameras para P1" 
            #Acende leds inferiores
            self.ids.Logs.text = "Ligando Leds inferiores"
            #Acende leds superiores
            self.ids.Logs.text = "Ligando Leds superiores"
            #Captura as 4 primeiras fotos
            self.ids.Logs.text = "Tirando fotos A-B-C-D"
            #Avança a barra para P2
            self.ids.Logs.text = "Levando cameras para P2"
            #Captura as 4 últimas fotos
            self.ids.Logs.text = "Tirando fotos E-F-G-H"
            #Apaga leds inferiores
            self.ids.Logs.text = "Desligando Leds inferiores"
            #Apaga leds superiores
            self.ids.Logs.text = "Desligando Leds superiores"
            
            
    def FinalizaEnsaio(self):
        #Exibe widget botão iniciar
        self.add_widget(self.ids.IniciaEnsaio)
        #Remove widget botão finalizar
        self.remove_widget(self.ids.FinalizaEnsaio)
        #Aletera a tela
        self.parent.current = 'Home'

    '''PC - manda por a bandeja e dar ok 
    ok do pc altera json
    ao entrar na nova tela o rasp pergunta se o ensaio esta certo, bandeja posicionada e verifica porta
    roda a rotina de teste
    altera json e aguarda na tela de finalizado
    pc verifica json e coleta as fotos
    pc altera json do rasp que volta pra tela home '''
    








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