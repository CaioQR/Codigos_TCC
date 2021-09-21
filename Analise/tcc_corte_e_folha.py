# -*- coding: utf-8 -*-
"""TCC_Corte_e_Folha.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/18nY_7Yctqw-gZmeUGQ4jeb-Y-_RDwCy5

#Configuração do Colab
"""

from google.colab import drive
drive.mount('/content/drive')

"""Irregular object: https://stackoverflow.com/questions/64394768/how-calculate-the-area-of-irregular-object-in-an-image-opencv-python-3-8

Blob detection: https://www.youtube.com/watch?v=2puHfSKnG7c 

Mask R-CNN: https://www.youtube.com/watch?v=8m8m4oWsp8M

Color segmentation: https://www.youtube.com/watch?v=efWITgemKvs

#Importações

##Módulos e Bibliotecas
"""

from datetime import datetime

import cv2 as cv
import numpy as np
import pandas as pd
from google.colab.patches import cv2_imshow
from pandas import DataFrame as df

import matplotlib.pyplot as plt

from skimage import measure, io, img_as_ubyte
from skimage.color import label2rgb, rgb2gray

from skimage.filters import threshold_otsu
from skimage.segmentation import clear_border

"""##Imagem

cv.imread: https://www.geeksforgeeks.org/python-opencv-cv2-imread-method/
"""

# file information
ImgFile = '/content/drive/MyDrive/Mauá/TCC/Códigos/Imagens/larvas_bandeja_2.jpg'

# read image
src1 = cv.imread(ImgFile,1)                             #Colorida
src0 = cv.imread(ImgFile,0)                             #grayscale

# show original image
print("Image 1")
cv2_imshow(src1)
print("Image 0")
cv2_imshow(src0)

"""#Função - Recortar Foto

##Aplicação dos filtros

Open.cv: https://docs.opencv.org/3.4/d4/d86/group__imgproc__filter.html 

cv.dilate: https://opencv24-python-tutorials.readthedocs.io/en/latest/py_tutorials/py_imgproc/py_morphological_ops/py_morphological_ops.html

cv.medianBlur: https://docs.opencv.org/3.4/d4/d86/group__imgproc__filter.html#ga564869aa33e58769b4469101aac458f9

cv.absdiff: https://docs.opencv.org/3.4/d2/de8/group__core__array.html#ga6fef31bc8c4071cbc114a758a2b79c14 

cv.normalize: https://docs.opencv.org/2.4/modules/core/doc/operations_on_arrays.html#normalize

cv.merge: https://docs.opencv.org/3.4/d2/de8/group__core__array.html#ga7d7b4d6c6ee504b30a20b1680029c7b4

cv.threshold: https://docs.opencv.org/4.5.2/d7/d4d/tutorial_py_thresholding.html

Otsu's thresholding: https://learnopencv.com/otsu-thresholding-with-opencv/
"""

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

# show image with edges
print("Edges Filter")
cv2_imshow(dst)

"""##Localizar os círculos

cv.HoughCircles: https://medium.com/turing-talks/houghcircles-detec%C3%A7%C3%A3o-de-c%C3%ADrculos-em-imagens-com-opencv-e-python-2d229ad9d43b
"""

# Achar os círculos
circles = cv.HoughCircles(dst,
                          cv.HOUGH_GRADIENT,
                          dp=1.2,
                          minDist=100,
                          param1=100,
                          param2=8,
                          minRadius=40,
                          maxRadius=45)
# 200, 200, 85 e 90
# Mudar para inteiro
circles = np.uint16(np.around(circles))
print(circles)

# Save circles coordinates in a list of tuples(center)
group='A'
center = []
for i in circles[0,:]:
    center.append([i[0],i[1], i[2]])
# treat circles with pandas dataframe 
df = pd.DataFrame(center, columns=['x','y','radius'])
# order circles by x position and limit result to 16 circles (this will exclude the other circles)
df = df.sort_values(by='x').reset_index(drop=True).head(n=16) 
# creates group_index
df['group_index'] = str(group)
# creates cell_index
df = df.sort_values(by=['group_index', 'y'])
df['cell_index'] = range(1, 17)


# show circles information
print(df)

# desenhar os círculos na imagem
circles_image = src1.copy()
for index, row in df.iterrows():
    # desenhar a borda do círculo
    cv.circle(circles_image,(df.x[index],df.y[index]),
              df.radius[index],(0,255,0),2)
    # desenhar o centro do círculo
    cv.circle(circles_image,(df.x[index],df.y[index]),2,(0,0,255),3)
# exibir imagem com círculos
print("Image With Circles")
cv2_imshow(circles_image)

"""##Divisão da Imagem"""

i = 0
fig, axes = plt.subplots(4, 4, figsize=(16, 8), sharex=True, sharey=True)
ax = axes.ravel()
for index, row in df.iterrows():
  # crop image
  image = src1[(df.y[index]-40):(df.y[index]+40),(df.x[index]-40):(df.x[index]+40)]
  # 100
  # save image
  image_name = str(df.group_index[index])+str(df.cell_index[index])+'.jpg'
  cv.imwrite('/content/drive/MyDrive/Mauá/TCC/Códigos/Imagens/Imagens cortadas/'+image_name, image) 
  # show images
  # print(image_name)
  # cv2_imshow(image)
  ax[i].imshow(image)
  ax[i].set_title(image_name)
  i+=1

for a in ax.ravel():
    a.axis('off')

fig.tight_layout()

"""#Análise da Figura - Algoritmo Caio

##Função - Análise da Área
"""

def main(cell):
  file_path = '/content/drive/MyDrive/Mauá/TCC/Códigos/Imagens/Imagens cortadas/'
  arquivo = file_path + cell + ".jpg"
  image = cv.imread(arquivo,1)
  image_gray = cv.imread(arquivo,0)

  # Threshold
  threshold = threshold_otsu(image_gray)
  thresholded_img = image < threshold
  
  # Labels
  label_image = measure.label(thresholded_img,
                              connectivity = image.ndim)

  all_props = measure.regionprops(label_image, image)
  #Can print various parameters for all objects
  for prop in all_props:
    # print('Label: {} Area: {}'.format(prop.label, prop.area))
    props = measure.regionprops_table(label_image, image, 
                          properties=['label',
                                      'area', 'equivalent_diameter'])
  
  scale = 0.6
  df2 = pd.DataFrame(props)
  # Converter em escala micron
  df2['equivalent_diameter_microns'] = df2['equivalent_diameter'] * (scale)
  df2['area_sq_microns'] = df2['area'] * (scale**2)

  del df2['equivalent_diameter']
  # del df2['area']
  # Filtrar áreas
  df2.drop(df2[df2.area < 200].index, inplace=True) # grãos
  df2.drop(df2['area_sq_microns'].idxmax(), inplace=True) # bandeja
  df2['Cell'] = cell
  total_area = df2['area_sq_microns'].sum()
  display(df2)
  return total_area

"""##Executa a Função"""

# read image
lista=[]
cells=[]

for i in range(1,17):
  leaf_index=group+str(i)
  area = main(leaf_index)
  lista.append(area)
  cells.append(leaf_index)

"""### CSV"""

#### Valores para edição #########
bioassay = 9895
path = '/Bayer/Resultados_Bioassay/'
operador = 'Bang'
planta = 'Soja'
lagarta = 'Chrysodeixis includens'
condicao = 'Controle'
hora_atual = datetime.now().strftime("%d/%m/%Y %H:%M:%S")


teste =[]
n= 0
for i in range(len(lista)):
  teste.append(lista[i]*(0.1+n))
  n += 0.05

def csv_inicial():
  db_inicial = pd.DataFrame()
  
  db_inicial['Área inicial da planta'] = lista
  db_inicial['Área final da planta'] = ''
  db_inicial['Redução (%)'] = ''
  db_inicial['Nível de redução'] = ''

  db_inicial['Data início'] = hora_atual
  db_inicial['Data final'] = ''
  db_inicial['Operador'] = operador
  db_inicial["Planta"] = planta
  db_inicial["Lagarta"] = lagarta
  db_inicial['Condição'] = condicao

  db_inicial["Groupo_ID"] =  cells[0][0]
  db_inicial['Cell_ID'] = list(range(1,17))

  cols = db_inicial.columns.tolist()
  cols = cols[-8:] + cols[:-8]
  db_inicial = db_inicial[cols]

  db_inicial.to_csv('/content/drive/MyDrive/Mauá/TCC/Códigos/CSV/' + str(bioassay) + '.csv')
  display(db_inicial) # teste depois tirar
csv_inicial()

def csv_final():
  db_final = pd.read_csv('/content/drive/MyDrive/Mauá/TCC/Códigos/CSV/' + str(bioassay) + '.csv')

  db_final['Área final da planta'] = teste # teste depois apagar
  db_final['Redução (%)'] = round((db_final['Área inicial da planta'] - db_final['Área final da planta']) / db_final['Área inicial da planta'] *100, 2)
  db_final['Data final'] = hora_atual

  # lista de condições para nível de redução
  conditions1 = [
      (db_final['Redução (%)'] >= 90), (db_final['Redução (%)'] < 90) & (db_final['Redução (%)'] >= 80),
       (db_final['Redução (%)'] < 80) & (db_final['Redução (%)'] >= 70), (db_final['Redução (%)'] < 70) & (db_final['Redução (%)'] >= 60), 
       (db_final['Redução (%)'] < 60) & (db_final['Redução (%)'] >= 50), (db_final['Redução (%)'] < 50) & (db_final['Redução (%)'] >= 40), 
       (db_final['Redução (%)'] < 40) & (db_final['Redução (%)'] >= 30), (db_final['Redução (%)'] < 30) & (db_final['Redução (%)'] >= 20), 
       (db_final['Redução (%)'] < 20) & (db_final['Redução (%)'] >= 10), (db_final['Redução (%)'] < 10)
      ]
  # # lista de valores para cada condição
  values1 = [10, 9, 8, 7, 6, 5, 4, 3, 2, 1]
  db_final['Nível de redução'] = np.select(conditions1, values1)
  db_final.drop(db_final.columns[0], axis=1, inplace=True)
  db_final.to_csv('/content/drive/MyDrive/Mauá/TCC/Códigos/CSV/' + str(bioassay) + '.csv')
  display(db_final) # teste depois tirar
csv_final()

"""#Laços de Repetição"""

# #Define os grupos
# group_list = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H']

# #Percorre os paths de fotos dos grupos
# for group in group_list:
#   group_path = path+str(bioassay)+'/Fotos_Originais/'+str(bioassay)+'_Grupo_'+group
#   print(group_path)

# #Linha de separação
# print()
# print("*"*100)
# print()

# #Percorre os paths de fotos das folhas cortadas
# for group in group_list:
#   for i in range(1,17):
#     img_path = path+str(bioassay)+'/Fotos_Cortadas/'+str(bioassay)+'_Foto_'+group+str(i)
# print(img_path)

"""#Realizar Teste"""

# def Capturar_Imagens():
#   pass

# def Cortar_Imagens(group_path):
#   pass
  
# def Analisar_Imagens(img_path):
#   return True

# #Valores para edição
# bioassay = 9895
# path = '/Bayer/Resultados_Bioassay/'

# #Define os grupos
# group_list = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H']

# #Execução da Função de Captura das Imagens
# Capturar_Imagens()

# #Execução da Função de Corte das Imagens
# for group in group_list:
#   group_path = path+str(bioassay)+'/Fotos_Originais/'+str(bioassay)+'_Grupo_'+group
#   Cortar_Imagens(group_path)

# #Execução da Função de Análise das Imagens
# ListGroup = []
# ListCell = []
# ListArea = []
# for group in group_list:
#   for i in range(1,17):
#     img_path = path+str(bioassay)+'/Fotos_Cortadas/'+str(bioassay)+'_Foto_'+group+str(i)
#     img_area = Analisar_Imagens(img_path)
#     ListArea.append(img_area)
#     ListCell.append(i)
#     ListGroup.append(group)

# df = pd.DataFrame()
# df['Group'] = ListGroup
# df['Cell'] = ListCell
# df['Área'] = ListArea

# display(df.set_index('Cell').T)