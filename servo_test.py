import RPi.GPIO as GPIO
import time

SERVO_PIN = 18

GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)
GPIO.setup(SERVO_PIN, GPIO.OUT)

servo = GPIO.PWM(SERVO_PIN, 50)

servo.start(0)

def set_angle(angle):
    duty = 2 + (angle/18)
    GPIO.output(SERVO_PIN, True)
    servo.ChangeDutyCycle(duty)
    time.sleep(0,3)
    GPIO.output(SERVO_PIN, False)
    servo.ChangeDutyCycle(0)
    
set_angle(0)
time.sleep(1)
set_angle(90)
time.sleep(1)
set_angle(0)
time.sleep(1)

servo.stop()
GPIO.cleanup()
