// content-script.js

if (!document.getElementById("shieldbox-container")) {
  const root = document.createElement("div");
  root.id = "shieldbox-container";
  root.attachShadow({ mode: "open" });

  const shadowRoot = root.shadowRoot;

  shadowRoot.innerHTML = `
    <style>
      .floating-box {
        position: fixed;
        top: 100px;
        right: 20px;
        width: 320px;
        background: rgba(30, 30, 30, 0.9);
        border-radius: 16px;
        box-shadow: 0 4px 20px rgba(0,0,0,0.4);
        padding: 20px;
        color: white;
        font-family: 'Segoe UI', sans-serif;
        z-index: 999999;
        user-select: none;
        backdrop-filter: blur(10px);
      }

      .floating-box.dark {
        background: rgba(255, 255, 255, 0.95);
        color: #111;
      }

      .floating-box h3 {
        margin-top: 0;
      }

      .toggle-row {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 10px;
      }

      .result-box {
        margin-top: 10px;
        padding: 10px;
        background: #222;
        border-radius: 10px;
      }

      .dark .result-box {
        background: #f0f0f0;
        color: #222;
      }

      .drag-handle {
        width: 100%;
        cursor: move;
        margin-bottom: 10px;
        font-weight: bold;
        text-align: center;
      }

      input[type="checkbox"] {
        transform: scale(1.2);
      }

      .iot-status {
        margin-top: 8px;
        font-size: 13px;
        color: #00cc66;
      }
    </style>

    <div class="floating-box" id="panel">
      <div class="drag-handle" id="dragHandle">☰ Shield Box</div>

      <div class="toggle-row">
        <label>Auto Scan</label>
        <input type="checkbox" id="autoScan">
      </div>

      <div class="toggle-row">
        <label>Dark Mode</label>
        <input type="checkbox" id="darkMode">
      </div>

      <div class="toggle-row">
        <label>IoT Alert</label>
        <input type="checkbox" id="iotToggle">
      </div>

      <div class="result-box" id="emailResult">
        <strong>Email Status:</strong> Waiting for scan...
      </div>

      <div class="iot-status" id="espStatus">ESP32 Alert: Not Sent</div>
    </div>
  `;

  document.body.appendChild(root);

  // ======= DRAGGABLE LOGIC =======
  const panel = shadowRoot.getElementById("panel");
  const dragHandle = shadowRoot.getElementById("dragHandle");
  let isDragging = false, offsetX = 0, offsetY = 0;

  dragHandle.addEventListener("mousedown", e => {
    isDragging = true;
    offsetX = e.clientX - panel.getBoundingClientRect().left;
    offsetY = e.clientY - panel.getBoundingClientRect().top;
    document.addEventListener("mousemove", onMouseMove);
    document.addEventListener("mouseup", () => isDragging = false, { once: true });
  });

  function onMouseMove(e) {
    if (!isDragging) return;
    panel.style.top = `${e.clientY - offsetY}px`;
    panel.style.right = 'unset';
    panel.style.left = `${e.clientX - offsetX}px`;
  }

  // ======= TOGGLE DARK MODE =======
  const darkToggle = shadowRoot.getElementById("darkMode");
  const container = shadowRoot.querySelector(".floating-box");

  if (localStorage.getItem("shieldbox-dark") === "true") {
    container.classList.add("dark");
    darkToggle.checked = true;
  }

  darkToggle.addEventListener("change", () => {
    container.classList.toggle("dark");
    localStorage.setItem("shieldbox-dark", darkToggle.checked);
  });

  // ======= SIMULATE EMAIL SCAN + IOT ALERT =======
  const autoScan = shadowRoot.getElementById("autoScan");
  const iotToggle = shadowRoot.getElementById("iotToggle");
  const resultBox = shadowRoot.getElementById("emailResult");
  const espStatus = shadowRoot.getElementById("espStatus");

  autoScan.addEventListener("change", () => {
    if (autoScan.checked) {
      simulateScan();
    } else {
      resultBox.innerHTML = `<strong>Email Status:</strong> Waiting for scan...`;
      espStatus.innerText = `ESP32 Alert: Not Sent`;
    }
  });

  function simulateScan() {
    // Mock scan result
    resultBox.innerHTML = `<strong>Email Status:</strong> 🚨 Phishing detected in subject: <em>"Reset your password!"</em>`;

    // Send alert if enabled
    if (iotToggle.checked) {
      fetch("http://<ESP32_IP>/alert", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ message: "Phishing Email Detected" })
      }).then(() => {
        espStatus.innerText = "ESP32 Alert: ✅ Sent";
      }).catch(() => {
        espStatus.innerText = "ESP32 Alert: ❌ Failed";
      });
    } else {
      espStatus.innerText = "ESP32 Alert: Off";
    }
  }
}
