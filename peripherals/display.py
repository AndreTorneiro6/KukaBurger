from PIL import Image  # Importing the Image module from PIL library
from PIL import ImageDraw  # Importing the ImageDraw module from PIL library
from PIL import ImageFont  # Importing the ImageFont module from PIL library
import ST7735 as TFT  # Importing the ST7735 module for the TFT display
import Adafruit_GPIO as GPIO  # Importing the Adafruit GPIO library
import Adafruit_GPIO.SPI as SPI  # Importing the Adafruit GPIO SPI library
from time import sleep  # Importing the sleep function from the time module


WIDTH = 128  # Setting the width of the display
HEIGHT = 160  # Setting the height of the display
SPEED_HZ = 4000000  # Setting the SPI speed
background_color = 'white'  # Setting the background color
image = Image.new("RGB", (WIDTH, HEIGHT),
                  color=background_color)  # Creating a new image with specified width, height, and background color

# Conexoes
DC = 24  # Setting the pin for Data/Command
RST = 25  # Setting the pin for Reset
SPI_PORT = 0  # Setting the SPI port
SPI_DEVICE = 0  # Setting the SPI device

# Cria o objeto de controle do display
disp = TFT.ST7735(
    DC,
    rst=RST,
    spi=SPI.SpiDev(
        SPI_PORT,
        SPI_DEVICE,
        max_speed_hz=SPEED_HZ))

# Inicia e limpa o display
disp.begin()

# Obtem o objeto ImageDraw para desenhar com o PIL
draw = disp.draw()

# Escreve um texto
font = ImageFont.load_default()


# Funcao para escrever texto rotacionado
def draw_rotated_text(image, text, position, angle, font, fill=(255, 255, 255)):
    # Get rendered font width and height.
    draw = ImageDraw.Draw(image)
    width, height = draw.textsize(text, font=font)
    # Create a new image with transparent background to store the text.
    textimage = Image.new('RGBA', (width, height), (0, 0, 0, 0))

    # Render the text.
    textdraw = ImageDraw.Draw(textimage)
    textdraw.text((0, 0), text, font=font, fill=fill)
    # Rotate the text image.
    rotated = textimage.rotate(angle, expand=1)
    # Paste the text into the image, using it as a mask for transparency.
    image.paste(rotated, position, rotated)


def turn_on():
    draw.rectangle((0, 0, 160, 160), outline=(64, 64, 64), fill=(255, 255, 255))

    # Uma caixa para o texto
    draw.rectangle((105, 8, 124, 80), outline=(64, 64, 64), fill=(0, 0, 255))

    # draw a line from (10,50) to (150,80) whit a red color
    line_color = "green"
    start_point = (0, 83)
    end_point = (150, 83)
    draw.line([start_point, end_point], fill=line_color, width=2)

    # Uma caixa para o texto
    draw.rectangle((105, 86, 124, 155), outline=(64, 64, 64), fill=(0, 192, 0))

    # Escreve um texto
    font = ImageFont.load_default()

    # Write two lines of white text on the buffer, rotated 90 degrees counter clockwise.
    draw_rotated_text(disp.buffer, 'PEDIDO', (110, 25), 270, font, fill=(255, 255, 255))
    draw_rotated_text(disp.buffer, 'ENTREGA', (110, 100), 270, font, fill=(255, 255, 255))

    disp.display()


def clear_text_region(position):
    draw.rectangle(position, fill=(255, 255, 255))


# Função para atualizar o texto do pedido
def update_screen(pedidos, entregas):
    # Limpa a área do texto do pedido
    pos_n_right = 100
    pos_n_left = 100
    clear_text_region((90, 0, 0, 80))
    clear_text_region((90, 90, 0, 155))

    for i, pedido in enumerate(pedidos):
        pos_n_right -= 15
        draw_rotated_text(disp.buffer, f'Pedido {pedido}', (pos_n_right, 15), 270, font, fill=(0, 0, 255))

    for i, entrega in enumerate(entregas):
        pos_n_left -= 15
        draw_rotated_text(disp.buffer, f'Pedido {entrega}', (pos_n_left, 90), 270, font, fill=(0, 192, 0))

    # Desenha o novo texto do pedido
    # Atualiza a tela
    disp.display()
