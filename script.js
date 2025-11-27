function updateStatus() {
    fetch("/status")
        .then(res => res.json())
        .then(data => {
            document.getElementById("current_time").innerText = data.current_time;
            document.getElementById("schedule").innerText = data.schedule;
            document.getElementById("status").innerText = data.status;
            document.getElementById("remaining").innerText = data.remaining;
        });
}

// 1초마다 자동 갱신
setInterval(updateStatus, 1000);
updateStatus();
