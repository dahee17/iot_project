from flask import Flask, render_template, request, jsonify, redirect
import json

app = Flask(__name__)
SCHEDULE_FILE = "schedule.json"

status = {
    "current_time": "00:00",
    "next_time": "00:00",
    "feeding": False,
    "distance": 0
}

@app.route("/", methods=["GET"])
def index():
    with open(SCHEDULE_FILE, "r") as f:
        schedule = json.load(f)
    return render_template("index.html", schedule=schedule)

@app.route("/save_time", methods=["POST"])
def save_time():
    hour = int(request.form["hour"])
    minute = int(request.form["minute"])

    with open(SCHEDULE_FILE, "w") as f:
        json.dump({"hour": hour, "minute": minute}, f)

    return redirect("/")
    

@app.route("/status")
def get_status():
    return jsonify(status)
