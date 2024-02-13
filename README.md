# KukaBurger

Welcome to the KukaBurger project repository! This project aims to automate the process of burger assembly using a KUKA robotic arm. The repository contains the necessary code and resources to control the robotic arm, coordinate its actions, and interface with external hardware components.

## Objective

The main objective of the KukaBurger project is to demonstrate the automation capabilities of the KUKA robotic arm in the food industry, specifically in the assembly of burgers. By automating this process, we aim to increase efficiency, reduce labor costs, and ensure consistency in burger preparation.

## Folder Structure

- **interface/**: Contains the code and assets for interfacing with external hardware components.
  - **assets/**: Contains assets such as images or configuration files used in the interface.
  - `app.py`: Create and Manage the entire interface in PyQT.
- **peripherals/**: Contains the code for control external hardware components.  
  - **IO_S_control/**: Contains classes for controlling the grill and motors.
    - `grill.py`: Defines a class for controlling the grill.
    - `motors.py`: Defines a class for controlling the motors.
  - `display.py`: Controls the display for user interaction.
  - `control.py`: Manages the hardware control and communication with the robotic arm.
- **robot/**: Contains the code for communication with the KUKA robotic arm and the KRL source code.
  - **communication/**: Contains code for communicating with the robot.
    - `connection.py`: Code for communicating with the robot using pyopenshowvar.
  - **krl/**: Contains the source code for the KUKA Robot Language (KRL) scripts.
    - `official_code.src`: Defines the loop control of the entire workflow.
    - `main.src`: Defines a function to change the orientation of the robotic arm.
    - `prepare_burger.sub`: Defines a function to prepare the burger by grabbing ingredients.
    - `stop_move_interrupt.src`: Defines a function to stop movement interrupts.
    - `wash_clean.sub`: Defines a function to wash and clean the gripper.
- **segmentation/**: Contains code for image processing and segmentation.
  - `hsv-finder.py`: Finds the HSV color range for image segmentation.
  - `segment_ingredients.py`: Processes images for segmentation.
  - `find_cont.py`: Performs image segmentation for object detection.
  - `colors_range`: Json file where the HSV ranges are stored.



## Video Demonstration

Check out the video demonstration of the KukaBurger project [here](https://alunosipca-my.sharepoint.com/:v:/g/personal/a17636_alunos_ipca_pt/EZcFDILYUJxGjHFCQDqaefIBifg4ynJKzZ8er7q-3qD_RA?nav=eyJyZWZlcnJhbEluZm8iOnsicmVmZXJyYWxBcHAiOiJPbmVEcml2ZUZvckJ1c2luZXNzIiwicmVmZXJyYWxBcHBQbGF0Zm9ybSI6IldlYiIsInJlZmVycmFsTW9kZSI6InZpZXciLCJyZWZlcnJhbFZpZXciOiJNeUZpbGVzTGlua0NvcHkifX0&e=BFn2MZ)!
