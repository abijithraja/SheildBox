document.getElementById("scanButton").addEventListener("click", () => {
  const url = document.getElementById("urlInput").value.trim();
  if (!url) return;

  fetch("http://localhost:5000/scan_url", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ url: url })
  })
    .then(res => res.json())
    .then(data => {
      const { risk_score, status } = data; // Assume 0–100 score
      document.getElementById("scanResult").innerText = `Result: ${status}`;
      document.getElementById("riskBar").style.width = `${risk_score}%`;
      document.getElementById("riskBar").style.backgroundColor = risk_score > 60 ? "red" : (risk_score > 30 ? "orange" : "green");

      // Optional: Notify ESP32 (if risk is high)
      if (risk_score > 60) {
        fetch("http://<ESP32_IP>/alert", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ message: "Suspicious Link Found" })
        }).then(() => {
          document.getElementById("espStatus").innerText = "ESP32 Alert:  Sent";
        }).catch(() => {
          document.getElementById("espStatus").innerText = "ESP32 Alert:  Failed";
        });
      }
    })
    .catch(() => {
      document.getElementById("scanResult").innerText = "Error scanning URL.";
    });
    document.addEventListener("DOMContentLoaded", () => {
  const toggle = document.getElementById("darkToggle");

  // Load saved theme
  if (localStorage.getItem("darkMode") === "true") {
    document.body.classList.add("dark");
    toggle.checked = true;
  }

  toggle.addEventListener("change", () => {
    document.body.classList.toggle("dark");
    localStorage.setItem("darkMode", toggle.checked);
  });

  // Dummy Scan button (optional)
  document.querySelector("button").addEventListener("click", () => {
    alert("This is a dummy scan. Backend not connected yet.");
  });
});
});
