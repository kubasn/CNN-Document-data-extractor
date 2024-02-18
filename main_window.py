from PyQt5.QtWidgets import QMainWindow, QApplication, QPushButton, QVBoxLayout, QWidget, QStackedWidget
from PyQt5.QtCore import Qt
from options_window import OptionsWindow  # Importujemy OptionsWindow z options_window.py
from info_window import InfoWindow  # nowy import
from preprocessing_window import PreprocessingWindow
from segmentation_window import SegmentationWindow
from classification_window import ClassificationWindow
from dataextraction_window import DataExtractionWindow

from stages.pre_processing import execute_main

from stages import utils


import sys

class MainWindow(QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()
        self.setWindowTitle("Data extraction")
        self.initUI()

    def initUI(self):
        # Tworzenie widgetów
        self.startButton = QPushButton('Start', self)
        self.startButton.setFixedSize(200, 100)
        self.startButton.clicked.connect(self.showInfo)  # przekierowanie do showInfo

        self.optionsButton = QPushButton('Opcje', self)
        self.optionsButton.setFixedSize(200, 100)
        self.optionsButton.clicked.connect(self.showOptionsWindow)

        # Tworzenie układu
        layout = QVBoxLayout()
        layout.addWidget(self.startButton, 0, Qt.AlignCenter)
        layout.addWidget(self.optionsButton, 0, Qt.AlignCenter)

        # Tworzenie widgetu centralnego
        self.mainWidget = QWidget()
        self.mainWidget.setLayout(layout)

        # Tworzenie widgetu z opcjami
        self.optionsWidget = OptionsWindow(self)
        self.infoWidget = InfoWindow(self)  
        self.preprocessingWidget = PreprocessingWindow(self)
        self.segmentationWidget = SegmentationWindow(self)
        self.classificationWidget = ClassificationWindow(self)
        self.dataExtractionWidget = DataExtractionWindow(self)


        # Widget
        self.stackedWidget = QStackedWidget()
        self.stackedWidget.addWidget(self.mainWidget)
        self.stackedWidget.addWidget(self.optionsWidget)
        self.stackedWidget.addWidget(self.infoWidget) 
        self.stackedWidget.addWidget(self.preprocessingWidget)
        self.stackedWidget.addWidget(self.segmentationWidget)
        self.stackedWidget.addWidget(self.classificationWidget)
        self.stackedWidget.addWidget(self.dataExtractionWidget)


        # Ustawianie QStackedWidget jako centralnego widgetu
        self.setCentralWidget(self.stackedWidget)

        self.setGeometry(300, 300, 800, 600)
#         self.setWindowTitle('Główne okno')    
        self.show()
    

    def showOptionsWindow(self):
        # Przełączanie na stronę z opcjami
        self.stackedWidget.setCurrentWidget(self.optionsWidget)
        self.setWindowTitle('Opcje')

    
    def showInfo(self):
        self.stackedWidget.setCurrentWidget(self.infoWidget)  # zmieniamy widok na infoWidget
        self.setWindowTitle('Informacje')
        
    def displayPreprocessing(self):
        self.stackedWidget.setCurrentWidget(self.preprocessingWidget)
        self.setWindowTitle('Preprocessing')  # Zmiana tytułu okna
    
    def displaySegmentation(self):
        self.stackedWidget.setCurrentWidget(self.segmentationWidget)
        self.setWindowTitle('Segmentation')  # Zmiana tytułu okna
        
    def displayClassification(self):
        self.stackedWidget.setCurrentWidget(self.classificationWidget)
        self.setWindowTitle('Classification')  # Zmiana tytułu okna
        
    def displayDataExtraction(self):
        self.stackedWidget.setCurrentWidget(self.dataExtractionWidget)
        self.setWindowTitle('Data extraction')  # Zmiana tytułu okna
        

def main():
    app = QApplication(sys.argv)
    ex = MainWindow()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()