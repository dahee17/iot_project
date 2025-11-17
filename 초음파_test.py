import RPi.GPIO as GPIO
import time

TRIG = 23
ECHO = 24

GPIO.setmode(GPIO.BCM)
GPIO.setup(TRIG, GPIO.OUT)
GPIO.setup(ECHO, GPIO.IN)

def get_distance():
    GPIO.output(TRIG, True)
    time.sleep(0.00001)
    GPIO.output(TRIG, False)

    while GPIO.input(ECHO) == 0:
        pulse_start = time.time()
    while GPIO.input(ECHO) == 1:
        pulse_end = time.time()

    duration = pulse_end - pulse_start
    distance = duration * 17150
    return round(distance, 2)

try:
    while True:
        distance = get_distance()
        if distance <= 15:
            print(f"접근 감지/ 거리: {distance} cm")
        else:
            print(f"거리: {distance} cm")
        time.sleep(0.5)

except KeyboardInterrupt:
    GPIO.cleanup()
