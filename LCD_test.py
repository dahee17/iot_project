from RPLCD.i2c import CharLCD
import time

# LCD 설정 (주소는 i2cdetect로 확인)
lcd = CharLCD('PCF8574', 0x27)  # 또는 0x3F

try:
    while True:
        lcd.clear()
        lcd.write_string("Hello, World!")
        lcd.cursor_pos = (1, 0)
        lcd.write_string("LCD Test 123")
        time.sleep(2)

        lcd.clear()
        lcd.write_string("Line1: Test")
        lcd.cursor_pos = (1,0)
        lcd.write_string("Line2: 456")
        time.sleep(2)

except KeyboardInterrupt:
    lcd.clear()
