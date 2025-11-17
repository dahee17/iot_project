import RPi.GPIO as GPIO
import time
from RPLCD.i2c import CharLCD

GPIO.setmode(GPIO.BCM)

TRIG = 23
ECHO = 24
GPIO.setup(TRIG, GPIO.OUT)
GPIO.setup(ECHO, GPIO.IN)

BUZZER = 12
GPIO.setup(BUZZER, GPIO.OUT)

lcd = CharLCD('PCF8574', 0x27)  # I2C 주소 확인 필요

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

def beep(duration=0.2):
    GPIO.output(BUZZER, True)
    time.sleep(duration)
    GPIO.output(BUZZER, False)

def lcd_print(line1, line2=""):
    lcd.clear()
    lcd.write_string(line1)
    lcd.cursor_pos = (1,0)
    lcd.write_string(line2)

try:
    while True:
        distance = get_distance()

        if distance <= 15:
            lcd_print("접근 감지!", f"거리: {distance}cm")
            beep(0.2)
        else:
            lcd_print("대기중...", f"거리: {distance}cm")

        time.sleep(0.5)

except KeyboardInterrupt:
    GPIO.cleanup()
    lcd.clear()
