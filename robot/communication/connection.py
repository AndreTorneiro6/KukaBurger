from py_openshowvar import openshowvar
from time import sleep
import re

# Establishing connection with the robot controller
client = openshowvar('172.21.84.105', 9999)

# Function to read a variable from the robot controller
def read_robot(variable):
    return client.read(variable, debug=False).decode()

# Function to write a value to a variable on the robot controller
def write_robot(variable, value):
    client.write(variable, value)

# Function to send gripper orientation to the robot
def send_gripper_orientation(orientation, grip_base, index):
    # Dictionary to map orientation to axis angles
    axis_angles = {
        'right': [('A4', 90), ('A5', 92), ('A6', -110)],
        'front': [('A4', 0), ('A5', -8), ('A6', 0)],
        'left': [('A4', 90), ('A5', -92), ('A6', -110)],
    }

    # Format the message with gripper axis and grip base
    formatted_message = f'{{GripperAxis: {", ".join(f"{axis} {value}" for axis, value in axis_angles.get(orientation, []))}, grip "{grip_base}"}}'
    print(formatted_message)
    # Write the formatted message to the robot controller
    client.write(f'KB_Orientation[{index}]', formatted_message, debug=False)

# send_gripper_orientation(orientation='right', grip_base='R',index=1)
# write_robot('KB_IngCoords[1]', f"{{IngredientCoords: X 2, name 2}}")
# print(f"{{IngredientCoords: X 2, name 2}}")

# send_gripper_orientation(orientation='left', grip_base='L', index=2)
# send_gripper_orientation(orientation='front', grip_base='F', index=3)
# write_robot('KB_ButtonClicked', 'FALSE')
# write_robot('$OUT[1]','TRUE')
send_gripper_orientation(orientation='right', grip_base='R', index=1)
send_gripper_orientation(orientation='left', grip_base='L', index=2)
send_gripper_orientation(orientation='front', grip_base='F', index=3)

pos_rail = {
    1: 'X 30, Y 5, Z 5',
    5: 'X 75, Y 10, Z 5',
    3: 'X 125, Y 16, Z 5',
    6: 'X 185, Y 27, Z 0',
    4: 'X 235, Y 40, Z 0',
    7: 'X 270, Y 50, Z -10',
    2: 'X 312, Y 66, Z -15',
}


for key, values in pos_rail.items():
#         if key == 'burgerHSVRange':
#             new_key = 'H'
#         elif key == 'breadTHSVRange':
#             new_key = 'B'
#         elif key == 'breadBHSVRange':
#             new_key = 'P'
#         else:
#             new_key = key[0].capitalize()
        
        formatted_string = f'{{IngredientCoords: {values}, name "A"}}'
        print(formatted_string)
#         print('AAAA', f"KB_IngCoords[{values['index']}]")
        write_robot(f"KB_IngCoords[{key}]", formatted_string)
write_robot('KB_IngCoords[4]', '{IngredientCoords: X 240, Y 40, Z -10, name "H"}')
# write_robot('KB_Job', '1')
# write_robot('KB_InPosition', '0')
# print(read_robot('KB_IngCoords[2]'))
# write_robot('KB_GripOpen','2')
# write_robot('KB_GripClose','2')
write_robot('KB_WashCoords[1]', '{FRAME: X 55, Y 95, Z 0, A 80, B 0, C -178}')
write_robot('KB_WashCoords[2]', '{FRAME: X 155, Y 70, Z 0, A 80, B 0, C -178}')
