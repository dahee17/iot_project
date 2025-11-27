import RPi.GPIO as GPIO
import time
import threading
import json
from datetime import datetime
from flask import Flask, render_template, request, jsonify

app = Flask(__name__)
SCHEDULE_FILE = "schedule.json"

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

feeding_status = "Idle"
remaining_text = ""

def load_schedule():
    with open(SCHEDULE_FILE, "r") as f:
        return json.load(f)

def save_schedule(h, m):
    with open(
