from PyQt5.QtWidgets import QPushButton, QLabel, QVBoxLayout, QWidget

class OptionsWindow(QWidget):
    def __init__(self, parent):
        super().__init__()
        
        self.parent = parent  # referencja do głównego okna

        self.backButton = QPushButton('Powrót', self)
        self.backButton.clicked.connect(self.goBack)

        layout = QVBoxLayout()
        label = QLabel('Tutaj znajdą się opcje')
        layout.addWidget(label)
        layout.addWidget(self.backButton)

        self.setLayout(layout)

    def goBack(self):
        # Przełączanie z powrotem na główny widok
        self.parent.stackedWidget.setCurrentWidget(self.parent.mainWidget)
        self.parent.setWindowTitle('Data extraction')
