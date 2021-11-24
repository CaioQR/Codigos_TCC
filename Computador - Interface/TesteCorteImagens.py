import pandas as pd
import matplotlib.pyplot as plt
import os
import numpy as np

from datetime import datetime
import cv2 as cv
import pandas as pd
from pandas import DataFrame as df
from skimage import measure, io, img_as_ubyte
from skimage.color import label2rgb, rgb2gray
from skimage.filters import threshold_otsu
from skimage.segmentation import clear_border
import scipy as sp
   
#Função para cálculo de mahalanobis
def mahalanobis(x=None, data=None, cov=None):
    x_minus_mu = x - np.mean(data)
    if not cov:
        cov = np.cov(data.values.T)
    inv_covmat = sp.linalg.inv(cov)
    left_term = np.dot(x_minus_mu, inv_covmat)
    mahal = np.dot(left_term, x_minus_mu.T)
    return mahal.diagonal()

#Função para cortar imagens
def Cortar_Imagens(path_local, path_temp):
    #Percorre os paths de fotos dos grupos
    for c in range(ord('A'), ord('I')):
        ImgFile = path_local+chr(c)+'.jpg'
        # IMAGEM
        src1 = cv.imdecode(np.fromfile(ImgFile, dtype=np.uint8), 1)
        src0 = cv.imdecode(np.fromfile(ImgFile, dtype=np.uint8), 0)
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
        df['group_index'] = str(chr(c))
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
        print()
    ########################################## RECORTAR CÍRCULOS ######################################
        i = 0
        for index, row in df.iterrows():
            # crop image
            image = src1[(df.y[index]-35):(df.y[index]+35),(df.x[index]-35):(df.x[index]+35)]
            # NOME E PATH DAS 16 IMAGENS
            image_name = path_temp+str(df.group_index[index])+str(df.cell_index[index])+'.jpg'
            print(image_name)
            is_success, im_buf_arr = cv.imencode(".jpg", image)
            im_buf_arr.tofile(image_name)
            i+=1


local_images_path = os.getcwd()+'\\SistemaBayer\\Ensaio_1\\Fotos\\'
local_temp_images_path = os.getcwd()+'\\SistemaBayer\\Ensaio_1\\FotosTemporarias\\'

Cortar_Imagens(local_images_path, local_temp_images_path)