diff = (sc["hour"]*3600 + sc["minute"]*60) - (now.hour*3600 + now.minute*60 + now.second)
if diff < 0:
    diff = 0

h = diff // 3600
m = (diff % 3600) // 60
s = diff % 60

remaining_text = f"{h}h {m}m {s}s"
