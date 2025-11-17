from flask import Flask, render_template, request, redirect
import json

app = Flask(__name__)

# 같은 폴더 안에 json 파일 생성하기
SCHEDULE_FILE = "schedule.json"

# 메인 페이지 (시간 설정)
@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        hour = int(request.form["hour"])
        minute = int(request.form["minute"])

        # JSON에 저장
        with open(SCHEDULE_FILE, "w") as f:
            json.dump({"hour": hour, "minute": minute}, f)

        return redirect("/")  # 갱신 후 페이지 재로딩

    # GET: 현재 저장된 시간 읽기
    with open(SCHEDULE_FILE, "r") as f:
        schedule = json.load(f)

    return f"""
    <h1>배급 시간 설정</h1>
    <form method="post">
        Hour: <input type="number" name="hour" min="0" max="23" value="{schedule['hour']}"><br>
        Minute: <input type="number" name="minute" min="0" max="59" value="{schedule['minute']}"><br>
        <input type="submit" value="저장">
    </form>
    <p>현재 설정: {schedule['hour']:02d}:{schedule['minute']:02d}</p>
    """

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
