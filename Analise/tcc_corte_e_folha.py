############################################### BIBLIOTECAS ###########################################
from datetime import datetime

import cv2 as cv
import numpy as np
import pandas as pd
from pandas import DataFrame as df
import matplotlib.pyplot as plt

from skimage import measure, io, img_as_ubyte
from skimage.color import label2rgb, rgb2gray
from skimage.filters import threshold_otsu
from skimage.segmentation import clear_border

########################################## VARIÁVEIS DO ENSAIO #####################################
path_raiz = 'H:\Caio Quaglierini\Documents\TCC\'
bioassay = 9895
lagarta_lista = []
folha_lista = []
horario_atual = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
scale = 0.6
condicao = 'Controle'
operador = 'João'
planta = 'Soja'
lagarta = 'Chrysodeixis includens'

################################################ IMAGEM ##############################################
#Define os grupos
group_list = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H']
#Percorre os paths de fotos dos grupos
for group in group_list:
  group_path = path_raiz+str(bioassay)+'/Fotos_Originais/'+str(bioassay)+'_Grupo_'+group
  ImgFile = group_path
  # IMAGEM
  img_rgb = cv.imread(ImgFile,1) #Colorida
  img_gray = cv.imread(ImgFile,0) #grayscale

########################################## IDENTIFICAR CÍRCULOS ######################################
# QUADRANTE
img_rgb = img_rgb[200:900, 570:1320].copy()
img_gray = img_gray[200:900, 570:1320].copy()

# CONTORNOS
rgb_planes = cv.split(img_gray)
result_planes = []
result_norm_planes = []
for plane in rgb_planes:
    dilated_img = cv.dilate(plane, np.ones((10,10), np.uint8))
    bg_img = cv.medianBlur(dilated_img, 21)
    diff_img = 255 - cv.absdiff(plane, bg_img)
    norm_img = cv.normalize(diff_img,None, alpha=0, beta=255, norm_type=cv.NORM_MINMAX, dtype=cv.CV_8UC1)
    result_planes.append(diff_img)
    result_norm_planes.append(norm_img)

result = cv.merge(result_planes)
result_norm = cv.merge(result_norm_planes)

maxValue = 255
retval, dst = cv.threshold(result, 0, maxValue, cv.THRESH_BINARY_INV+cv.THRESH_OTSU)

# CÍRCULOS
circles = cv.HoughCircles(dst,
                          cv.HOUGH_GRADIENT,
                          dp=1.2,
                          minDist=100,
                          param1=100,
                          param2=8,
                          minRadius=40,
                          maxRadius=45)
circles = np.uint16(np.around(circles))

# LISTA DE COORDENADAS DOS CÍRCULOS
group='A'
center = []
for i in circles[0,:]:
    center.append([i[0],i[1], i[2]])
df = pd.DataFrame(center, columns=['x','y','radius'])
df = df.sort_values(by='x').reset_index(drop=True).head(n=16) 
df['group_index'] = str(group)
df = df.sort_values(by=['group_index', 'y'])
df['cell_index'] = range(1, 17)

# DESENHAR CÍRCULOS NA IMAGEM
circles_image = img_rgb.copy()
for index, row in df.iterrows():
    # desenhar a borda do círculo
    cv.circle(circles_image,(df.x[index],df.y[index]),
              df.radius[index],(0,255,0),2)
    # desenhar o centro do círculo
    cv.circle(circles_image,(df.x[index],df.y[index]),2,(0,0,255),3)

########################################## RECORTAR CÍRCULOS ######################################
i = 0
for index, row in df.iterrows():
  # crop image
  image = img_rgb[(df.y[index]-40):(df.y[index]+40),(df.x[index]-40):(df.x[index]+40)]
  # NOME E PATH DAS 16 IMAGENS
  image_name = str(df.group_index[index])+str(df.cell_index[index])+'.jpg'
  cv.imwrite(path_raiz + str(bioassay) + '/Fotos_Cortadas/' + str(bioassay) + '_Foto_' + image_name, image) 
  i+=1

################################################# MAIN #############################################
def main(cell):
  #Percorre os paths de fotos dos grupos
  for group in group_list:
    #Percorre os paths de fotos das folhas cortadas
    for i in range(1,17):
      img_path = path_raiz+str(bioassay)+'/Fotos_Cortadas/'+str(bioassay)+'_Foto_'+group+str(i)
      arquivo = img_path + ".jpg"
      image = cv.imread(arquivo,1)
      image_gray = cv.imread(arquivo,0)
      # Threshold
      threshold = threshold_otsu(image_gray)
      thresholded_img = image < threshold
      # Labels
      label_image = measure.label(thresholded_img,
                                  connectivity = image.ndim)
      all_props = measure.regionprops(label_image, image)
      for j in all_props:
        props_folha = measure.regionprops_table(label_image, image, 
                              properties=['label', 'area'])
      props_folha['Célula_ID'] = i
      folha_lista.append(props_folha)
  return folha_lista

################################################## CSV #############################################
lista=[]
cells=[]
for i in range(1,17):
  leaf_index=group+str(i)
  area = main(leaf_index)
  lista.append(area)
  cells.append(leaf_index)

teste =[]
n= 0
for i in range(len(lista)):
  teste.append(lista[i]*(0.1+n))
  n += 0.05

def csv_inicial():
  df_inicial = pd.DataFrame()
  df_inicial = pd.DataFrame(folha_lista)
  df_inicial = df_inicial.rename(columns={'area':'area_folha'})
  df_inicial = df_inicial.apply(pd.Series.explode)
  # Filtrar áreas
  # df_inicial = df_inicial[(df_inicial.area_folha > 700) & (df_inicial.area_folha < 3000)] # grãos
  df_inicial = df_inicial.groupby("Célula_ID").sum().sort_values(by=['Célula_ID'])
  df_inicial = df_inicial.reset_index()
  # df_inicial.drop(columns='label', inplace=True)

  df_lagarta = pd.DataFrame()
  df_lagarta = pd.DataFrame(lagarta_lista)
  df_lagarta = df_lagarta.apply(pd.Series.explode)
  df_lagarta = df_lagarta.groupby("Célula_ID").sum().sort_values(by=['Célula_ID'])
  df_lagarta = df_lagarta.reset_index()

  # Converter em escala micron
  df_inicial["A0_Folha"] = df_inicial['area_folha'] * (scale**2)
  df_inicial['A0_Lagarta'] = df_lagarta['area'] * (scale**2)

  df_inicial['Data início'] = horario_atual
  df_inicial['Data final'] = ''
  df_inicial['Grupo_ID'] = 'A'
  df_inicial['Condição'] = condicao
  df_inicial['Planta'] = planta
  df_inicial['Lagarta'] = lagarta
  df_inicial['Técnico'] = operador
  df_inicial["A'_Folha"] = ''
  df_inicial["A'_Lagarta"] = ''
  df_inicial['Redução (%)'] = ''
  df_inicial['Aumento (%)'] = ''
  df_inicial['Status da lagarta'] = ''
  df_inicial = df_inicial[['Data início', 'Data final', 'Técnico', 'Planta', 'Lagarta', 'Condição', 'Grupo_ID', 'Célula_ID',
          'A0_Folha', "A'_Lagarta", 'Redução (%)', 'A0_Lagarta', "A'_Lagarta", 'Aumento (%)', 'Status da lagarta']]
  df_inicial.to_csv(path_raiz + str(bioassay) +str(bioassay) + '.csv')
  return df_inicial

def csv_final():
  df_final = pd.read_csv(path_raiz + str(bioassay) +str(bioassay) + '.csv')
  df_final['Área final da planta'] = teste # teste depois apagar
  df_final['Redução (%)'] = round((df_final['Área inicial da planta'] - df_final['Área final da planta']) / df_final['Área inicial da planta'] *100, 2)
  df_final['Data final'] = hora_atual
  # lista de condições para nível de redução
  conditions1 = [
      (df_final['Redução (%)'] >= 90), (df_final['Redução (%)'] < 90) & (df_final['Redução (%)'] >= 80),
       (df_final['Redução (%)'] < 80) & (df_final['Redução (%)'] >= 70), (df_final['Redução (%)'] < 70) & (df_final['Redução (%)'] >= 60), 
       (df_final['Redução (%)'] < 60) & (df_final['Redução (%)'] >= 50), (df_final['Redução (%)'] < 50) & (df_final['Redução (%)'] >= 40), 
       (df_final['Redução (%)'] < 40) & (df_final['Redução (%)'] >= 30), (df_final['Redução (%)'] < 30) & (df_final['Redução (%)'] >= 20), 
       (df_final['Redução (%)'] < 20) & (df_final['Redução (%)'] >= 10), (df_final['Redução (%)'] < 10)
      ]
  # # lista de valores para cada condição
  values1 = [10, 9, 8, 7, 6, 5, 4, 3, 2, 1]
  df_final['Nível de redução'] = np.select(conditions1, values1)
  df_final.drop(df_final.columns[0], axis=1, inplace=True)
  df_final.to_csv(path_raiz + str(bioassay) +str(bioassay) + '.csv')
  return df_final

############################################### REALIZAR TESTE #############################################
def Cortar_Imagens(group_path):
  pass
  
def Analisar_Imagens(img_path):
  return True

#Execução da Função de Corte das Imagens
for group in group_list:
  group_path = path_raiz+str(bioassay)+'/Fotos_Originais/'+str(bioassay)+'_Grupo_'+group
  Cortar_Imagens(group_path)

#Execução da Função de Análise das Imagens
ListGroup = []
ListCell = []
ListArea = []
for group in group_list:
  for i in range(1,17):
    img_path = path_raiz+str(bioassay)+'/Fotos_Cortadas/'+str(bioassay)+'_Foto_'+group+str(i)
    img_area = Analisar_Imagens(img_path)
    ListArea.append(img_area)
    ListCell.append(i)
    ListGroup.append(group)

df = pd.DataFrame()
df['Group'] = ListGroup
df['Cell'] = ListCell
df['Área'] = ListArea