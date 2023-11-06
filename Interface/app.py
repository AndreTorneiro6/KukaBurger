import os
import sys

from PyQt5.QtCore import QSize
from PyQt5.QtWidgets import QApplication, QMainWindow, QDesktopWidget, QPushButton

CURRENT_DIR = "/home/andretorneiro/Desktop/Robotica/KukaCooker/Interface/assets"


# Subclass QMainWindow to customize your application's main window
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("My App")

        self.setFixedSize(QSize(1280, 720))

        qr = self.frameGeometry()
        cp = QDesktopWidget().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())

        # Set the central widget of the Window.
        # self.setCentralWidget(button)
        self.setStyleSheet(
            """
            QMainWindow{
                border-image: url(%s) 0 0 0 0 stretch stretch
            }
            """
            % os.path.join(CURRENT_DIR, "Background.jpeg")
        )

        orderButton = QPushButton("Order Here", self)
        orderButton.setStyleSheet('background-color: orange;' 'border-radius:4;' "font:Bold;"
                           "font-family:Georgia;" "font-size:22px;")
        # orderButton.adjustSize()

        orderButton.resize(150,32)
        orderButton.move(570,640)
        orderButton.clicked.connect(self.orderHere)

    def orderHere(self):
        print('hello')





        # oImage = QtGui.QImage('/Background.jpeg')
        # sImage= oImage.scaled(QtCore.QSize(440, 280))
        # palette = QPalette()
        # palette.setBrush(QPalette.Window, QBrush(sImage))
        # self.setPalette(palette)


app = QApplication(sys.argv)

window = MainWindow()
window.show()

app.exec()
