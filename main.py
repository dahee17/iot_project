import RPi.GPIO as GPIO
import time
import threading
import json
from datetime import datetime

from webapp import start_flask

# ---------------------------------------------------------
# GPIO 핀 설정
# ---------------------------------------------------------
SERVO_PIN = 18
BUZZER_PIN = 23
TRIG = 24
ECHO = 25

GPIO.setmode(GPIO.BCM)
GPIO.setup(SERVO_PIN, GPIO.OUT)
GPIO.setup(BUZZER_PIN, GPIO.OUT)
GPIO.setup(TRIG, GPIO.OUT)
GPIO.setup(ECHO, GPIO.IN)

servo = GPIO.PWM(SERVO_PIN, 50)
servo.start(0)

# ---------------------------------------------------------
# LCD (I2C 1602)
# ---------------------------------------------------------
import smbus
I2C_ADDR = 0x27
LCD_WIDTH = 16
bus = smbus.SMBus(1)

def lcd_write(cmd, mode):
    bus.write_byte(I2C_ADDR, mode | (cmd & 0xF0))
    time.sleep(0.0005)
    bus.write_byte(I2C_ADDR, mode | ((cmd << 4) & 0xF0))
    time.sleep(0.0005)

def lcd_text(text, line):
    line_addr = [0x80, 0xC0]
    lcd_write(line_addr[line], 0)
    for ch in text.ljust(16):
        bus.write_byte(I2C_ADDR, 1 | ord(ch))
        time.sleep(0.001)

# ---------------------------------------------------------
# 서보 모터 제어
# ---------------------------------------------------------
def servo_open():
    servo.ChangeDutyCycle(7)  # 약 90도
    time.sleep(1)

def servo_close():
    servo.ChangeDutyCycle(2)  # 약 0도
    time.sleep(1)

# ---------------------------------------------------------
# 부저
# ---------------------------------------------------------
def beep():
    GPIO.output(BUZZER_PIN, 1)
    time.sleep(0.2)
    GPIO.output(BUZZER_PIN, 0)

# ---------------------------------------------------------
# 초음파 거리 측정
# ---------------------------------------------------------
def get_distance():
    GPIO.output(TRIG, 1)
    time.sleep(0.00001)
    GPIO.output(TRIG, 0)

    while GPIO.input(ECHO) == 0:
        start = time.time()

    while GPIO.input(ECHO) == 1:
        end = time.time()

    return (end - start) * 34300 / 2

# ---------------------------------------------------------
# 메인 루프
# ---------------------------------------------------------
def main_loop():
    while True:
        with open("schedule.json", "r") as f:
            sc = json.load(f)

        now = datetime.now()
        schedule_str = f"{sc['hour']:02d}:{sc['minute']:02d}"

        # --------- 초음파 감지 (15cm 이하) ----------
        dist = get_distance()
        if dist < 15:
            remain = (sc["hour"]*60 + sc["minute"]) - (now.hour*60 + now.minute)
            rem = max(remain, 0)
            lcd_text(f"Next {schedule_str}", 0)
            lcd_text(f"{rem} min left", 1)
            beep()
            time.sleep(2)

        # --------- 배급 시간 도달 ----------
        if now.hour == sc["hour"] and now.minute == sc["minute"] and now.second == 0:
            lcd_text("FEEDING NOW!", 0)
            servo_open()
            time.sleep(3)
            servo_close()

        time.sleep(0.5)

# ---------------------------------------------------------
# Flask 서버는 스레드로 실행
# ---------------------------------------------------------
t = threading.Thread(target=start_flask)
t.daemon = True
t.start()

# ---------------------------------------------------------
# 메인 실행
# ---------------------------------------------------------
try:
    main_loop()
except KeyboardInterrupt:
    pass
finally:
    servo.stop()
    GPIO.cleanup()
