import os
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, QSlider,QSizePolicy,QComboBox,QLineEdit
from PyQt5.QtCore import Qt, QSize,pyqtSignal
from PyQt5.QtGui import QPixmap,QImage
from natsort import natsorted

from stages.classification import execute_main
from PIL import Image
import os


class ClassificationWindow(QWidget):
    startSignal = pyqtSignal(str)  # Sygnał emitowany przy kliknięciu przycisku Start

    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent = parent  # referencja do głównego okna

        self.main_layout = QVBoxLayout()
        self.buttons_layout = QHBoxLayout()
        
        self.class_input = QLineEdit()
        self.class_input.setPlaceholderText('Klasa zdjęcia')
        self.rename_button = QPushButton('Zmień typ')
        

        self.label = QLabel('W poniższym polu możesz poprawić typ obszaru (podaj jedną z wartości: text,image,table)')
        self.label1 = QLabel('Przesuń suwak aby przeglądać zdjęcia')
        self.rotate_button = QPushButton('Obróć zdjęcie')  # Dodaj przycisk do interfejsu

        self.label.setAlignment(Qt.AlignCenter)
        self.label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        
        self.label1.setAlignment(Qt.AlignCenter)
        self.label1.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

    
        self.start_button = QPushButton('Start')
        self.next_button = QPushButton('Dalej')
        self.next_button.setEnabled(False)  # Disable the button by default
        self.back_button = QPushButton('Cofnij')
        
        self.delete_button = QPushButton('Usuń zdjęcie')

        self.image_name_label = QLabel()
        self.image_name_label.setAlignment(Qt.AlignCenter)

        self.image_label = QLabel()
        self.image_label.setAlignment(Qt.AlignCenter)
        self.image_label.setMinimumHeight(600)  # Set minimum height to 600 pixels
        self.image_label.setMinimumWidth(300)  # Set minimum QLabel width to 300 pixels
        
   

        self.slider = QSlider(Qt.Horizontal)
        self.slider.setTickPosition(QSlider.TicksBelow)
        self.slider.setTickInterval(1)
        self.slider.setMinimum(1)

  

        self.main_layout.addWidget(self.start_button)
        

        
        self.buttons_layout.addWidget(self.back_button)
        self.buttons_layout.addWidget(self.next_button)
        self.main_layout.addLayout(self.buttons_layout)

        self.main_layout.addWidget(self.label1)


        self.main_layout.addWidget(self.image_label)
        self.main_layout.addWidget(self.slider)
        self.main_layout.addWidget(self.image_name_label)  # Add image name label to the layout
        self.main_layout.addWidget(self.label)
        self.main_layout.addWidget(self.class_input)
        self.main_layout.addWidget(self.rename_button)
        self.main_layout.addWidget(self.rotate_button)
        self.main_layout.addWidget(self.delete_button)
        self.setLayout(self.main_layout)

        self.delete_button.clicked.connect(self.deleteImage)  # Connect the button to the deleteImage function
        self.next_button.clicked.connect(self.goNext)
        self.start_button.clicked.connect(self.startProcess)  # Connect the Start button to the startProcess function
        self.slider.valueChanged.connect(self.updateImage)  # Connect the slider value change to the updateImage function
        self.back_button.clicked.connect(self.goBack)
        self.rename_button.clicked.connect(self.renameImage)  # Connect the button to the renaming function
        self.rotate_button.clicked.connect(self.rotateImage)  # Połącz przycisk z funkcją obracającą obraz

        self.image_files = self.getImageFiles()  # Get the list of image files

    def getImageFiles(self):
        images_folder = 'images_classification'  # Folder with images
        image_files = natsorted([file for file in os.listdir(images_folder) if file.endswith('.jpg')])
        if image_files:
            self.slider.setMaximum(len(image_files) - 1)  # -1 because index starts from 0
            self.next_button.setEnabled(bool(image_files))

            return image_files
        
        
    def rotateImage(self):
        image_index = self.slider.value()
        if self.image_files:
            image_path = os.path.join('images_classification', self.image_files[image_index])
            
            image = Image.open(image_path)
            image = image.rotate(90, expand=True)  # Obróć obraz o 90 stopni
            image.save(image_path)  # Zapisz obrócony obraz
            
            self.updateImage()  # Odśwież wyświetlany obraz        

    def startProcess(self):
        # Perform processing with the selected option and coefficient
        execute_main()
        self.image_files = self.getImageFiles()  # Get the list of image files
        
    def resizeEvent(self, event):
        super().resizeEvent(event)
        self.updateImage()
        
        
    def updateImage(self):
        image_index = self.slider.value()
        if self.image_files:
            if image_index < len(self.image_files):
                image_path = os.path.join('images_classification', self.image_files[image_index])
                image = QImage(image_path)

                window_width = self.width()
                window_height = self.height()

                image_name = self.image_files[image_index]
                self.image_name_label.setText(image_name)  # Update image name label text
                class_name = image_name.split("_")[0] 
                self.class_input.setPlaceholderText(class_name)  # Set the placeholder to the image class

                scaled_image = image.scaledToWidth(window_width - 20)
                if scaled_image.height() > window_height - 200:
                    scaled_image = image.scaledToHeight(window_height - 200)

                self.image_label.setPixmap(QPixmap.fromImage(scaled_image))
    
    
    def goBack(self):
        print(self.parent)
        # Code to go back to the previous state or screen
        self.parent.stackedWidget.setCurrentWidget(self.parent.segmentationWidget)
        self.parent.setWindowTitle('Segmentation')

    def goNext(self):
        self.parent.displayDataExtraction()  # Dodane przekierowanie do okna preprocessing.


    def renameImage(self):
        new_class = self.class_input.text()
        image_index = self.slider.value()
        if self.image_files and new_class:
            old_image_path = os.path.join('images_classification', self.image_files[image_index])
            new_image_path = os.path.join('images_classification', f"{new_class}_{image_index}.jpg")  # or whatever your numbering system is
            os.rename(old_image_path, new_image_path)
            self.image_files[image_index] = f"{new_class}_{image_index}.jpg"  # Update the list of image files with the new name
            self.updateImage()  # Refresh the displayed image and class

            
    def deleteImage(self):
        image_index = self.slider.value()
        if self.image_files:
            image_path = os.path.join('images_classification', self.image_files[image_index])
            os.remove(image_path)  # Delete the image file
            self.image_files.pop(image_index)  # Remove the image from the list
            self.slider.setMaximum(len(self.image_files) - 1)  # Update the slider maximum
            self.updateImage()  # Refresh the displayed image           
            

if __name__ == '__main__':
    app = QApplication([])
    window = PreprocessingWindow()
    window.show()
    app.exec()