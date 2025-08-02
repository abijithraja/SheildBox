document.addEventListener("DOMContentLoaded", () => {
  const darkToggle = document.getElementById("darkToggle");
  const container = document.getElementById("themeContainer");

  // Load saved dark mode
  const isDark = localStorage.getItem("darkMode") === "true";
  container.classList.toggle("dark", isDark);
  container.classList.toggle("light", !isDark);
  darkToggle.textContent = isDark ? "🌙" : "☀️";

  // Toggle dark mode
  darkToggle.addEventListener("click", () => {
    const currentDark = container.classList.contains("dark");
    container.classList.toggle("dark", !currentDark);
    container.classList.toggle("light", currentDark);
    darkToggle.textContent = currentDark ? "☀️" : "🌙";
    localStorage.setItem("darkMode", !currentDark);
  });

  // Toggle logic
  document.getElementById("autoScanToggle").addEventListener("change", (e) => {
    console.log("Auto Scan:", e.target.checked);
    localStorage.setItem("autoScan", e.target.checked);
  });

  document.getElementById("iotToggle").addEventListener("change", (e) => {
    console.log("IoT Alert:", e.target.checked);
    localStorage.setItem("iotAlert", e.target.checked);
  });

  // Simulate email scan result (replace with real backend call later)
  // Sample fake scan on load (or add Scan button if needed)
  simulateScanAndIoT();
});

// Simulated scan + IoT alert logic (can replace with real Gmail scan later)
function simulateScanAndIoT() {
  fetch("http://localhost:5000/scan_url", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ url: "https://suspicious.example.com" })
  })
    .then(res => res.json())
    .then(data => {
      const { risk_score, status } = data;

      document.getElementById("emailResult").textContent = `Result: ${status}`;
      const useIoT = localStorage.getItem("iotAlert") === "true";

      if (useIoT && risk_score > 60) {
        fetch("http://<ESP32_IP>/alert", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ message: "Suspicious Email Detected" })
        })
          .then(() => {
            document.getElementById("iotStatus").textContent = "✅ Alert sent to IoT device";
          })
          .catch(() => {
            document.getElementById("iotStatus").textContent = "❌ Failed to send alert";
          });
      } else {
        document.getElementById("iotStatus").textContent = "✅ No alert needed";
      }
    })
    .catch(() => {
      document.getElementById("emailResult").textContent = "Error scanning email.";
      document.getElementById("iotStatus").textContent = "⚠️ No scan result";
    });
}
