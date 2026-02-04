const API = "http://127.0.0.1:5000";
let chart;

// ---------------- PAGE DETECTION ----------------
const isLoginPage = document.getElementById("email");
const isDashboardPage = document.getElementById("statusCard");

// ---------------- LOGIN PAGE ----------------
function login() {
    const email = document.getElementById("email").value;
    const password = document.getElementById("password").value;

    fetch(`${API}/login`, {
        method: "POST",
        credentials: "include",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify({ email, password })
    })
    .then(res => res.json())
    .then(data => {
        if (data.message) {
            localStorage.setItem("role", data.role);
            window.location.href = "dashboard.html";
        } else {
            document.getElementById("message").innerText = data.error;
        }
    });
}

// ---------------- DASHBOARD LOAD ----------------
if (isDashboardPage) {
    document.getElementById("role").innerText =
        localStorage.getItem("role");
}

// ---------------- RUN PREDICTION ----------------
function runPrediction() {
    fetch(`${API}/predict`, {
        method: "POST",
        credentials: "include"
    })
    .then(res => res.json())
    .then(data => {
        updateStatus(data.prediction, data.alert);
        drawChart(data.prediction);
    });
}

// ---------------- STATUS UPDATE ----------------
function updateStatus(prediction, alert) {
    const start = prediction[0];
    const end = prediction[prediction.length - 1];
    const drop = start - end;

    const card = document.getElementById("statusCard");
    const text = document.getElementById("statusText");
    const desc = document.getElementById("statusDesc");
    const advice = document.getElementById("adviceText");

    card.className = "card";

    if (alert) {
        card.classList.add("critical");
        text.innerText = "🚨 CRITICAL";
        desc.innerText = "Water level may reduce significantly";
        advice.innerText =
            "Reduce water usage. Avoid flood irrigation. Use drip irrigation.";
        speak("Warning. Groundwater level may become critical.");
    } else if (drop > 0.3) {
        card.classList.add("warning");
        text.innerText = "⚠️ WARNING";
        desc.innerText = "Possible water level reduction";
        advice.innerText =
            "Use water carefully. Monitor irrigation.";
    } else {
        card.classList.add("safe");
        text.innerText = "🟢 SAFE";
        desc.innerText = "Water level is stable";
        advice.innerText =
            "Normal irrigation is safe.";
    }
}

// ---------------- GRAPH ----------------
function drawChart(data) {
    const ctx = document.getElementById("waterChart");

    if (chart) chart.destroy();

    chart = new Chart(ctx, {
        type: "line",
        data: {
            labels: data.map((_, i) => `Day ${i + 1}`),
            datasets: [{
                label: "Water Level (m)",
                data,
                borderColor: "#3498db",
                tension: 0.4
            }]
        }
    });
}

//
