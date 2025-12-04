if dist < 15:
    feeding_status = "Countdown"

    now = datetime.now()
    sc_hour = sc["hour"]
    sc_min = sc["minute"]

    today_target = now.replace(hour=sc_hour, minute=sc_min, second=0, microsecond=0)
    tomorrow_target = today_target + timedelta(days=1)

    diff = (today_target - now).total_seconds()
    if diff < 0:
        diff = (tomorrow_target - now).total_seconds()

    h = int(diff // 3600)
    m = int((diff % 3600) // 60)
    s = int(diff % 60)

    remaining_text = f"{h}h {m}m {s}s"

    if not beeped:
        GPIO.output(BUZZER_PIN, 1)
        time.sleep(0.2)
        GPIO.output(BUZZER_PIN, 0)
        beeped = True
            
    time.sleep(0.3)
    continue
