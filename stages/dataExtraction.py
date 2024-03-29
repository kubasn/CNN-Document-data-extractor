# import tensorflow as tf
# from tensorflow import keras
from tensorflow.keras.preprocessing import image
# import numpy as np
# import matplotlib.pyplot as plt
# from PIL import Image, ImageOps
# from tensorflow.keras.models import load_model
# # from ./ import utils as ut
# import sys
# sys.path.append("..") # Adds higher directory to python modules path.
# import utils as ut
# import keras_ocr
# import easyocr
# reader = easyocr.Reader(['en','pl'], gpu = True)
# import cv2
# import pytesseract
import os
# import tensorflow as tf
import re
import pandas as pd
import glob
import multiprocessing as mp

import sys
sys.path.append("..") # Adds higher directory to python modules path.
import utils as ut
import cv2
import pytesseract
from pytesseract import Output
import math
import numpy as np
from itertools import filterfalse
import time
from openpyxl import Workbook
import argparse
import ntpath
import easyocr
reader = easyocr.Reader(['en','pl'], gpu = True)



def execute_main():
    image_dir = "images_classification"  # replace with your directory
    images = glob.glob(os.path.join(image_dir, "table_*.jpg"))
    print(image_dir)
    
    # create a pool of workers
    with mp.Pool(mp.cpu_count()) as pool:
        results = []
        for img_path in images:
            filename = os.path.basename(img_path)  # get the name of the file
            number_str = filename.split('_')[1].split('.')[0]  # split the filename by '_' and '.'
            number = int(number_str)  # convert the number to an integer
            print(filename, number)
            # apply the function to each image asynchronously
            result = pool.apply_async(extract, args=(img_path, number))
            results.append(result)

        # get the results
        for result in results:
            result.get()
            
            
        pool.close()
        pool.join()

def extract(img_path,number):     
    img = load_and_preprocess_image(img_path)

    img1 = cv2.imread(img_path)
    img1 = cv2.copyMakeBorder(img1, top=50, bottom=50, left=50, right=50, borderType=cv2.BORDER_CONSTANT, value=[255,255,255])

    #Szerekość kernela jako 2% totalnej szerokości

    cols = np.array(img).shape[1]
    rows = np.array(img).shape[0]

    verticalSize = cols//80 #podziel przez 30
    horizontalSize = rows//80 #podziel przez 30

    # Kernel do wykrywania linii w kierunku horyzontalnym
    horizontalStructure = cv2.getStructuringElement(cv2.MORPH_RECT, (horizontalSize, 1))
    # Kernel do wykrywania linii w kierunku wertykalnym
    verticalStructure = cv2.getStructuringElement(cv2.MORPH_RECT, (1, verticalSize))
    # Karnel rozmiaru 2 x 2
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (2, 2))
    
    
    
    #Operacje erozji i dyletacji aby wykryć linie na obrazie
    #linie poziome
    horizontal = cv2.erode(img, horizontalStructure, iterations=2)
    horizontal = cv2.dilate(horizontal, horizontalStructure, iterations=6)

    # linie pionowe
    vertical = cv2.erode(img, verticalStructure, iterations=2)
    vertical = cv2.dilate(vertical, verticalStructure, iterations=4)

    # Złączenie 2 obrazów w jeden 
    img_vh = cv2.addWeighted(vertical, 0.5, horizontal, 0.5, 0.0)
    #Erozja i binaryzacja obrazu
    #img_vh = cv2.erode(img_vh, kernel, iterations=2)
    thresh, img_vh = cv2.threshold(img_vh,128,255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)
    bitxor = cv2.bitwise_xor(img,img_vh)
    bitnot = cv2.bitwise_not(bitxor)

    # Wykryj kontury na obrazie img_vh
    contours, hierarchy = cv2.findContours(img_vh, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

     # Sort all the contours by top to bottom.
    contours, boundingBoxes = sort(contours)   
    
    # cols = np.array(img).shape[1]
    # rows = np.array(img).shape[0]
    #Create list box to store all boxes in  
    boxes = []
    # Get position (x,y), width and height for every contour and show the contour on image
    for contour in contours:
        x, y, w, h = cv2.boundingRect(contour)
        if (w<np.array(img).shape[1]*0.95 and h<np.array(img).shape[0]*0.5):
            if (w>50 and h>50):
                img1 = cv2.rectangle(img1,(x,y),(x+w,y+h),(0,255,0),5)
                boxes.append([x,y,w,h])

    image_rgb = cv2.cvtColor(img1, cv2.COLOR_BGR2RGB)

    # Minimalna wysokość prostokątów otaczających
    min_height = min([b[3] for b in boxes])

    # Sortowanie boxów według ich współrzędnych y
    boxes.sort(key=lambda b: b[1])

    # Grupowanie boxów na wiersze
    row = []
    current_row = []
    prev_box = boxes[0]

    for box in boxes:
        # Jeśli box jest na tym samym poziomie co poprzedni, dodajemy go do bieżącego wiersza
        if box[1] <= prev_box[1] + min_height/2:
            current_row.append(box)
        # Jeśli box jest na nowym poziomie, tworzymy nowy wiersz
        else:
            # Sortowanie bieżącego wiersza według współrzędnych x, co daje nam kolumny
            current_row.sort(key=lambda b: b[0])
            row.append(current_row)
            current_row = [box]
        prev_box = box

    # Dodajemy ostatni wiersz do listy wierszy
    if current_row:
        current_row.sort(key=lambda b: b[0])
        row.append(current_row)

    
        #obliczenie maksymalnej ilosci komorek w wierszu
    count = 0
    for i in range(len(row)):
        countcol = len(row[i])
    #     print(countcol)
        if countcol > count:
            count = countcol

    
    countcol = count

            
            
    i = max(range(len(row)), key=lambda index: len(row[index]))

    # tutaj jest kluczowy punkt trzeba znaleść komórki gdzie i jest największe !!!!
    print(i)
    center_points = []
    for j in range(len(row[i])):
        if row[0]:
            center_point = int(row[i][j][0] + row[i][j][2] / 2)
            center_points.append(center_point)


    center_points=np.array(center_points)
    center_points.sort()
    
        # od uporządkowuje prostokąty otaczające na podstawie ich odległości od punktów centralnych kolumn,
    #zakładając, że prostokąty otaczające bliżej środka danej kolumny należą do tej kolumny. W ten sposób 
    #kod przyporządkowuje prostokąty otaczające do odpowiednich kolumn w tabeli.

    finalboxes = []
    for i in range(len(row)):
    #     lista przechowująca prostokąty otaczające należące do danej kolumny
        lis=[]
        for k in range(countcol):
            lis.append([])
        for j in range(len(row[i])):

    # Dla każdego prostokąta otaczającego w danym wierszu, oblicza jego odległość 
    #od punktów centralnych kolumn. Robi to poprzez obliczenie wartości bezwzględnej 
    #różnicy między współrzędną x lewego górnego punktu prostokąta plus jedną czwartą jego szerokości         
    #  tutaj było zamiast /2 /4 !!!!!!!!!!!!!
            diff = abs(center_points-(row[i][j][0]+row[i][j][2]/2))
            minimum = min(diff)
            indexing = list(diff).index(minimum)
            lis[indexing].append(row[i][j])
        finalboxes.append(lis)
    

    # #tablica przechowująca wyniki rozpoznanych tekstów
    # recognized=[]

    # for box in finalboxes:
    #     for sub_box in box:
    #         if not sub_box:  # Jeśli sub_box jest pusty, dodajemy pustą przestrzeń do listy wyników
    #             recognized.append(' ')
    #         else:
    #             for element in sub_box:
    #                 y, x, w, h = element

    #                 img = bitnot[x+10:x+h-10, y+10:y+w-10]
    #                 # Przygotowanie obrazu do OCR
    #                 kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (2, 1))
    #                 border = cv2.copyMakeBorder(img,2,2,2,2, cv2.BORDER_CONSTANT,value=[255,255])
    #                 cropped = cv2.resize(border, None, fx=2, fy=2, interpolation=cv2.INTER_CUBIC)
    #                 eroded = cv2.erode(cropped, kernel,iterations=1)
    #                 dilatated = cv2.dilate(eroded, kernel,iterations=1)

    #                 # Rozpoznawanie tekstu
    #                 out = reader.readtext(dilatated)
    #                 out = ' '.join([item[1] for item in out if item[2]>0.5])

    #                 # Jeśli tekst nie został rozpoznany, spróbuj ponownie
    #                 if not out:
    #                     out = reader.readtext(dilatated)
    #                     out = ' '.join([item[1] for item in out if item[2]>0.5])

    #                 # Czyszczenie wyników
    #                 out = re.sub("[|~]|","",out)

    #                 print('a',out)
    #             recognized.append(out) # Dodaj rozpoznany tekst do listy tuż po jego wygenerowaniu

    # print('p2',out)
    # print(recognized)


    # Tablica przechowująca wyniki rozpoznanych tekstów
    recognized=[]
    image_processed = image_rgb
    image_processed = ut.cv.cvtColor(image_processed, ut.cv.COLOR_BGR2GRAY)
    _, img_bin = cv2.threshold(image_processed, 0, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)
    
    for box in finalboxes:
        for sub_box in box:
            if not sub_box:  # Jeśli sub_box jest pusty, dodajemy pustą przestrzeń do listy wyników
                recognized.append(' ')
            else:
                for element in sub_box:
                    y, x, w, h = element

                    img = img_bin[x+5:x+h-5, y+5:y+w-5]
                    # Przygotowanie obrazu do OCR
                    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (2, 1))
                    border = cv2.copyMakeBorder(img,2,2,2,2, cv2.BORDER_CONSTANT,value=[255,255])
                    cropped = cv2.resize(border, None, fx=2, fy=2, interpolation=cv2.INTER_CUBIC)
                    eroded = cv2.erode(cropped, kernel,iterations=1)
                    dilatated = cv2.dilate(eroded, kernel,iterations=1)

                    # Rozpoznawanie tekstu
                    out = reader.readtext(dilatated)
                    out = ' '.join([item[1] for item in out if item[2]>0.5])
#                     out = pytesseract.image_to_string(dilatated, lang="pol+eng", config='--psm 6')

#                     # Jeśli tekst nie został rozpoznany, spróbuj ponownie
#                     if not out:
#                         out = reader.readtext(dilatated)
#                         out = ' '.join([item[1] for item in out if item[2]>0.3])
# #                         out = pytesseract.image_to_string(dilatated, lang="pol+eng", config='--psm 6')

                    # Czyszczenie wyników
                    out = re.sub("[|~]|","",out)


                    # Dodaj szerokość i wysokość komórki do listy
#                     cell_dimensions = (w, h)
                recognized.append(out)
    #             recognized.append(out)

    # print('p2',out)
#     print(recognized)    
    
    arr = np.array(recognized)
    dataframe = pd.DataFrame(arr.reshape(len(row), countcol))

        # Ustaw pierwszy wiersz jako nagłówek
    dataframe.columns = dataframe.iloc[0]

    # Usuń pierwszy wiersz
    dataframe = dataframe[1:]
    data = dataframe.style.set_properties(align="left")


    dataframe.to_excel(f'csv_classification/{number}.xlsx', index=False)
    
    
            
def load_and_preprocess_image(img_path, target_size=(256, 256)):
    img = cv2.imread(img_path)
    img = cv2.copyMakeBorder(img, top=50, bottom=50, left=50, right=50, borderType=cv2.BORDER_CONSTANT, value=[255,255,255])
    img = ut.cv.cvtColor(img, ut.cv.COLOR_BGR2GRAY)
    img_array = image.img_to_array(img)
    img_array_uint8 = img_array.astype(np.uint8)
    _, img_bin = cv2.threshold(img_array_uint8, 0, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)
    img_bin = 255-img_bin

    
    return img_bin


# sortowanie elementów
def sort(cnts):
    # sorotwanie rosnąco
    reverse = False
#     i = 1
   
    # construct the list of bounding boxes and sort them from top to
    # bottom
    #każdy odnaleziony kształt otocz prostokątem
    boundingBoxes = [cv2.boundingRect(c) for c in cnts]
#     połączenie listy konturów z listą prostokątów otaczjących(boundingBoxes)
#sortowanie wed lug wspórzednej y prostokąta rosnaco
    (cnts, boundingBoxes) = zip(*sorted(zip(cnts, boundingBoxes),
    key=lambda b:b[1][1], reverse=reverse))
    # return the list of sorted contours and bounding boxes
    return (cnts, boundingBoxes)

