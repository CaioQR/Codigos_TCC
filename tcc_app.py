import kivy
from kivy.app import App
from kivy.uix.label import Label
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.textinput import TextInput
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
from IPython.display import display
import pandas as pd

# Definir telas
class WindowManager(ScreenManager):
    pass

class HomeWindow(Screen):
    pass


#Código referente à tela Etapa 1
class Etapa1Window(Screen): 
    def __init__(self, **kwargs):
        super(Etapa1Window, self).__init__(**kwargs)
        #Cria um relógio que chamará a função 'atualiza' a cada 1 segundo
        Clock.schedule_interval(self.atualiza, 1)
    

    #Variáveis
    ensaio = ''
    tecnico = ''
    current_datetime = '00:00   00/00/0000'
    lista_especies = []
    lista_comentarios = []
    

    #Função para limpar os dados preenchidos na tela
    def Clear_Data(self):
        #Limpa as variáveis
        self.tecnico = ''
        self.ensaio = ''
        self.lista_especies = []
        self.lista_comentarios = []
        
        #Limpa os campos da tela
        self.ids.id_ensaio.text = ''
        self.ids.tecnico.text = ''
        for c in range(ord('A'), ord('I')):
            comand = "self.ids.Spinner_"+chr(c)+".text = 'Espécie'"
            exec(comand)
        for c in range(ord('A'), ord('I')):
            comand = 'self.ids.Comentarios_'+chr(c)+'.text = ""'
            exec(comand)
        

    #Função para atualizar a data    
    def atualiza(self, dt):
        #Coleta a data e hora atual
        self.current_datetime = datetime.now()
        #Exibe os dados coletados na tela
        self.ids.current_date.text = self.current_datetime.strftime("%H:%M:%S   %d/%m/%Y")


    #Função para gerar um ID único para cada ensaio
    def Gera_ID (self):
        #Verifica se o ID já foi gerado (caso o botão seja pressionado novamente)
        if (self.ensaio!=''):
            print('já gerei id')
            pass
        #Cria um ID único
        else:
            #https://www.codegrepper.com/code-examples/python/get+list+of+folders+in+directory+python
            #epochtime+id bandeja
            print('gerei id')
            self.ensaio = '1234'
            self.ids.id_ensaio.text = self.ensaio


    #Função para salvar os dados preenchidos
    def save_data(self):
        #Atualiza as informações
        agora = datetime.now()
        self.datetime = agora.strftime("%H:%M %d/%m/%Y")
        self.ensaio = self.ids.id_ensaio.text
        self.tecnico = self.ids.tecnico.text
        for c in range(ord('A'), ord('I')):
            comand = 'self.lista_especies.append(self.ids.Spinner_'+chr(c)+'.text)'
            exec(comand)
        for c in range(ord('A'), ord('I')):
            comand = 'self.lista_comentarios.append(self.ids.Comentarios_'+chr(c)+'.text)'
            exec(comand)

        #Verifica dados Nulos
        verifica_dados = []
        verifica_dados.append(self.ensaio)
        verifica_dados.append(self.tecnico)
        verifica_dados.append(self.datetime)
        verifica_dados.append(self.lista_especies)
        verifica_dados.append(self.lista_comentarios)
        FaltamDados = False
        for i in range(0,len(verifica_dados)):
            if(verifica_dados[i]==''):
                FaltamDados = True
        if(FaltamDados):
            #PopUp de dados faltando
            box = BoxLayout(orientation='vertical',padding=10,spacing=10)
            popup = Popup(title='Atenção!', content=box, auto_dismiss=False, size_hint=(0.4,0.3))
            texto = Label(text='Você possui dados faltando')
            botao = Button(text='Preencher dados',on_release=popup.dismiss)
            box.add_widget(texto)
            box.add_widget(botao)
            popup.open()
        else:
            #Função Criar Ensaio CSV
            self.Cria_Ensaio_CSV()


    #Função para criar arquivo CSV com os dados preenchidos
    def Cria_Ensaio_CSV(self):
        #Trata os dados
        coluna_celula = []
        coluna_especie = []
        coluna_comentarios = []
        j = 0
        for c in range(ord('A'), ord('I')):
            for i in range(1,17):
                coluna_celula.append(chr(c)+str(i))
                coluna_especie.append(self.lista_especies[j])
                coluna_comentarios.append(self.lista_comentarios[j])
            j += 1

        #Cria o dataframe
        df = pd.DataFrame()
        df['DiscoFoliar'] = range(1,129)
        df['ID_Ensaio'] = self.ensaio
        df['Tecnico'] = self.tecnico
        df['Inicio'] = self.datetime
        df['Especie'] = coluna_especie
        df['Comentarios'] = coluna_comentarios
        df['Celula'] = coluna_celula

        #Converte o data frame para o formato desejado
        #https://stackoverflow.com/questions/27758126/exchanging-variables-between-screens-in-kivy-python
        #https://www.geeksforgeeks.org/create-a-directory-in-python/
        #df.to_excel("Ensaio_"+str(self.ensaio)+".xlsx")
        df.to_csv("Ensaio_"+str(self.ensaio)+".csv", index=False)
        print(df)
        display(df)
        df.style

        #Exibe PopUp avisando que o ensaio foi criado
        box = BoxLayout(orientation='vertical',padding=10,spacing=10)
        popup = Popup(title='Ensaio Criado', content=box, auto_dismiss=False, size_hint=(0.4,0.3))
        texto = Label(text='O ensaio '+str(self.ensaio)+' foi criado')
        botao = Button(text='ok',on_release=popup.dismiss)
        box.add_widget(texto)
        box.add_widget(botao)
        popup.open()

        #Limpa os campos
        self.Clear_Data()

        #Altera a página

    

class RealizaEnsaioCompletoWindow(Screen):
    pass

class Etapa2Window(Screen):
    pass

class HistoricoWindow(Screen):
    pass


kv = Builder.load_file('design_screenmanager.kv')

Window.clearcolor = (1, 1, 1, 1)
Window.size = (1280, 720)
Window.minimum_width, Window.minimum_height = (1280, 720)

class MyApp(App):
    def build(self):
        return kv
        
if __name__ == '__main__':
    MyApp().run()