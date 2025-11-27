setInterval(() => {
    fetch("/status")
        .then(res => res.json())
        .then(data => {
            document.getElementById("current_time").innerText = data.current_time;
            document.getElementById("schedule").innerText = data.schedule;
            document.getElementById("status").innerText = data.status;
            document.getElementById("remaining").innerText = data.remaining;
        });
}, 1000);

document.getElementById("timeForm").onsubmit = (e) => {
    e.preventDefault();
    const formData = new FormData(e.target);

    fetch("/set", {
        method: "POST",
        body: formData
    }).then(() => alert("Saved!"));
};
