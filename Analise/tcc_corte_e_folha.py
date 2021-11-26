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
group_list = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H']
bioassay = 9895
lagarta_lista = []
folha_lista = []
horario_atual = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
scale = 0.1
condicao = 'Controle'
operador = 'João'
planta = 'Soja'
lagarta = 'Chrysodeixis includens'

######################################### MAHALANOBIS #####################################
import scipy as sp
def mahalanobis(x=None, data=None, cov=None):
    x_minus_mu = x - np.mean(data)
    if not cov:
        cov = np.cov(data.values.T)
    inv_covmat = sp.linalg.inv(cov)
    left_term = np.dot(x_minus_mu, inv_covmat)
    mahal = np.dot(left_term, x_minus_mu.T)
    return mahal.diagonal()

################################################ IMAGEM ##############################################
def Cortar_Imagens(group_path):
#Percorre os paths de fotos dos grupos
  for group in group_list:
    group_path = path_raiz+str(bioassay)+'/Fotos_Originais/'+str(bioassay)+'_Grupo_'+group
    ImgFile = group_path
    # IMAGEM
    img_rgb = cv.imread(ImgFile,1) #Colorida
    img_gray = cv.imread(ImgFile,0) #grayscale
########################################## IDENTIFICAR CÍRCULOS ######################################
    # QUADRANTE
    src1 = src1[int(src1.shape[0]/2-400):int(src1.shape[0]/2+400), int(src1.shape[1]/2-400):int(src1.shape[1]/2+400)].copy()
    #[200:900, 570:1320]
    src0 = src0[int(src0.shape[0]/2-400):int(src0.shape[0]/2+400), int(src0.shape[1]/2-400):int(src0.shape[1]/2+400)].copy()

    # CONTORNOS
    rgb_planes = cv.split(src0)
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

    # Achar os círculos
    circles = cv.HoughCircles(dst,
                              cv.HOUGH_GRADIENT,
                              dp=1.15,
                              minDist=110,
                              param1=110,
                              param2=9,
                              minRadius=55,
                              maxRadius=58)
    # 1.15, 110, 100, 8, 46, 50
    # Mudar para inteiro
    circles = np.uint16(np.around(circles))

    # LISTA DE COORDENADAS DOS CÍRCULOS
    center = []
    for i in circles[0,:]:
        center.append([i[0],i[1], i[2]])
    # treat circles with pandas dataframe 
    df = pd.DataFrame(center, columns=['x','y','radius'])
    # order circles by x position and limit result to 16 circles (this will exclude the other circles)
    df = df.sort_values(by='x').reset_index(drop=True).head(n=30) 
    # creates group_index
    df['group_index'] = str(group)
    # creates cell_index
    df = df.sort_values(by=['group_index', 'y'])
    df['cell_index'] = range(1, len(df.index)+1)
    
    # Mahalanobis
    df_mahala = df.copy()
    df_mahala['mahala'] = mahalanobis(df_mahala[['x','y']], df_mahala[['x','y']])

    # DESENHAR CÍRCULOS NA IMAGEM
    # desenhar os círculos na imagem
    circles_image = src1.copy()
    df = df_mahala.drop(df_mahala[df_mahala.mahala < 0.001].index)
    df = df.drop(df[df.mahala > 4].index)
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
      image = src1[(df.y[index]-70):(df.y[index]+70),(df.x[index]-70):(df.x[index]+70)]
      # NOME E PATH DAS 16 IMAGENS
      image_name = str(df.group_index[index])+str(df.cell_index[index])+'.jpg'
      cv.imwrite(path_raiz + str(bioassay) + '/Fotos_Cortadas/' + str(bioassay) + '_Foto_' + image_name, image) 
      i+=1
  return

######################################### ANALISAR IMAGENS ########################################
def Analisar_Imagens(img_path):
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

################ 1a ETAPA ###############
def csv_inicial():
  df_inicial = pd.DataFrame()
  df_inicial = pd.DataFrame(folha_lista)
  df_inicial = df_inicial.rename(columns={'area':'area_folha'})
  df_inicial = df_inicial.apply(pd.Series.explode)
  # Filtrar áreas
  # df_inicial = df_inicial[(df_inicial.area_folha > 700) & (df_inicial.area_folha < 3000)] # grãos
  df_inicial = df_inicial.groupby("Célula_ID").sum().sort_values(by=['Célula_ID'])
  df_inicial = df_inicial.reset_index()

  df_lagarta = pd.DataFrame()
  df_lagarta = pd.DataFrame(lagarta_lista)
  df_lagarta = df_lagarta.apply(pd.Series.explode)
  df_lagarta = df_lagarta.groupby("Célula_ID").sum().sort_values(by=['Célula_ID'])
  df_lagarta = df_lagarta.reset_index()

  # Converter em escala micron
  df_inicial["Área inicial da folha"] = df_inicial['area_folha'] * (scale**2)
  df_inicial['Área inicial da lagarta'] = df_lagarta['area'] * (scale**2)
  df_inicial['Data início'] = horario_atual
  df_inicial['Data final'] = ''
  df_inicial['Grupo_ID'] = group
  df_inicial['Condição'] = condicao
  df_inicial['Planta'] = planta
  df_inicial['Lagarta'] = lagarta
  df_inicial['Técnic o'] = operador
  df_inicial["Área final da folha"] = ''
  df_inicial["Área final da lagarta"] = ''
  df_inicial['Redução (%)'] = ''
  df_inicial['Aumento (%)'] = ''
  df_inicial['Status da lagarta'] = ''
  df_inicial = df_inicial[['Data início', 'Data final', 'Técnico', 'Planta', 'Lagarta', 'Condição', 'Grupo_ID', 'Célula_ID',
          'Área inicial da folha', "Área final da lagarta", 'Redução (%)', 'Área inicial da lagarta', "Área final da lagarta", 'Aumento (%)', 'Status da lagarta']]
  df_inicial.to_csv(path_raiz + str(bioassay) +str(bioassay) + '.csv')
  return df_inicial

################ 2a ETAPA ###############
def csv_final():
  df_final = pd.read_csv(path_raiz + str(bioassay) +str(bioassay) + '.csv')
  df_final['Área final da folha'] = folha_lista
  df_final['Redução (%)'] = round((df_final['Área inicial da folha'] - df_final['Área final da folha']) / df_final['Área inicial da planta'] *100, 2)
  df_final['Data final'] = horario_atual
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