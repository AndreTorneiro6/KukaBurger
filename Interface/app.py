import sys

sys.path.append('/home/raspad/Desktop/KukaCooker')

import os
import cv2
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtMultimedia import *
import json
import threading

from segmentation.test.unique_test import *
from segmentation.find_cont import *
from segmentation.segment_ingredients import segmentation, index_items

from peripheral.control import send_data_to_thread, play_song
from peripheral.control_aux import pi_thread
from robot.connection import read_robot, write_robot, send_gripper_orientation

CURRENT_DIR = "/home/raspad/Desktop/KukaCooker/Interface/assets/"

data = list()

menuID = None
calibrate = False
count = 0


###############################################################################################################
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("My App")
        self.setFixedSize(1280, 740)
        #         self.center_window()

        background_image = os.path.join(CURRENT_DIR, "Background.jpeg")
        if os.path.exists(background_image):
            self.setStyleSheet(
                """
                QMainWindow{
                    border-image: url(%s) 0 0 0 0 stretch stretch
                }
                """ % background_image
            )
        order_button = QPushButton("Order Here", self)
        order_button.setStyleSheet(
            'background-color: orange;' 'border-radius: 4;' "font: Bold;" "font-family: Georgia;" "font-size: 22px;"
        )
        order_button.resize(150, 32)
        order_button.move(570, 600)
        order_button.clicked.connect(self.order_here)

        config_button = QPushButton(self)
        config_button.setStyleSheet(
            'background-color: None;' 'border-radius: 4;''   text-align: center;'
        )
        config_button.setIcon(QIcon(os.path.join(CURRENT_DIR, "gear.jpeg")))
        config_button.setIconSize(QSize(50, 50))

        config_button.resize(50, 50)
        config_button.move(1208, 110)
        config_button.clicked.connect(self.change_config)

        self.media_player = QMediaPlayer()
        audio_file_path = os.path.join(CURRENT_DIR, "audio.mpeg")
        media_content = QMediaContent(QUrl.fromLocalFile(audio_file_path))
        self.media_player.setMedia(media_content)
        self.media_player.mediaStatusChanged.connect(self.on_media_status_changed)

        self.w = OrderWindow()

    def center_window(self):
        qr = self.frameGeometry()
        cp = QDesktopWidget().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())

    def order_here(self):
        global calibrate
        if calibrate == True:
            self.media_player.play()
        else:
            QMessageBox.information(self, "Aguarde", "Calibracao por fazer")
            result = QMessageBox.Ok

            if result == 1024:
                self.change_config()

    def on_media_status_changed(self, status):
        if status == QMediaPlayer.EndOfMedia:
            self.w.show()
            self.close()

    def change_config(self):
        self.config_instance = Config_Window()
        self.config_instance.show()


###############################################################################################################

class Config_Window(QDialog):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Config Window")
        self.setFixedSize(500, 200)

        button_layout = QHBoxLayout()

        do_button = QPushButton("Perform Alterations", self)
        do_button.setStyleSheet(
            'background-color: orange;' 'border-radius: 4;' "font: Bold;" "font-family: Georgia;" "font-size: 16px;"
        )
        do_button.setFixedSize(200, 50)
        do_button.clicked.connect(self.on_do_button_clicked)

        register_button = QPushButton("Register Alterations", self)
        register_button.setStyleSheet(
            'background-color: orange;' 'border-radius: 4;' "font: Bold;" "font-family: Georgia;" "font-size: 16px;"
        )
        register_button.setFixedSize(200, 50)
        register_button.clicked.connect(self.on_register_button_clicked)
        button_layout.addWidget(do_button)
        button_layout.addWidget(register_button)

        self.setLayout(button_layout)

        # Initialize values as an instance variable
        self.values = []
        # Initialize register_dialog as an instance variable
        self.register_dialog = None

    def on_do_button_clicked(self):
        QMessageBox.information(self, "Aguarde", "Realizando alterações. Por favor, aguarde...")

    def on_register_button_clicked(self):
        ip_cam_address = '172.21.84.100:8080'

        # Cria uma nova janela com um GIF e abre a câmera
        self.register_dialog = QDialog(self)
        self.register_dialog.setWindowTitle("Registro de Alterações")
        self.register_dialog.setFixedSize(800, 600)

        # Cria o QStackedWidget para alternar entre o GIF e a câmera
        stacked_widget = QStackedWidget()

        # Adiciona um QLabel para exibir o GIF
        gif_label = QLabel()
        movie = QMovie(os.path.join(CURRENT_DIR, "wait.gif"))
        gif_label.setMovie(movie)
        gif_label.setAlignment(Qt.AlignCenter)
        movie.start()
        stacked_widget.addWidget(gif_label)

        # Adiciona uma QLabel para exibir a câmera
        self.camera_label = QLabel()
        self.camera_label.setAlignment(Qt.AlignCenter)  # Configura o alinhamento para o centro
        stacked_widget.addWidget(self.camera_label)

        # Configura a função de atualização do frame
        def show_camera():
            self.init_camera(ip_cam_address)
            qimage = self.convert_numpy_to_qimage()  # Converte a imagem OpenCV para QImage
            pixmap = QPixmap.fromImage(qimage)
            self.camera_label.setPixmap(pixmap)  # Exibe a imagem no QLabel
            stacked_widget.setCurrentIndex(1)

        QTimer.singleShot(2000, show_camera)  # Altera para a câmera após 2000 ms

        # Configura o layout da janela
        layout = QVBoxLayout()
        layout.addWidget(stacked_widget)

        # Create a confirm button
        confirm_button = QPushButton("Confirmar", self.register_dialog)
        confirm_button.setStyleSheet(
            'background-color: green;' 'border-radius: 4;' "font: Bold;" "font-family: Georgia;" "font-size: 16px;"
        )
        confirm_button.setFixedSize(200, 50)
        confirm_button.clicked.connect(self.on_confirm_button_clicked)

        # Add the confirm button to the layout
        layout.addWidget(confirm_button, alignment=Qt.AlignCenter)

        self.register_dialog.setLayout(layout)

        self.register_dialog.exec_()

    def on_confirm_button_clicked(self):
        global calibrate

        self.send_robot_initials()
        calibrate = True

        send_data_to_thread({"type": 'coords', "centroids": self.values, "dist": self.dist})

        self.close()

        # Optionally, close the dialog programmatically
        self.register_dialog.accept()

    def send_robot_initials(self):
        # grip coords for robot
        send_gripper_orientation(orientation='right', grip_base='R', index=1)
        send_gripper_orientation(orientation='left', grip_base='L', index=2)
        send_gripper_orientation(orientation='front', grip_base='F', index=3)
        #
        #         # Pos lavar pata + pano
        write_robot('KB_WashCoords[1]', '{FRAME: X 55, Y 95, Z 0, A 80, B 0, C -178}')
        write_robot('KB_WashCoords[2]', '{FRAME: X 155, Y 70, Z 0, A 80, B 0, C -178}')

    def init_camera(self, ip_cam_address):
        # Inicializa a câmera IP
        self.values = None  # Clear values before populating
        self.dist = None
        url = f"http://{ip_cam_address}/shot.jpg"
        img_resp = requests.get(url)
        img_arr = np.array(bytearray(img_resp.content), dtype=np.uint8)
        self.img = cv2.imdecode(img_arr, -1)  # Agora self.img está definido

        
#         self.dist = find_distance(self.img)

        ingredients = ['tomatoHSVRange', 'breadBHSVRange', 'breadTHSVRange', 'cheeseHSVRange', 'burgerHSVRange',
                       'onionHSVRange', 'lettuceHSVRange']
        values_aux = []
        for ingredient in ingredients:
            centroid, y = segmentation(self.img, ingredient)
            values_aux.append((centroid, ingredient, y))

        self.values = index_items(values_aux, self.img)

    def convert_numpy_to_qimage(self):
        # Converte a imagem OpenCV para QImage
        height, width, channel = self.img.shape
        bytes_per_line = 3 * width
        q_image = QImage(self.img.data, width, height, bytes_per_line, QImage.Format_RGB888)
        return q_image.rgbSwapped()


###############################################################################################################
class OrderWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Order Menu")
        self.setFixedSize(1280, 740)

        main_layout = QHBoxLayout()
        # Criar e adicionar o layout para cada imagem e botão
        main_layout.addLayout(self.create_image_button_layout("frango.jpeg", "Hamburguer Frango"))
        main_layout.addLayout(self.create_image_button_layout("veg.jpeg", "Hamburguer Vegetariano"))
        main_layout.addLayout(self.create_image_button_layout("burger.jpeg", "Hamburguer Normal"))

        back_button = QPushButton(self)
        back_button.setStyleSheet(
            'background-color: orange;'
            'border-radius: 4;'
            "font: Bold;"
            "font-family:"
            " Georgia;"
            "font-size: 15px;"
            'padding: 10px;'
            ""

        )
        back_button.setIcon(QIcon(os.path.join(CURRENT_DIR, "back.jpeg")))
        # Defina o tamanho desejado para o botão
        back_button.setFixedSize(50, 50)
        back_button.move(10, 10)

        back_button.clicked.connect(lambda: self.go_back())

        # Centralizar cada QVBoxLayout
        central_layout = QVBoxLayout()
        central_layout.addStretch(1)
        central_layout.addLayout(main_layout)
        central_layout.addStretch(1)

        self.setLayout(central_layout)

    def create_image_button_layout(self, image_filename, burger_type):
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        label = QLabel(self)
        img_path = os.path.join(CURRENT_DIR, image_filename)
        pixmap = QPixmap(img_path)
        pixmap = pixmap.scaledToWidth(200)  # Ajuste a largura desejada
        pixmap = pixmap.scaledToHeight(200)  # Ajuste a altura desejada
        label.setPixmap(pixmap)
        label.setAlignment(Qt.AlignCenter)

        button = QPushButton(burger_type, self)
        button.setStyleSheet(
            'background-color: orange;'
            'border-radius: 4;'
            "font: Bold;"
            "font-family: Georgia;"
            "font-size: 15px;"
            "margin-bottom: 50px;"
            'padding: 10px;'
        )
        button.clicked.connect(lambda: self.show_menu_or_burger(burger_type))
        layout.addWidget(label)
        layout.addWidget(button)

        return layout

    def show_menu_or_burger(self, burger_type):
        menu_or_burger_window = MenuOrBurger(burger_type)
        menu_or_burger_window.show()
        self.close()

    def go_back(self):
        window.show()
        self.close()


###############################################################################################################
class MenuOrBurger(QWidget):
    def __init__(self, burger_type):
        super().__init__()
        self.setWindowTitle("Order Menu")
        self.setFixedSize(1280, 740)

        main_layout = QHBoxLayout()

        if burger_type == "Hamburguer Frango":
            menuID = 4
            main_layout.addLayout(
                self.create_image_button_layout("menu_frango.jpeg", "Combine Em Menu", burger_type, menuID))
        elif burger_type == "Hamburguer Vegetariano":
            menuID = 6
            main_layout.addLayout(
                self.create_image_button_layout("menu_veg.jpeg", "Combine Em Menu", burger_type, menuID))
        elif burger_type == "Hamburguer Normal":
            menuID = 2
            main_layout.addLayout(
                self.create_image_button_layout("menu_carne.jpeg", "Combine Em Menu", burger_type, menuID))

        if burger_type == "Hamburguer Frango":
            menuID = 3
            main_layout.addLayout(
                self.create_image_button_layout("frango.jpeg", "Apenas Hamburguer", burger_type, menuID))
        elif burger_type == "Hamburguer Vegetariano":
            menuID = 5
            main_layout.addLayout(self.create_image_button_layout("veg.jpeg", "Apenas Hamburguer", burger_type, menuID))
        elif burger_type == "Hamburguer Normal":
            menuID = 1
            main_layout.addLayout(
                self.create_image_button_layout("burger.jpeg", "Apenas Hamburguer", burger_type, menuID))

        back_button = QPushButton(self)
        back_button.setStyleSheet(
            'background-color: orange;'
            'border-radius: 4;'
            "font: Bold;"
            "font-family:"
            " Georgia;"
            "font-size: 15px;"
            'padding: 10px;'

        )
        back_button.setIcon(QIcon(os.path.join(CURRENT_DIR, "back.jpeg")))
        # Defina o tamanho desejado para o botão
        back_button.setFixedSize(50, 50)
        back_button.move(10, 10)
        back_button.clicked.connect(lambda: self.go_back())

        central_layout = QVBoxLayout()
        central_layout.addStretch(1)
        central_layout.addLayout(main_layout)
        central_layout.addStretch(1)

        self.setLayout(central_layout)

    def create_image_button_layout(self, image_filename, button_text, burger_type, menuID):
        # Criar QLabel para a imagem
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        menu_image = QLabel(self)
        img_path = os.path.join(CURRENT_DIR, image_filename)
        pixmap = QPixmap(img_path)
        pixmap = pixmap.scaledToWidth(250)  # Ajuste a largura desejada
        pixmap = pixmap.scaledToHeight(250)  # Ajuste a altura desejada
        menu_image.setAlignment(Qt.AlignCenter)
        menu_image.setPixmap(pixmap)
        layout.addWidget(menu_image)

        button = QPushButton(button_text, self)
        button.setStyleSheet(
            'background-color: orange;'
            'border-radius: 4;'
            "font: Bold;"
            "font-family: Georgia;"
            "font-size: 15px;"
            'padding: 10px;'
        )
        if button_text == "Apenas Hamburguer":
            button.clicked.connect(lambda: self.show_checkbox_window(img_path, burger_type, button_text, menuID))

        else:
            button.clicked.connect(lambda: self.show_checkbox_window(img_path, burger_type, button_text, menuID))

        layout.addWidget(button)

        return layout

    def show_checkbox_window(self, burger_path, burger_type, button_text, menuID):
        checkbox_window = BurgerEditor(burger_path, burger_type, button_text, menuID)
        checkbox_window.show()
        self.close()

    def go_back(self):
        _instance = OrderWindow()
        _instance.show()
        self.close()


###############################################################################################################
class BurgerEditor(QDialog):
    def __init__(self, burger_path, burger_type, button_text, menuID):
        super().__init__()
        self.setWindowTitle("Escolha suas opções")
        self.setFixedSize(1280, 740)

        overall_layout = QVBoxLayout()
        main_layout = QVBoxLayout()
        main_layout.setSpacing(0)
        main_layout.setContentsMargins(0, 0, 0, 0)

        if button_text == "Apenas Hamburguer":
            main_layout.addLayout(self.create_image_with_text_below(burger_path, burger_type, menuID))
        elif button_text == "Combine Em Menu":
            if burger_type == "Hamburguer Frango":
                main_layout.addLayout(self.create_image_with_text_below("menu_frango.jpeg", burger_type, menuID))
            elif burger_type == "Hamburguer Vegetariano":
                main_layout.addLayout(self.create_image_with_text_below("menu_veg.jpeg", burger_type, menuID))
            else:
                main_layout.addLayout(self.create_image_with_text_below("menu_carne.jpeg", burger_type, menuID))

        self.frame = QFrame()
        second_layout = QHBoxLayout()
        second_layout.setContentsMargins(0, 0, 0, 0)
        second_layout.setAlignment(Qt.AlignBottom | Qt.AlignCenter)

        # Adiciona a seção 1 com imagem, texto e checkbox
        second_layout.addLayout(self.create_checkbox_with_image("alface.jpeg", "Alface"))
        second_layout.addWidget(self.create_separator())
        # Adiciona a seção 2 com outra imagem, texto e checkbox
        second_layout.addLayout(self.create_checkbox_with_image("tomate.jpeg", "Tomate"))
        second_layout.addWidget(self.create_separator())
        # Adiciona a seção 2 com outra imagem, texto e checkbox
        second_layout.addLayout(self.create_checkbox_with_image("queijo.jpeg", "Queijo"))
        second_layout.addWidget(self.create_separator())
        # Adiciona a seção 2 com outra imagem, texto e checkbox
        second_layout.addLayout(self.create_checkbox_with_image("cebola.jpeg", "Cebola"))

        self.frame.setLayout(second_layout)  # Define o segundo layout como conteúdo do QFrame
        overall_layout.setSpacing(0)
        overall_layout.setContentsMargins(0, 0, 0, 0)
        overall_layout.addLayout(main_layout)
        overall_layout.addWidget(self.frame)  # Adiciona o QFrame ao layout geral

        self.setLayout(overall_layout)
        self.toggleFrame()

    def toggleFrame(self):
        self.frame.setHidden(not self.frame.isHidden())

    def next_window(self, menuID):
        # Collect checkbox states and text
        checkbox_states = {
            "Alface": self.frame.findChild(QCheckBox, "AlfaceCheckbox").isChecked(),
            "Tomate": self.frame.findChild(QCheckBox, "TomateCheckbox").isChecked(),
            "Queijo": self.frame.findChild(QCheckBox, "QueijoCheckbox").isChecked(),
            "Cebola": self.frame.findChild(QCheckBox, "CebolaCheckbox").isChecked(),
        }

        checkbox_texts = {
            "Alface": "Alface",
            "Tomate": "Tomate",
            "Queijo": "Queijo",
            "Cebola": "Cebola",
        }
        self.next_window_instance = Final_Window(menuID, checkbox_states)
        self.next_window_instance.show()
        # Close the current window
        self.close()

    def go_back(self, burger_type):
        menuorburger_instance = MenuOrBurger(burger_type)
        menuorburger_instance.show()
        self.close()

    def create_checkbox_with_image(self, image_filename, checkbox_text):
        layout = QHBoxLayout()
        label = QLabel(self)

        img_path = os.path.join(CURRENT_DIR, image_filename)
        pixmap = QPixmap(img_path)
        pixmap = pixmap.scaledToWidth(100)
        pixmap = pixmap.scaledToHeight(100)
        label.setPixmap(pixmap)

        checkbox = QCheckBox(checkbox_text, self)
        checkbox.setChecked(True)
        checkbox.setObjectName(f"{checkbox_text}Checkbox")
        layout.addWidget(label)
        layout.addWidget(checkbox)

        return layout

    def create_separator(self):
        # Cria uma barra vertical preta como separador
        color = "#FFA500"
        separator = QFrame(self)
        separator.setFrameShape(QFrame.VLine)
        separator.setFrameShadow(QFrame.Sunken)
        separator.setStyleSheet(f"color: {color}; background-color: {color};")

        return separator

    def create_image_with_text_below(self, image_filename, burger_type, menuID):
        layout = QVBoxLayout()
        layout.setSpacing(0)
        layout.setContentsMargins(0, 0, 0, 0)
        # Criar QLabel para o texto acima da imagem
        label_text = QLabel(burger_type, self)
        label_text.setAlignment(Qt.AlignCenter)
        text_style = \
            'background-color: orange;' \
            'border-radius: 4;' \
            "font: Bold;" \
            "font-family:" \
            " Georgia;" \
            "font-size: 15px;" \
            'padding: 10px;'
        label_text.setStyleSheet(text_style)
        label_text.setFixedSize(1280, 50)

        layout.addWidget(label_text)

        layout2 = QHBoxLayout()
        layout2.setSpacing(0)
        layout2.setContentsMargins(0, 150, 0, 0)

        back_button = QPushButton(self)
        back_button.setStyleSheet(
            'background-color: orange;'
            'border-radius: 4;'
            "font: Bold;"
            "font-family:"
            " Georgia;"
            "font-size: 15px;"
            'padding: 10px;'
        )
        back_button.setIcon(QIcon(os.path.join(CURRENT_DIR, "back.jpeg")))
        # Defina o tamanho desejado para o botão
        back_button.setFixedSize(70, 70)
        back_button.clicked.connect(lambda: self.go_back(burger_type))

        label_image = QLabel(self)
        img_path = os.path.join(CURRENT_DIR, image_filename)
        pixmap = QPixmap(img_path)
        pixmap = pixmap.scaledToWidth(300)  # Ajuste a largura desejada
        pixmap = pixmap.scaledToHeight(300)  # Ajuste a altura desejada
        label_image.setAlignment(Qt.AlignCenter)
        label_image.setPixmap(pixmap)

        next_button = QPushButton(self)
        next_button.setIcon(
            QIcon(QPixmap(os.path.join(CURRENT_DIR, "back.jpeg")).transformed(QTransform().rotate(180))))
        next_button.setStyleSheet(
            'background-color: orange;'
            'border-radius: 4;'
            "font: Bold;"
            "font-family: Georgia;"
            "font-size: 15px;"
            'padding: 10px;'
        )
        next_button.setFixedSize(70, 70)
        next_button.clicked.connect(lambda: self.next_window(menuID))

        layout2.addWidget(back_button, alignment=Qt.AlignCenter)
        layout2.addWidget(label_image, alignment=Qt.AlignCenter)
        layout2.addWidget(next_button, alignment=Qt.AlignCenter)

        layout.addLayout(layout2)
        # Criar QLabel para a imagem

        button = QPushButton("Editar Hamburguer", self)
        button.setStyleSheet(
            'background-color: orange;'
            'border-radius: 4;'
            "font: Bold;"
            "font-family: Georgia;"
            "font-size: 15px;"
            'padding: 10px'
            "margin"
        )
        button.setFixedSize(400, 50)
        button.clicked.connect(lambda: self.toggleFrame())
        layout.addWidget(button, alignment=Qt.AlignCenter)

        return layout


###############################################################################################################
class Final_Window(QWidget):

    def __init__(self, menuID, checkbox_states):
        super().__init__()
        self.setWindowTitle("Final Window")
        self.setFixedSize(1280, 740)

        self.layout = QVBoxLayout(self)
        self.layout.setSpacing(0)

        # Texto "Pedido Finalizado"
        self.label_pedido_finalizado = QLabel("Pedido Finalizado", self)
        text_style = \
            'background-color: orange;' \
            'border-radius: 4;' \
            "font: Bold;" \
            "font-family:" \
            " Georgia;" \
            "font-size: 15px;" \
            'padding: 10px;'
        self.label_pedido_finalizado.setStyleSheet(text_style)
        self.label_pedido_finalizado.setFixedSize(1280, 100)
        self.label_pedido_finalizado.setAlignment(Qt.AlignCenter)
        self.layout.addWidget(self.label_pedido_finalizado)

        # Primeiro layout com gif
        self.show_initial_layout()
        global count

        count += 1
        order = {'pedido': count, 'status': False, 'id': menuID, 'ingridients': list(checkbox_states.items())}

        send_data_to_thread({"type": "order", "order": order})

        #     label_checkbox = QLabel(f"{checkbox_text}: {'Sim' if checkbox_value else 'Não'}", self)
        #     self.layout.addWidget(label_checkbox)

    def show_initial_layout(self):
        # Gif inicial
        gif_path = os.path.join(CURRENT_DIR, "wait.gif")  # Substitua pelo caminho real do seu gif
        movie = QMovie(gif_path)
        label_gif = QLabel(self)
        label_gif.setMovie(movie)
        label_gif.setAlignment(Qt.AlignCenter)
        label_gif.move(640, 270)
        movie.start()
        self.layout.addWidget(label_gif)

        # Agendar a mudança para o segundo layout após dois segundos
        QTimer.singleShot(2000, lambda: self.show_second_layout(movie))

    def show_second_layout(self, movie):
        global count
        # Parar o gif
        movie.stop()
        # Remover widgets do primeiro layout
        for i in reversed(range(self.layout.count())):
            self.layout.itemAt(i).widget().setParent(None)
        # Manter o texto inicial
        self.layout.addWidget(self.label_pedido_finalizado)
        self.layout.setSpacing(100)
        # self.layout.setContentsMargins(0,0,0,0)
        # Nova imagem
        label_imagem_nova = QLabel(self)
        img_path = os.path.join(CURRENT_DIR, "finalizado.jpeg")
        imagem_nova = QPixmap(img_path)  # Substitua pelo caminho real da sua nova imagem
        label_imagem_nova.setPixmap(imagem_nova.scaledToWidth(300))
        label_imagem_nova.move(640, 370)
        label_imagem_nova.setAlignment(Qt.AlignCenter)

        self.layout.addWidget(label_imagem_nova)

        self.label_pedido_number = QLabel(f"Pedido Número {count}", self)
        text_style = \
            'background-color: orange;' \
            'border-radius: 4;' \
            "font: Bold;" \
            "font-family:" \
            " Georgia;" \
            "font-size: 15px;" \
            'padding: 10px;'
        self.label_pedido_number.setStyleSheet(text_style)
        self.label_pedido_number.setFixedSize(300, 50)
        self.label_pedido_number.setAlignment(Qt.AlignCenter)
        self.layout.addWidget(self.label_pedido_number, alignment=Qt.AlignCenter)

        QTimer.singleShot(2000, lambda: self.showMain())


    def showMain(self):
        window.show()
        self.close()


###############################################################################################################

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()

    output_thread = threading.Thread(target=pi_thread)
    output_thread.start()

    sys.exit(app.exec_())

