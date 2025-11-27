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

GPIO.setmode(GPIO.BCM)
GPIO.setup(SERVO_PIN, GPIO.OUT)
GPIO.setup(BUZZER_PIN, GPIO.OUT)
GPIO.setup(LED_PIN, GPIO.OUT)

servo = GPIO.PWM(SERVO_PIN, 50)
servo.start(0)

feeding_status = "Idle"
remaining_text = ""


def load_schedule():
    try:
        with open(SCHEDULE_FILE, "r") as f:
            return json.load(f)
    except:
        return {"hour":0,"minute":0}

def save_schedule(h, m):
    with open(SCHEDULE_FILE, "w") as f:
        json.dump({"hour":h,"minute":m}, f)


def servo_open():
    servo.ChangeDutyCycle(7)
    time.sleep(1)

def servo_close():
    servo.ChangeDutyCycle(2)
    time.sleep(1)

def play_melody_with_led():
    global feeding_status
    feeding_status = "Feeding"

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

# -------------------
# Main Loop
# -------------------
def main_loop():
    global feeding_status, remaining_text

    while True:
        sc = load_schedule()
        now = datetime.now()
        target_minutes = sc["hour"]*60 + sc["minute"]
        now_minutes = now.hour*60 + now.minute
        remaining = max(target_minutes - now_minutes, 0)

        # Feeding 시간 도달
        if now.hour == sc["hour"] and now.minute == sc["minute"] and now.second == 0:
            feeding_status = "Feeding"
            remaining_text = ""
            play_melody_with_led()
            servo_open()
            time.sleep(3)
            servo_close()
            feeding_status = "Completed"
            time.sleep(1)
            continue

        # Countdown 표시
        if remaining > 0:
            feeding_status = "Countdown"
            h = remaining // 60
            m = remaining % 60
            remaining_text = f"{h}h {m}m left"
        else:
            if feeding_status not in ["Feeding","Completed"]:
                feeding_status = "Idle"
                remaining_text = ""

        time.sleep(0.5)

# -------------------
# Flask Routes
# -------------------
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
