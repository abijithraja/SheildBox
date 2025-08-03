console.log("floatingpanel.js loaded");

fetch(chrome.runtime.getURL('floatingpanel.html'))
  .then(res => res.text())
  .then(html => {
    const container = document.createElement('div');
    container.id = 'shieldbox-floating-panel';
    container.style.position = 'fixed';
    container.style.top = '100px';
    container.style.left = '100px';
    container.style.zIndex = '999999';

    const shadow = container.attachShadow({ mode: 'open' });
    shadow.innerHTML = html;

    // ✅ Inject CSS
    fetch(chrome.runtime.getURL('style.css'))
      .then(res => res.text())
      .then(css => {
        const styleTag = document.createElement('style');
        styleTag.textContent = css;
        shadow.appendChild(styleTag);
      });

    document.body.appendChild(container);

    // --- Elements ---
    const scanBtn = shadow.getElementById("scanBtn");
    const urlInput = shadow.getElementById("urlInput");
    const manualLinkResult = shadow.getElementById("manual-link-result");
    const manualEmailResult = shadow.getElementById("manual-email-result");
    const scanEmailBtn = shadow.getElementById("scanEmailBtn");
    const autoScanResult = shadow.getElementById("auto-scan-result");

    // ✅ Manual link scan
    if (scanBtn && urlInput && manualLinkResult) {
      scanBtn.addEventListener("click", () => {
        const url = urlInput.value.trim();
        if (!url) {
          manualLinkResult.textContent = "⚠️ Please enter a URL.";
          return;
        }

        manualLinkResult.textContent = "🔍 Scanning...";
        console.log("[ShieldBox] Scanning URL:", url);

        chrome.runtime.sendMessage({ action: "scanLink", data: url }, (response) => {
          console.log("[ShieldBox] Response from background:", response);
          if (response?.result) {
            const status = response.result.status || "Unknown";
            manualLinkResult.textContent = `🛡️ Status: ${status.toUpperCase()}`;
          } else {
            manualLinkResult.textContent = "❌ Scan failed. Try again.";
          }
        });
      });
    }

    // 📩 Email scan
    if (scanEmailBtn && manualEmailResult) {
      scanEmailBtn.addEventListener("click", () => {
        manualEmailResult.textContent = "🔍 Scanning emails...";
        chrome.runtime.sendMessage({ action: "scanEmail" });
      });
    }

    // 🔁 Listen for result updates
    chrome.runtime.onMessage.addListener((message, sender, sendResponse) => {
      if (message.action === "displayResult") {
        if (message.source === "email") {
          manualEmailResult.textContent = message.result;
        } else if (message.source === "link") {
          manualLinkResult.textContent = message.result;
        }
      } else if (message.action === "displayAutoScanResult") {
        if (autoScanResult) autoScanResult.textContent = message.result;
        const external = document.getElementById("auto-email-result");
        if (external) external.textContent = message.result;
      }
    });

    // 🌗 Dark mode and Auto Scan toggle logic
    const interval = setInterval(() => {
      const darkModeToggle = shadow.getElementById("darkModeToggle");
      const autoScanToggle = shadow.getElementById("autoScanToggle");
      if (!darkModeToggle || !autoScanToggle) return;

      clearInterval(interval);

      function applyTheme(mode) {
        if (mode === "dark") {
          shadow.host.classList.add("dark-mode");
          darkModeToggle.checked = true;
        } else {
          shadow.host.classList.remove("dark-mode");
          darkModeToggle.checked = false;
        }
        localStorage.setItem("theme", mode);
      }

      const savedTheme = localStorage.getItem("theme");
      applyTheme(savedTheme || "light");

      darkModeToggle.addEventListener("change", () => {
        applyTheme(darkModeToggle.checked ? "dark" : "light");
      });

      if (chrome.storage && chrome.storage.local) {
        chrome.storage.local.get("autoScan", (data) => {
          autoScanToggle.checked = !!data.autoScan;
        });

        autoScanToggle.addEventListener("change", () => {
          chrome.storage.local.set({ autoScan: autoScanToggle.checked }, () => {
            console.log("[ShieldBox] Auto Scan set to:", autoScanToggle.checked);
          });
        });
      }
    }, 50);

    // 🖱️ Draggable
    let isDragging = false, offsetX = 0, offsetY = 0;

    container.onmousedown = (e) => {
      isDragging = true;
      offsetX = e.clientX - container.offsetLeft;
      offsetY = e.clientY - container.offsetTop;
    };

    document.onmousemove = (e) => {
      if (isDragging) {
        container.style.left = `${e.clientX - offsetX}px`;
        container.style.top = `${e.clientY - offsetY}px`;
      }
    };

    document.onmouseup = () => {
      isDragging = false;
    };
  });
