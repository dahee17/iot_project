import RPi.GPIO as GPIO
import time
import threading
import json
from datetime import datetime
from app import status, app, SCHEDULE_FILE
from flask import Flask, render_template

SERVO_PIN = 18   
BUZZER_PIN = 15
LED_PIN = 14     
TRIG = 23
ECHO = 24

GPIO.setmode(GPIO.BCM)
GPIO.setup(SERVO_PIN, GPIO.OUT)
GPIO.setup(BUZZER_PIN, GPIO.OUT)
GPIO.setup(LED_PIN, GPIO.OUT)
GPIO.setup(TRIG, GPIO.OUT)
GPIO.setup(ECHO, GPIO.IN)

servo = GPIO.PWM(SERVO_PIN, 50)
servo.start(0)


def servo_open():
    servo.ChangeDutyCycle(7)
    time.sleep(1)
    servo.ChangeDutyCycle(0)

def servo_close():
    servo.ChangeDutyCycle(2)
    time.sleep(1)
    servo.ChangeDutyCycle(0)
# --
def beep(duration=0.2):
    GPIO.output(BUZZER_PIN, 1)
    time.sleep(duration)
    GPIO.output(BUZZER_PIN, 0)

def play_melody_with_led():
    GPIO.output(LED_PIN, 1)
    buz = GPIO.PWM(BUZZER_PIN, 440)
    buz.start(50)
    notes = [
        (262, 0.4),  
        (330, 0.4),  
        (392, 0.4),  
        (523, 0.4)   
    ]
    for freq, duration in notes:
        buz.ChangeFrequency(freq)
        time.sleep(duration)
    buz.stop()
    GPIO.output(LED_PIN, 0)


def get_distance():
    GPIO.output(TRIG, 1)
    time.sleep(0.00001)
    GPIO.output(TRIG, 0)

    start = time.time()
    timeout = start + 0.05
    while GPIO.input(ECHO) == 0 and time.time() < timeout:
        start = time.time()
    end = time.time()
    while GPIO.input(ECHO) == 1 and time.time() < timeout:
        end = time.time()
    return (end - start) * 34300 / 2


def main_loop():
    last_minute_displayed = None

    while True:
      
        with open(SCHEDULE_FILE, "r") as f:
            sc = json.load(f)

        now = datetime.now()
        schedule_str = f"{sc['hour']:02d}:{sc['minute']:02d}"

      
        dist = get_distance()
        status["distance"] = dist
        status["current_time"] = f"{now.hour:02d}:{now.minute:02d}"
        status["next_time"] = schedule_str
        status["feeding"] = False

        if dist < 15:
           
            beep()
            time.sleep(2)
            continue

        
        if (now.hour == sc["hour"] and now.minute == sc["minute"] and now.second == 0):
            status["feeding"] = True
            play_melody_with_led() 
            servo_open()
            time.sleep(3)
            servo_close()
            status["feeding"] = False
            time.sleep(1)
            continue

     
        if last_minute_displayed != now.minute:
            last_minute_displayed = now.minute
     
        time.sleep(0.3)


t = threading.Thread(target=lambda: app.run(host="0.0.0.0", port=5000, debug=False))
t.daemon = True
t.start()


try:
    main_loop()
except KeyboardInterrupt:
    pass
finally:
    servo.stop()
    GPIO.cleanup()
