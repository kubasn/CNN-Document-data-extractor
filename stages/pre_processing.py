import numpy as np
import utils as ut
import os
from os import listdir
import cv2


def execute_main(selected_option):
    print('ello')
    pdf_directory = 'pdf'
    pdf_files = [f for f in os.listdir(pdf_directory) if f.endswith('.pdf')]
    print(pdf_files)
    if pdf_files:
        pdf_file = os.path.join(pdf_directory, pdf_files[0])
        ut.pdf2img(pdf_file)
    else:
        print("No PDF files found in the directory.")
    
    images_folder = 'images'
# licznik do zliczania ile obszarów odnaleziono na obrazie

    for img_file in os.listdir(images_folder):
        if img_file.endswith(".jpg"):
#             print(img_file,counter)
            counter = int(img_file.split('.')[0])
            file_path = os.path.join(images_folder, img_file)
#             image_processing(file_path, counter)
            source_img = cv2.imread(file_path)
            binarized_img = binImg( source_img,selected_option)
            binarized_img = removeFiguresOrSpots(binarized_img, 'linesBoth')
            binarized_img = removeFiguresOrSpots(binarized_img, 'spots')
            cv2.imwrite(f'images_binarized/{counter}.jpg', binarized_img)

#             page.save(f'images/{count}.jpg', 'JPEG')



def binImg(img,mode):
    '''
    Binaryzacja - można wybrać jedną z metod
    
    Parametry
    ----------
    image- obraz źródłowy, obraz kolorowy przekształca się wcześniej na szary
    mode - określa rodzaj binaryzacji

    Zwraca
    -------
    obraz po binaryzacji
    '''
    if img.ndim > 2:
        img = ut.cv.cvtColor(img, ut.cv.COLOR_BGR2GRAY)

    binarization_methods = {
        'Otsu': lambda img: ut.binarize(img, ut.threshold_otsu(img)) * 255,
        'Normal': lambda img: ut.cv.threshold(img, 242, 255, ut.cv.THRESH_BINARY)[1],
        'Sauvola': lambda img: ut.binarize(img, ut.threshold_sauvola(img)) * 255,
        'Inverse': lambda img: ut.cv.threshold(img, 242, 255, ut.cv.THRESH_BINARY_INV)[1]
    }

    return binarization_methods[mode](img)

    
def removeFiguresOrSpots(binarized_img, mode):
    '''
    *usunięcie artefaktów, linii, kropek itd...
    
    Parametry
    ----------
    binarized_img - obraz źródłowy binarny
    mode - co chemy usunąć

    Zwaraca
    -------
    new_img - obraz po usunięciu elementów
    '''
    if mode != 'figures':
        kernel = np.ones((3,2), np.uint8) 
        binarized_img = ut.cv.dilate(~binarized_img, kernel, iterations=1)
        binarized_img = ut.cv.erode(binarized_img, kernel, iterations=1)
        binarized_img = ~binarized_img
    new_img = binarized_img.copy()
    if new_img.ndim >2:
        new_img = ut.cv.cvtColor(new_img, ut.cv.COLOR_BGR2GRAY)
    contours,_ = ut.cv.findContours(~binarized_img, ut.cv.RETR_EXTERNAL, ut.cv.CHAIN_APPROX_NONE)
    

    
# - Tryb 'figures': Usuwa obszary, które są zbyt duże (szerokość lub wysokość większa niż 250 pikseli).
# - Tryb 'spots': Usuwa obszary o niewielkich wymiarach (szerokość i wysokość mniejsze lub równe 5 pikseli).
# - Tryb 'linesVert': Usuwa obszary reprezentujące pionowe linie (wysokość większa niż 100 pikseli i szerokość mniejsza niż 30 pikseli).
# - Tryb 'linesHoriz': Usuwa obszary reprezentujące poziome linie (szerokość większa niż 100 pikseli i wysokość mniejsza niż 30 pikseli).
# - Tryb 'linesBoth': Usuwa obszary reprezentujące zarówno pionowe, jak i poziome linie.
    
    def remove_area(x, y, w, h):
        for i in range(y, y + h):
            for j in range(x, x + w):
                new_img[i][j] = 255

    def figures():
        if w > 250 or h > 250:
            remove_area(x, y, w, h)

    def spots():
        if 0 <= w <= 10 and 0 <= h <= 10:
            remove_area(x, y, w, h)

    def linesVert():
        if h > 100 and w < 30:
            remove_area(x, y, w, h)

    def linesHoriz():
        if w > 100 and h < 30:
            remove_area(x, y, w, h)

    def linesBoth():
        if (w > 150 and h < 40) or (h > 150 and w < 40):
            remove_area(x, y, w, h)

    mode_switch = {
        'figures': figures,
        'spots': spots,
        'linesVert': linesVert,
        'linesHoriz': linesHoriz,
        'linesBoth': linesBoth
    }

    for contour in contours:
        x, y, w, h = ut.cv.boundingRect(contour)
        mode_switch.get(mode, lambda: None)()
    

                        
    return new_img