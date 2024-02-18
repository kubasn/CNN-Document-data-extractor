import cv2 as cv
import numpy as np
from matplotlib import pyplot as plt
import math
from pdf2image import convert_from_path
from skimage.filters import (threshold_otsu, threshold_sauvola)
from skimage.transform import hough_line
from sklearn.neighbors import kneighbors_graph
from collections import defaultdict  
from scipy.signal import find_peaks
import heapq


  
# zliczenie jaki procent obrazu pokrywa kolor zielony (funkcja użyta w printContours)
def color_percentage(image, target_color, tolerance=0):
    # Convert the target color to a NumPy array
    target_color = np.array(target_color, dtype=np.uint8)

    # Calculate the lower and upper bounds for the color range
    lower_bound = np.clip(target_color - tolerance, 0, 255)
    upper_bound = np.clip(target_color + tolerance, 0, 255)
    # Create a mask for the target color within the specified tolerance
    mask = cv.inRange(image, lower_bound, upper_bound)

    # Count the number of pixels of the target color
    target_color_pixel_count = np.sum(mask > 0)

    # Calculate the percentage
    total_pixels = image.shape[0] * image.shape[1]
    percentage = (target_color_pixel_count / total_pixels) * 100

    return percentage


def printContours(binarized_img,output_img, thickness,direction,orig,counter):
    '''
    znajduje kontury na binarnym obrazie, rysuje prostokąty wokół tych konturów, które spełniają określone warunki, 
    a następnie zapisuje wyodrębnione fragmenty obrazu na dysku
    
    Parametry
    ----------
    binarized_img : źródłowy obraz binarny. 
    output_img: obraz na którym zostaną narysiwane prostokąty.
    thickness: grubość pudełka
    kierunek wycinania 
    orig: oryginalny obraz z którego mają zostać wycięte fragmenty
    
    Zwraca
    -------
    box_coordinates: koordynaty oraz wymiary(x,y,w,h) wszystkich okienek które spełniają wymagania.
    '''
    IMAGE_EXTESION = '.png'
    out_path= "images_segmentation/"
    img_name=counter
    i=0
    #box_coordinates: Lista do przechowywania współrzędnych prostokątów
    box_coordinates = [] 
    contours,_  = cv.findContours(~binarized_img,cv.RETR_EXTERNAL,cv.CHAIN_APPROX_SIMPLE) 
    for contour in contours:
        #Znajdowanie konturów na binarnym obrazie
        [x,y,w,h] = cv.boundingRect(contour)
        # Sprawdzenie, czy kontur spełnia określone warunki dotyczące wymiarów
        if ((w >= 70*4 and h >= 60*4) or (w >= 70*4 and h >= 30*4))  and h/w<10:
            cv.rectangle(output_img, (x,y), (x+w,y+h), (0, 255, 0), thickness)
            pt1 = (x,y)
            pt2 = (x+w,y+h)
            color = (0, 255, 0)  # Green
            thickness = -1

            if(direction=='vert'):
                cover_percentage = color_percentage(orig[y:y + h, x:x + w], color, 0)
                if(cover_percentage<20.0):
                    cropped = orig[y:y + h, x:x + w]
                    save = cv.imwrite(out_path+'/'+str(counter)+'_'+str(i)+IMAGE_EXTESION, cropped)
                    cv.rectangle(orig, pt1, pt2, color, thickness)
            i=i+1
            #if (w >= 100 and h >= 50) or (w >= 50 and h >= 100):: Dodawanie współrzędnych prostokąta do listy box_coordinates, jeśli spełnia określone warunki dotyczące wymiarów.
        if (w >= 100*4 and h >= 50*4) or (w >= 50*4 and h >= 100*4):
            box_coordinates.append([x,y,w,h])
    #return box_coordinates: Zwracanie listy współrzędnych prostokątów.
    return box_coordinates
                    
def angleBetween(p1, p2):
    '''
        Funkcja  jest używana do obliczenia kąta między dwoma punktami w układzie współrzędnych kartezjańskich, a wynik jest zwracany w stopniach.
    
    Parametry
    ----------
    p1/2: para koordynatów x,y
    
    Zwraca
    -------
    angle: wartość kąta nachylenia(float)
    '''

    
    dX = p2[0] - p1[0]
    dY = p2[1] - p1[1]
    angle = math.degrees(math.atan2(dY, dX))
    return angle


# ważne
def getAngles(edges,points):
    '''
    oblicza kąt nachylenia lini przechodzącej przez dwa punkty na tablicy krawędzi
    
    Parametry
    ----------
    edges: indeksy pary punktów krawędzi 
    points: tablica koordynatów x,y
    
    Zwraca
    -------
    angles: tablica wartości kątów nachylenia
    '''
    angles = []
    for edge in edges:
        i,j = edge
        angle = angleBetween(points[i],points[j])
#Obliczenie kąta między punktami o indeksach i i j przy użyciu funkcji angleBetween i dodanie tego kąta do listy angles.
        angles.append(angle)
    return angles

# funkcja, która analizuje krawędzie przekazane jako argumenty (edges) i zwraca informacje o krawędziach poziomych i pionowych.
def edgesInformation(edges, points, distances):
    '''
    Metoda  docstrum, pośród listy krawędzi horyzontalnych i wertykalnych znajduje różnice +-20 by naprawić niedokładności kątów krawędzi
    
    
    Parametry
    ----------
    edges: lista krawędzi do analizy.
    points: lista punktów, które tworzą te krawędzie.
    distances: lista odległości między punktami tworzącymi krawędzie.
    
    Zwraca
    -------
    horizontal_edges: tablica par indeksów punktów tworzących krawędzie horyzontalne 
    vertical_edges: tablica par indeksów punktów tworzących krawędzie wertykalne 
    '''
    angles = getAngles(edges,points)
    points = np.int32(points)
    
#horizontal_edges: przechowuje krawędzie poziome.
#vertical_edges: przechowuje krawędzie pionowe.

    horizontal_edges =[]
    vertical_edges = []
    
    for i, angle in enumerate(angles):
    
#Funkcja iteruje przez wszystkie obliczone kąty (angles) i sprawdza, czy kąt jest bliski 0(180)(-+20 stopni) (dla krawędzi poziomych) lub bliski 90(-90)(+-20stopni) stopni (dla krawędzi pionowych). Jeśli kąt spełnia warunki, odpowiednia krawędź jest dodawana do odpowiedniej listy (horizontal_edges lub vertical_edges) wraz z kątem, odległością i współrzędnymi krawędzi.   
    
        edge = [edges[i][0], edges[i][1]]
        if -20 < angle < 20 or 160 < angle or angle < -160:
            horizontal_edges.append((angle, distances[i], edge))
        elif 70 < angle < 110 or (-70 > angle and angle > -110):
            vertical_edges.append((angle, distances[i], edge))
    
    return horizontal_edges,vertical_edges

  

# analizuje listę odległości między punktami krawędziami obrazu. Na podstawie tych odległości, funkcja znajduje dwie najczęściej występujące wartości odległości 
def findPeakValues(distances, distance):
    '''
    
    Parametry
    ----------
    distances - tablica wartości(float) reprezentująca odległości między dwoma punktami krawędzi 
    distance - wartość (int) użyta jako odległość pomiędzy pierwszym a drugim peak (opcjonalnie)
    Zwraca
    -------
    peak_values - integer values of best two peak distances
    '''
    
#     Tworzony jest słownik d za pomocą defaultdict(int), który będzie używany do zliczania wystąpień zaokrąglonych wartości odległości.
    d = defaultdict(int)
    
    for distance in distances:
        distance = round(distance)
        d[distance] += 1
        
    result = sorted(d.items(), key = lambda x:x[1], reverse=True)
    
    values = []
    occurrences = []
    for item in result:
        values.append(item[0])
        occurrences.append(item[1])

    x = np.array(values)
    y = np.array(occurrences)
    
    sort_id = np.argsort(x)
    x = x[sort_id]
    y = y[sort_id]

# Funkcja find_peaks ze scipy.signal jest używana do znalezienia lokalnych maksimów na wykresie. Jeśli opcjonalny parametr distance jest podany, używany jest jako odległość między szczytami.
    if distance!=0:
        peaks, _ = find_peaks(y, distance= distance)
    else:
        peaks, _ = find_peaks(y)


    peaks_occurrences = []
    for peak in peaks:
        peaks_occurrences.append((x[peak], y[peak]))
    peaks_occurrences = sorted(peaks_occurrences, key=lambda x: x[1], reverse=True)
    
    #znajdz dwa najwyższe peak's
    best_peaks = heapq.nlargest(2, peaks_occurrences, key=lambda x: x[1])
    

    peak_values = []
    for occurrence in peaks_occurrences:
        if len(peak_values) < 2 and occurrence in best_peaks:
            peak_values.append(int(occurrence[0]))
#     W rezultacie, funkcja zwraca dwie najczęściej występujące wartości odległości jako peak_values.
    return peak_values

# konwertowanie pliku PDF na obrazy
def pdf2img(pdf):
    pages = convert_from_path(pdf,300)
    for count, page in enumerate(pages):
      # Zapisanie stron PDF jako jpg
         page.save(f'images/{count}.jpg', 'JPEG')
#     print('images saved')
