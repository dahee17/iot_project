from flask import Flask, render_template, request, redirect
import json

app = Flask(__name__)
SCHEDULE_FILE = "schedule.json"

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        hour = int(request.form["hour"])
        minute = int(request.form["minute"])

        with open(SCHEDULE_FILE, "w") as f:
            json.dump({"hour": hour, "minute": minute}, f)

        return redirect("/")

    with open(SCHEDULE_FILE, "r") as f:
        schedule = json.load(f)

    return render_template("index.html", schedule=schedule)

def start_flask():
    app.run(host="0.0.0.0", port=5000, debug=False)
