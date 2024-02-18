from PyQt5.QtWidgets import QPushButton, QLabel, QVBoxLayout, QHBoxLayout, QWidget
from PyQt5.QtCore import Qt

class InfoWindow(QWidget):
    def __init__(self, parent):
        super().__init__()

        self.parent = parent  # referencja do głównego okna

        self.startButton = QPushButton('Start', self)
#         self.startButton.setStyleSheet("background-color: green; color: #F0F0F2; border-radius: 10px;")  # Zmieniamy kolor na zielony
        self.startButton.clicked.connect(self.startProcess)

        self.backButton = QPushButton('Cofnij', self)  # nowy przycisk
        self.backButton.clicked.connect(self.goBack)  # funkcja goBack

        # Utwórz QHBoxLayout dla przycisków
        buttonsLayout = QHBoxLayout()
        buttonsLayout.addWidget(self.startButton)
        buttonsLayout.addWidget(self.backButton)
        
        layout = QVBoxLayout()
        label = QLabel('Przed uruchomieniem programu, upewnij się, że umieściłeś plik PDF w katalogu pdf.')
        label.setAlignment(Qt.AlignCenter)  # Wycentrowanie tekstu

        # Dodaj etykietę i układ przycisków do głównego układu
        layout.addWidget(label)
        layout.addLayout(buttonsLayout)

        self.setLayout(layout)

    def startProcess(self):
        # Tutaj umieść kod, który ma zostać uruchomiony po naciśnięciu przycisku Start.
        self.parent.displayPreprocessing()  # Dodane przekierowanie do okna preprocessing.

    def goBack(self):
        # Funkcja do powrotu do głównego widoku
        self.parent.stackedWidget.setCurrentWidget(self.parent.mainWidget)
        self.parent.setWindowTitle('Data extraction')
