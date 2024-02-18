import numpy as np
import utils as ut
import os
from os import listdir
import cv2
from utils import *
from layoutAnalysis import *


def execute_main():
#     pdf_file = '../pdf/Mikrostruktury-58.pdf'
#     ut.pdf2img(pdf_file)
    
    images_folder = 'images'
    images_binarized_folder = 'images_binarized'

# licznik do zliczania ile obszarów odnaleziono na obrazie

    for img_file in os.listdir(images_folder):
        if img_file.endswith(".jpg"):
#             print(img_file,counter)
            counter = int(img_file.split('.')[0])
            file_path = os.path.join(images_folder, img_file)
#             image_processing(file_path, counter)
#             binarized_img = cv2.imread(file_path)
            segmentation_func(file_path,counter)
    
    
#              page.save(f'images/{count}.jpg', 'JPEG')

    
    
    
def segmentation_func(input_path,img_counter):    
    print(input_path)
    print(f'images_binarized/{img_counter}.jpg')

    source_img = cv2.imread(input_path)
    original = source_img.copy()
    binarized_img = cv2.imread(f'images_binarized/{img_counter}.jpg')
    binarized_img = cv2.cvtColor(binarized_img, cv2.COLOR_BGR2GRAY)
    


# Utworzenie kilku kopii obrazu, które będą modyfikowane w trakcie przetwarzania.
#     binarized_img = source_img.copy()
    
    img_copy1 = binarized_img.copy()
    binary_img1 = binarized_img.copy()
    binary_img2 = binarized_img.copy()


    centroid_points = findCenterPoints(binary_img1, binary_img1)
    k_nearest_graph = nearestNeighborGraph(centroid_points, 5)
    k_nearest_edges = np.array(k_nearest_graph.nonzero()).T
    k_nearest_distances = k_nearest_graph.data
    peak_values = findPeakValues(k_nearest_distances, 20)
    hor_edges, ver_edges = edgesInformation(k_nearest_edges, centroid_points, k_nearest_distances)

    drawDocstrumEdges(binary_img2, hor_edges, centroid_points, max(peak_values))

    printContours(binary_img2, img_copy1, 3, 'vert', original, img_counter)