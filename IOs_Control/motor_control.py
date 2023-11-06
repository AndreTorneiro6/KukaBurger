import RPi.GPIO as GPIO
from time import sleep



def start():
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(17, GPIO.OUT)
    global pwm
    pwm = GPIO.PWM(17, 50)
    pwm.start(0)

def setAngle(angle, start=False):
    duty = angle / 18 + 2
    GPIO.output(17, True)
    pwm.ChangeDutyCycle(duty)
    return duty
   
def stop():
    pwm.ChangeDutyCycle(0)
 
'''    
count = 0
numLoops = 2

while count < numLoops:
    print("set to 0-deg")
    setAngle(70)
    sleep(0.5)
        
    print("set to 90-deg")
    setAngle(0)
    sleep(1)

    print("set to 135-deg")
    setAngle(180)
    sleep(1)
    
    count=count+1

pwm.stop()
GPIO.cleanup()


import RPi.GPIO as GPIO
from time import sleep

## add your servo BOARD PIN number ##
servo_pin = 17

GPIO.setmode(GPIO.BCM)
GPIO.setup(servo_pin, GPIO.OUT)

pwm=GPIO.PWM(servo_pin, 50)
pwm.start(0)

## edit these duty cycle % values ##
left = 8
neutral = 2
right = 5
#### that's all folks ####

print("begin test")

print("duty cycle", left,"% at left -90 deg")
pwm.ChangeDutyCycle(left)
sleep(1)

print("duty cycle", neutral,"% at 0 deg")
pwm.ChangeDutyCycle(neutral)
sleep(1)

print("duty cycle",right, "% at right +90 deg")
pwm.ChangeDutyCycle(right)
sleep(1)
print("end of test")

pwm.stop()
GPIO.cleanup()
'''