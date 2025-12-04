import RPi.GPIO as GPIO
import time
import threading
import json
from datetime import datetime
from flask import Flask, render_template, request, jsonify, redirect, url_for

app = Flask(__name__)
SCHEDULE_FILE = "./schedule.json"

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
beeped = False

def load_schedule():
    try:
        with open(SCHEDULE_FILE, "r") as f:
            return json.load(f)
    except:
        return {"hour": 0, "minute": 0}

def save_schedule(h, m):
    with open(SCHEDULE_FILE, "w") as f:
        json.dump({"hour": h, "minute": m}, f)

def servo_set(dc):
    servo.ChangeDutyCycle(dc)
    time.sleep(1)
    servo.ChangeDutyCycle(0)

def servo_open():
    servo_set(7)

def servo_close():
    servo_set(2)

def play_melody_with_led():
    global feeding_status
    feeding_status = "Feeding"
    GPIO.output(LED_PIN, 1)
    buz = GPIO.PWM(BUZZER_PIN, 440)
    buz.start(50)
    notes = [(262, 0.4), (330, 0.4), (392, 0.4), (523, 0.4)]
    for freq, dur in notes:
        buz.ChangeFrequency(freq)
        time.sleep(dur)
    buz.stop()
    GPIO.output(LED_PIN, 0)

def get_distance():
    GPIO.output(TRIG, 1)
    time.sleep(0.00001)
    GPIO.output(TRIG, 0)
    start = time.time()
    end = time.time()
    while GPIO.input(ECHO) == 0:
        start = time.time()
    while GPIO.input(ECHO) == 1:
        end = time.time()
    distance = (end - start) * 34300 / 2
    return distance

def main_loop():
    global feeding_status, remaining_text, beeped

    countdown_start = None
    completed_start = None
    feeding_done = False

    COUNTDOWN_TIMEOUT = 5
    COMPLETED_TIMEOUT = 10

    while True:
        sc = load_schedule()
        now = datetime.now()
        target_minutes = sc["hour"]*60 + sc["minute"]
        now_minutes = now.hour*60 + now.minute
        remaining = max(target_minutes - now_minutes, 0)

        if feeding_status == "Completed":
            if completed_start and time.time() - completed_start >= COMPLETED_TIMEOUT:
                feeding_status = "Idle"
                remaining_text = ""
                completed_start = None

        if feeding_status == "Countdown":
            if countdown_start and time.time() - countdown_start >= COUNTDOWN_TIMEOUT:
                feeding_status = "Idle"
                remaining_text = ""
                countdown_start = None

        dist = get_distance()
        if dist < 15:
            feeding_status = "Countdown"
            if countdown_start is None:
                countdown_start = time.time()
            h = remaining // 60
            m = remaining % 60
            remaining_text = f"{h}h {m}m left"
            if not beeped:
                GPIO.output(BUZZER_PIN, 1)
                time.sleep(0.2)
                GPIO.output(BUZZER_PIN, 0)
                beeped = True
            time.sleep(0.3)
            continue
        else:
            beeped = False

        if now.hour == sc["hour"] and now.minute == sc["minute"] and not feeding_done:
            feeding_done = True
            feeding_status = "Feeding"
            remaining_text = ""
            play_melody_with_led()
            servo_open()
            time.sleep(3)
            servo_close()
            feeding_status = "Completed"
            completed_start = time.time()
            continue

        if now.hour != sc["hour"] or now.minute != sc["minute"]:
            feeding_done = False

        if feeding_status not in ["Feeding", "Completed", "Countdown"]:
            feeding_status = "Idle"
            remaining_text = ""

        time.sleep(0.5)

@app.route("/")
def index():
    schedule = load_schedule()
    return render_template("index.html", schedule=schedule)

@app.route("/set", methods=["POST"])
def set_time():
    h = int(request.form["hour"])
    m = int(request.form["minute"])
    save_schedule(h, m)
    return redirect(url_for("index"))

@app.route("/status")
def status():
    now = datetime.now()
    sc = load_schedule()
    return jsonify({
        "current_time": now.strftime("%H:%M:%S"),
        "schedule": f"{sc['hour']:02d}:{sc['minute']:02d}",
        "status": feeding_status,
        "remaining": remaining_text
    })

def start_flask():
    app.run(host="0.0.0.0", port=5000, debug=False)

t = threading.Thread(target=start_flask)
t.daemon = True
t.start()

try:
    main_loop()
except KeyboardInterrupt:
    pass
finally:
    servo.stop()
    GPIO.cleanup()
