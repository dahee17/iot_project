import RPi.GPIO as GPIO
import time
import threading
import json
from datetime import datetime
from flask import Flask, render_template

# -------------------- Flask 설정 --------------------
app = Flask(__name__)
SCHEDULE_FILE = "schedule.json"

@app.route("/")
def index():
    # schedule 읽기
    with open(SCHEDULE_FILE, "r") as f:
        sc = json.load(f)
    now = datetime.now()
    current_time = f"{now.hour:02d}:{now.minute:02d}"
    next_time = f"{sc['hour']:02d}:{sc['minute']:02d}"
    return render_template("index.html", current_time=current_time, next_time=next_time)

def start_flask():
    app.run(host="0.0.0.0", port=5000, debug=False)

# -------------------- GPIO 설정 --------------------
SERVO_PIN = 18   # 서보 (여전히 필요하면)
BUZZER_PIN = 15
LED_PIN = 14     # 새 LED 핀
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

# -------------------- 서보 제어 --------------------
def servo_open():
    servo.ChangeDutyCycle(7)
    time.sleep(1)
    servo.ChangeDutyCycle(0)

def servo_close():
    servo.ChangeDutyCycle(2)
    time.sleep(1)
    servo.ChangeDutyCycle(0)

# -------------------- 부저 & LED --------------------
def beep(duration=0.2):
    GPIO.output(BUZZER_PIN, 1)
    time.sleep(duration)
    GPIO.output(BUZZER_PIN, 0)

def play_melody_with_led():
    # LED 켜기
    GPIO.output(LED_PIN, 1)
    buz = GPIO.PWM(BUZZER_PIN, 440)
    buz.start(50)

    notes = [
        (262, 0.4),  # 도
        (330, 0.4),  # 미
        (392, 0.4),  # 솔
        (523, 0.4)   # 높은도
    ]

    for freq, duration in notes:
        buz.ChangeFrequency(freq)
        time.sleep(duration)

    buz.stop()
    # LED 끄기 (배급 3초 기준)
    GPIO.output(LED_PIN, 0)

# -------------------- 초음파 --------------------
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

# -------------------- 메인 루프 --------------------
def main_loop():
    last_minute_displayed = None

    while True:
        # schedule 읽기
        with open(SCHEDULE_FILE, "r") as f:
            sc = json.load(f)

        now = datetime.now()
        schedule_str = f"{sc['hour']:02d}:{sc['minute']:02d}"

        # 1) 초음파 감지시 (15cm 이하)
        dist = get_distance()
        if dist < 15:
            remain = (sc["hour"]*60 + sc["minute"]) - (now.hour*60 + now.minute)
            remain = max(remain, 0)
            print(f"Next {schedule_str} | {remain} min left")
            beep()
            time.sleep(2)
            continue

        # 2) 배급 시간
        if (now.hour == sc["hour"] and now.minute == sc["minute"] and now.second == 0):
            print("FEEDING NOW!")
            play_melody_with_led()   # 부저+LED 3초
            servo_open()
            time.sleep(3)
            servo_close()
            time.sleep(1)
            continue

        # 3) 기본 상태 (웹에서 보여줄 내용은 print)
        if last_minute_displayed != now.minute:
            last_minute_displayed = now.minute
            print(f"Current time: {now.hour:02d}:{now.minute:02d} | Next: {schedule_str}")

        time.sleep(0.3)

# -------------------- Flask 스레드 실행 --------------------
t = threading.Thread(target=start_flask)
t.daemon = True
t.start()

# -------------------- 메인 실행 --------------------
try:
    main_loop()
except KeyboardInterrupt:
    pass
finally:
    servo.stop()
    GPIO.cleanup()
