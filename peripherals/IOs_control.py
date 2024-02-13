import RPi.GPIO as GPIO
import time
from time import sleep


class GrillController:
    def __init__(self, left_led_pin, right_led_pin, button_pin):
        self.left_led_pin = left_led_pin
        self.right_led_pin = right_led_pin
        self.button_pin = button_pin

        # GPIO.setmode(GPIO.BCM)  # Setting the GPIO mode to Broadcom numbering scheme

        GPIO.setup(self.left_led_pin, GPIO.OUT)  # Setting up the left LED pin as output
        GPIO.setup(self.right_led_pin, GPIO.OUT)  # Setting up the right LED pin as output
        GPIO.setup(self.button_pin, GPIO.IN,
                   pull_up_down=GPIO.PUD_UP)  # Setting up the button pin as input with pull-up resistor

        self.left_led_pwm = GPIO.PWM(self.left_led_pin, 100)  # Creating PWM object for the left LED pin
        self.left_led_pwm.start(0)  # Starting PWM with duty cycle 0

        self.right_led_pwm = GPIO.PWM(self.right_led_pin, 100)  # Creating PWM object for the right LED pin
        self.right_led_pwm.start(0)  # Starting PWM with duty cycle 0

        self.grill_on = False  # Variable to track grill state
        self.button_state = False  # Variable to store button state
        self.max_duty_reached = True  # Variable to track if maximum duty cycle is reached

    def read_button(self):
        self.button_state = GPIO.input(self.button_pin)  # Reading the state of the button
        return self.button_state  # Returning the button state

    def turn_on(self):
        if not self.max_duty_reached:
            for i in range(101):  # Looping through duty cycles from 0 to 100
                self.left_led_pwm.ChangeDutyCycle(i)  # Changing duty cycle of left LED
                self.right_led_pwm.ChangeDutyCycle(i)  # Changing duty cycle of right LED
                time.sleep(0.1)  # Waiting for a short duration
                print(i)  # Printing the current duty cycle
        self.max_duty_reached = True  # Resetting maximum duty cycle reached flag
        self.grill_on = not self.grill_on  # Toggling grill state
        return self.grill_on  # Returning the grill state

    def turn_off(self):
        if not self.max_duty_reached:
            for j in reversed(range(100)):  # Looping through duty cycles from 99 to 0 in reverse order
                self.left_led_pwm.ChangeDutyCycle(j)  # Changing duty cycle of left LED
                self.right_led_pwm.ChangeDutyCycle(j)  # Changing duty cycle of right LED
                time.sleep(0.1)  # Waiting for a short duration

        self.max_duty_reached = True  # Resetting maximum duty cycle reached flag
        self.grill_on = not self.grill_on  # Toggling grill state
        return self.grill_on  # Returning the grill state


class MotorController:
    def __init__(self, dir_pin, step_pin, control_pin, servo_pin, stepper_in1, stepper_in2, stepper_in3, stepper_in4):
        self.dir_pin = dir_pin
        self.step_pin = step_pin
        self.control_pin = control_pin
        self.servo_pin = servo_pin
        self.stepper_in_1 = stepper_in1
        self.stepper_in_2 = stepper_in2
        self.stepper_in_3 = stepper_in3
        self.stepper_in_4 = stepper_in4
        self.positions = [0, 7500, 11750, 16000, 20250, 24500, 28750, 33000]

        self.current_position = 0  # Variable to store current position of motor

        self.sequence = [
            [1, 0, 0, 0],
            [1, 1, 0, 0],
            [0, 1, 0, 0],
            [0, 1, 1, 0],
            [0, 0, 1, 0],
            [0, 0, 1, 1],
            [0, 0, 0, 1],
            [1, 0, 0, 1]
        ]

        # stepper rail motor
        GPIO.setup(self.dir_pin, GPIO.OUT)
        GPIO.setup(self.step_pin, GPIO.OUT)
        GPIO.setup(self.control_pin, GPIO.OUT)

        GPIO.output(self.control_pin, GPIO.HIGH)

        # stepper mini motor
        GPIO.setup(self.stepper_in_1, GPIO.OUT)
        GPIO.setup(self.stepper_in_2, GPIO.OUT)
        GPIO.setup(self.stepper_in_3, GPIO.OUT)
        GPIO.setup(self.stepper_in_4, GPIO.OUT)

        # servo motor
        GPIO.setup(self.servo_pin, GPIO.OUT)
        self.pwm = GPIO.PWM(self.servo_pin, 50)
        self.pwm.start(0)

    def rotate_motor(self, delay, direction, steps):
        GPIO.output(self.dir_pin, direction)  # Setting the direction of rotation
        for _ in range(steps):
            GPIO.output(self.step_pin, GPIO.HIGH)  # Applying step signal
            time.sleep(delay)  # Delaying for a short duration
            GPIO.output(self.step_pin, GPIO.LOW)  # Turning off step signal
            time.sleep(delay)  # Delaying for a short duration

    def move(self, desired_position):
        if 0 <= desired_position <= 7:
            print(desired_position, self.current_position)
            position = desired_position - self.current_position
            move_position = self.positions[desired_position] - self.positions[self.current_position]

            print(self.current_position, position)

            if position < 0:
                GPIO.output(self.control_pin, GPIO.LOW)  # Enabling the motor control
                self.rotate_motor(0.001, GPIO.LOW, abs(move_position))  # Rotating the motor in one direction
                self.current_position = desired_position  # Updating the current position
                GPIO.output(self.control_pin, GPIO.HIGH)  # Disabling the motor control
            elif position > 0:
                GPIO.output(self.control_pin, GPIO.LOW)  # Enabling the motor control
                self.rotate_motor(0.001, GPIO.HIGH, abs(move_position))  # Rotating the motor in the other direction
                self.current_position = desired_position  # Updating the current position
                print(self.current_position)
                GPIO.output(self.control_pin, GPIO.HIGH)  # Disabling the motor control

    def set_angle(self, angle):
        duty = angle / 18 + 3  # Calculating duty cycle for servo motor
        GPIO.output(self.servo_pin, True)  # Turning on servo motor
        self.pwm.ChangeDutyCycle(duty)  # Setting duty cycle
        return duty  # Returning duty cycle

    def stop(self):
        self.pwm.ChangeDutyCycle(0)  # Stopping the servo motor

    def stepper_forward(self, position):
        steps = position % 512  # Calculating the number of steps based on desired position
        for _ in range(steps):
            for halfstep in range(8):  # Looping through half-steps
                for pin in range(4):  # Looping through stepper motor pins
                    GPIO.output([self.stepper_in_1, self.stepper_in_2, self.stepper_in_3, self.stepper_in_4][pin],
                                self.sequence[halfstep][pin])
                time.sleep(0.001)  # Delaying for a short duration

    def stepper_backward(self, position):
        steps = position % 512  # Calculating the number of steps based on desired position
        for _ in range(steps):
            for halfstep in range(7, -1, -1):  # Looping through half-steps in reverse order
                for pin in range(4):  # Looping through stepper motor pins
                    GPIO.output([self.stepper_in_1, self.stepper_in_2, self.stepper_in_3, self.stepper_in_4][pin],
                                self.sequence[halfstep][pin])
                time.sleep(0.001)  # Delaying for a short duration
