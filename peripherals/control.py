import sys
import queue
import threading
import pygame
import os

sys.path.append('/home/raspad/Desktop/KukaCooker/')


from robot.connection import read_robot, write_robot
from time import sleep
from peripheral.display import turn_on, update_screen
from peripheral.IOs_control import GrillController, MotorController

# Creating a shared queue for inter-thread communication
shared_queue = queue.Queue()

# Creating a lock for thread-safe access to the queue
queue_lock = threading.Lock()

# Dictionary mapping burger types to their IDs
burger_types = {
    1: 'Normal',
    2: 'Normal + D',
    3: 'Frango',
    4: 'Frango + D',
    5: 'Veg',
    6: 'Veg + D'
}

# Dictionary mapping rail positions to coordinates
pos_rail = {
    1: 'X 75, Y 5, Z -20',
    2: 'X 120, Y 15, Z -30',
    3: 'X 140, Y 25, Z -30',
    4: 'X 210, Y 20, Z -30',
    5: 'X 232, Y 50, Z -25',
    6: 'X 260, Y 60, Z -25',
    7: 'X 300, Y 85, Z -25',
}

# Function representing the thread for processing data
def pi_thread():
    # Initialize pygame mixer for playing sounds
    pygame.mixer.init()
    pygame.mixer.music.load("/home/raspad/Desktop/KukaCooker/peripheral/hand_dryer.mp3")

    # Initialize variables
    order_list, pedidos, entregas, centroids = [], [], [], []
    processing = 0

    ingredients = ['tomatoHSVRange', 'breadBHSVRange', 'breadTHSVRange', 'cheeseHSVRange', 'burgerHSVRange',
                   'onionHSVRange', 'lettuceHSVRange']

    frango_order = [ingredients[1], ingredients[6], ingredients[5], ingredients[4],
                    ingredients[3], ingredients[0], ingredients[2]]

    normal_order = [ingredients[1], ingredients[0], ingredients[6], ingredients[4],
                    ingredients[3], ingredients[5], ingredients[2]]

    veg_order = [ingredients[1], ingredients[0], ingredients[6], ingredients[5]]

    turn_on()  # Turn on display

    grill_controller = GrillController(left_led_pin=5, right_led_pin=6, button_pin=18)
    motors = MotorController(20, 21, 16, 13, 4, 17, 23, 12)

    while True:
        # Check if the shared queue is not empty
        if not shared_queue.empty():
            with queue_lock:
                data = shared_queue.get()
                # Process order data
                if data["type"] == "order":
                    print(data["order"])
                    order_list.append(data["order"])

                    for order in order_list:
                        if not order['status'] and str(order['pedido']) not in pedidos:
                            pedidos.extend(str(order['pedido']))
                    print(pedidos)
                    update_screen(pedidos, entregas)

                    processing = 1

                # Process coordinates data
                elif data["type"] == "coords":
                    centroids = data["centroids"]
                    print(centroids)

        # If processing an order and the robot is available
        if processing == 1 and read_robot('$KB_Available') == 'TRUE':
            print(order_list)
            write_robot('KB_JOB', '1')

            order = order_list[0]
            if order['id'] in [1, 2]:
                order_id = normal_order
            elif order['id'] in [3, 4]:
                order_id = frango_order
            else:
                order_id = veg_order

            if order['id'] in [2, 4, 6]:
                drink = True

            robot_coords = {ingredient: centroids[ingredient] for ingredient in order_id}

            rail_move = list(robot_coords.keys())
            print(robot_coords[rail_move[0]])
            sleep(10)

            # Write ingredient coordinates to the robot
            for i, (key, values) in enumerate(robot_coords.items()):
                if key == 'burgerHSVRange':
                    new_key = 'H'
                elif key == 'breadTHSVRange':
                    new_key = 'B'
                elif key == 'breadBHSVRange':
                    new_key = 'P'
                else:
                    new_key = key[0].capitalize()

                formatted_string = f'{{IngredientCoords: {pos_rail[values["index"]]}, name "{new_key}"}}'
                print(formatted_string)
                print('AAAA', f"KB_IngCoords[{order_id.index(key) + 1}]")
                write_robot(f"KB_IngCoords[{order_id.index(key) + 1}]", formatted_string)

            write_robot('KB_Ingredients', f'{len(robot_coords)}')

            pos = 0

            processing = 2

        # While processing an order
        while processing == 1:
            # Check button state and control grill accordingly
            if not grill_controller.read_button():
                write_robot('KB_ButtonClicked', 'TRUE')
                grill_controller.max_duty_reached = False

                if not grill_controller.grill_on:
                    grill_controller.turn_on()
            else:
                grill_controller.turn_off()

            # Open gripper
            if read_robot('KB_GripOpen') == '1' and read_robot('$ROB_STOPPED') == 'TRUE':
                motors.set_angle(70)
                sleep(1)
                motors.stop()

                write_robot('KB_GripOpen', '2')

            # Close gripper
            if read_robot('KB_GripClose') == '1' and read_robot('$ROB_STOPPED') == 'TRUE':
                motors.set_angle(180)
                sleep(1)
                motors.stop()

                write_robot('KB_GripClose', '2')

            # Processed order
            if read_robot('KB_Processed') == 'TRUE':
                pedido_pronto = pedidos.pop(0)
                print(pedido_pronto)
                entregas.append(pedido_pronto['pedido'])
                update_screen(pedidos, entregas)

                processing = 0

            # Play music
            if read_robot('KB_Music') == '1' and read_robot('$ROB_STOPPED') == 'TRUE':
                pygame.mixer.music.play()
                write_robot('KB_Music', '0')

            # Stop music
            if read_robot('KB_Music') == '2' and read_robot('$ROB_STOPPED') == 'TRUE':
                pygame.mixer.music.stop()

            # Move to next position
            if read_robot('KB_InPosition') == '1' and read_robot('$ROB_STOPPED') == 'TRUE':
                motors.move(int(robot_coords[rail_move[pos]]['index']))
                motors.stepper_forward(450)
                sleep(0.2)
                motors.stepper_backward(450)
                sleep(0.2)

                write_robot('KB_InPosition', '0')

                pos += 1


# Function to send data to the thread
def send_data_to_thread(data):
    with queue_lock:
        shared_queue.put(data)

def play_song():
    pygame.mixer.init()
    pygame.mixer.music.load("/home/raspad/Desktop/KukaCooker/peripheral/hand_dryer.mp3")
    
    while True:
        if read_robot('KB_Music') == '1':
                pygame.mixer.music.play()
                write_robot('KB_Music', '0')
                
        if read_robot('KB_Music') == '2':
            pygame.mixer.music.stop()
            write_robot('KB_Music', '0')
# def receive_order(order):
#     global a, order_list, pedidos, entregas
#     a = 5
#     order_list.extend(order.copy())
#     for order in order_list:
#         if not order['status'] and str(order['pedido']) not in pedidos:
#             pedidos.extend(str(order['pedido']))
#     update_screen(pedidos, entregas)
#
#
# def receive_centroids(valores, dist):
#     global centroids, ret_dist
#
#     dist = "{:.2f}".format(dist)
#
#     centroids = valores.copy()
#     print(type(centroids))
#
#     print("distancia : ", dist)


# pi_thread()