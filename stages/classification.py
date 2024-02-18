import tensorflow as tf
from tensorflow import keras
from tensorflow.keras.preprocessing import image
import numpy as np
import matplotlib.pyplot as plt
from PIL import Image, ImageOps
from tensorflow.keras.models import load_model
import utils as ut
import cv2
import os

# model_path = '../modele/model_params_05_07_najlepszy.h5'
model_path = '../model_params.h5'
model = load_model(model_path)
folder_path = 'images_segmentation'
image_extensions = ['.jpg', '.jpeg', '.png', '.bmp']
class_labels = ['image', 'table', 'text']


def execute_main():
    recognize(folder_path)


def load_and_preprocess_image(img_path, target_size=(256, 256)):
    img = image.load_img(img_path, target_size=target_size)
    img = ImageOps.grayscale(img)


    img_array = image.img_to_array(img)
    img_array = np.expand_dims(img_array, axis=0)
    img_array /= 255.
    return img_array



def recognize(path):
    image_files = [f for f in os.listdir(path) if any(f.lower().endswith(ext) for ext in image_extensions)]
    counter = 1
    for img_file in image_files:
        img_path = os.path.join(folder_path, img_file)
        img_array = load_and_preprocess_image(img_path)
        predictions = model.predict(img_array)
        predicted_class_idx = np.argmax(predictions)
        predicted_class_label = class_labels[predicted_class_idx]
        predicted_class_probability = predictions[0][predicted_class_idx] * 100
#         print(f"Predicted Class: {predicted_class_label} ({predicted_class_probability:.2f}%)")
#         if(predicted_class_label == 'table'):
        img = image.load_img(img_path)
#         cv2.imwrite(f'images_classification/{predicted_class_label}_{counter}.jpg', img)
        img.save(f'images_classification/{predicted_class_label}_{counter}.jpg')
        counter = counter+1
    
    


