import os
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, QSlider,QSizePolicy,QComboBox,QLineEdit
from PyQt5.QtCore import Qt, QSize,pyqtSignal
from PyQt5.QtGui import QPixmap,QImage
from natsort import natsorted

from stages.pre_processing import execute_main
from PIL import Image
import os

class PreprocessingWindow(QWidget):
    startSignal = pyqtSignal(str)  # Sygnał emitowany przy kliknięciu przycisku Start

    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent = parent  # referencja do głównego okna

        self.main_layout = QVBoxLayout()
        self.buttons_layout = QHBoxLayout()

        self.label = QLabel('Wybierz opcję i wprowadź współczynnik')
        self.label1 = QLabel('Przesuń suwak aby przeglądać zdjęcia')

        self.label.setAlignment(Qt.AlignCenter)
        self.label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        
        self.label1.setAlignment(Qt.AlignCenter)
        self.label1.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        self.options = QComboBox()
        self.options.addItems(['Normal','Otsu','Sauvola', 'Inverse'])

        self.coefficient = QLineEdit()
        self.coefficient.setPlaceholderText('Wprowadź współczynnik')

        self.start_button = QPushButton('Start')
        
        self.next_button = QPushButton('Dalej')
        self.next_button.setEnabled(False)  # Disable the button by default
        self.back_button = QPushButton('Cofnij')

        self.image_name_label = QLabel()
        self.image_name_label.setAlignment(Qt.AlignCenter)

        self.image_label = QLabel()
        self.image_label.setAlignment(Qt.AlignCenter)
        self.image_label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.image_label.setMinimumHeight(600)  # Set minimum height to 600 pixels
        self.image_label.setMinimumWidth(300)  # Set minimum QLabel width to 300 pixels

        self.slider = QSlider(Qt.Horizontal)
        self.slider.setTickPosition(QSlider.TicksBelow)
        self.slider.setTickInterval(1)
        self.slider.setMinimum(1)

        self.main_layout.addWidget(self.label)
        self.main_layout.addWidget(self.options)
        self.main_layout.addWidget(self.coefficient)
        self.main_layout.addWidget(self.start_button)
        
        self.buttons_layout.addWidget(self.back_button)
        self.buttons_layout.addWidget(self.next_button)
        self.main_layout.addLayout(self.buttons_layout)

        
        self.main_layout.addWidget(self.label1)


        self.main_layout.addWidget(self.image_label)
        self.main_layout.addWidget(self.slider)
        self.main_layout.addWidget(self.image_name_label)  # Add image name label to the layout

        self.setLayout(self.main_layout)

        self.next_button.clicked.connect(self.goNext)
        self.start_button.clicked.connect(self.startProcess)  # Connect the Start button to the startProcess function
        self.slider.valueChanged.connect(self.updateImage)  # Connect the slider value change to the updateImage function
        self.back_button.clicked.connect(self.goBack)
        self.image_files = self.getImageFiles()  # Get the list of image files

    def getImageFiles(self):
        images_folder = 'images_binarized'  # Folder with images
        image_files = natsorted([file for file in os.listdir(images_folder) if file.endswith('.jpg')])
        if image_files:
            self.slider.setMaximum(len(image_files) - 1)  # -1 because index starts from 0
            self.next_button.setEnabled(bool(image_files))

            return image_files

    def startProcess(self):
        selected_option = self.options.currentText()
        print(selected_option)
        coefficient = self.coefficient.text()
        # Perform processing with the selected option and coefficient
        execute_main(selected_option)
        self.image_files = self.getImageFiles()  # Get the list of image files
        
    def resizeEvent(self, event):
        super().resizeEvent(event)
        self.updateImage()
        
    def updateImage(self):
        image_index = self.slider.value()
        if self.image_files:
            if image_index < len(self.image_files):
                image_path = os.path.join('images_binarized', self.image_files[image_index])
                image = QImage(image_path)

                label_width = self.image_label.width()
                label_height = self.image_label.height()
                print(label_width,label_height)

                image_name = self.image_files[image_index]
                self.image_name_label.setText(image_name)  # Update image name label text

                self.image_name_label.setText(image_name)

                scaled_image = image.scaled(label_width, label_height)
                self.image_label.setPixmap(QPixmap.fromImage(scaled_image))
    
    def goBack(self):
        print(self.parent)
        # Code to go back to the previous state or screen
        self.parent.stackedWidget.setCurrentWidget(self.parent.infoWidget)
        self.parent.setWindowTitle('Data extraction')

    def goNext(self):
        # Code to go to the next state or screen
        self.parent.displaySegmentation()  # Dodane przekierowanie do okna preprocessing.


if __name__ == '__main__':
    app = QApplication([])
    window = PreprocessingWindow()
    window.show()
    app.exec()
