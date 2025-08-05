console.log("floatingpanel.js loaded");

function initializeFloatingPanel(shadow, container) {
  const scanBtn = shadow.getElementById("scanBtn");
  const urlInput = shadow.getElementById("urlInput");
  const manualLinkResult = shadow.getElementById("manual-link-result");
  const scanEmailBtn = shadow.getElementById("scanEmailBtn");
  const manualEmailResult = shadow.getElementById("manual-email-result");
  const autoScanResult = shadow.getElementById("auto-scan-result");

  // Manual link scan
  if (scanBtn && urlInput && manualLinkResult) {
    scanBtn.addEventListener("click", () => {
      const url = urlInput.value.trim();
      if (!url) {
        const msg = "Please enter a URL.";
        manualLinkResult.textContent = msg;
        console.log("[ShieldBox]", msg);
        return;
      }
      // Basic URL format validation
      const urlPattern = /^(https?:\/\/)?([a-zA-Z0-9-]+\.)+[a-zA-Z]{2,}(\/.*)?$/;
      if (!urlPattern.test(url)) {
        const msg = "Please enter a valid URL.";
        manualLinkResult.textContent = msg;
        console.log("[ShieldBox]", msg);
        return;
      }
      manualLinkResult.textContent = "Scanning...";
      manualLinkResult.className = "result-box scanning";
      console.log("[ShieldBox] Scanning URL:", url);
      const msg = { action: "scanLink", data: url };
      console.log("[ShieldBox] Sending message:", msg);
      chrome.runtime.sendMessage(msg, (response) => {
        console.log("[ShieldBox] Got response:", response);
        if (response?.result) {
          const status = response.result.status || "Unknown";
          manualLinkResult.textContent = `Status: ${status.toUpperCase()}`;
          // Apply CSS class based on status
          if (status.toLowerCase() === "safe") {
            manualLinkResult.className = "result-box safe";
            console.log("[ShieldBox] Applied CSS class: safe");
          } else if (status.toLowerCase() === "phishing") {
            manualLinkResult.className = "result-box phishing";
            console.log("[ShieldBox] Applied CSS class: phishing");
          } else {
            manualLinkResult.className = "result-box";
            console.log("[ShieldBox] Applied CSS class: default");
          }
        } else {
          manualLinkResult.textContent = "Scan failed. Please try again.";
          manualLinkResult.className = "result-box neutral";
          console.error("[ShieldBox] No response or error in response.");
        }
      });
    });
  }

  // Email scan
  if (scanEmailBtn && manualEmailResult) {
    scanEmailBtn.addEventListener("click", () => {
      console.log("[ShieldBox] Manual email scan triggered.");
      manualEmailResult.textContent = "Scanning email content...";
      manualEmailResult.className = "result-box scanning";
      chrome.runtime.sendMessage({ action: "request_email_extraction" }, (response) => {
        if (!response || response.error) {
          console.error("[ShieldBox] Failed to extract email:", response?.error);
          manualEmailResult.textContent = "Could not extract email content.";
          manualEmailResult.className = "result-box neutral";
          return;
        }
        const emailData = response.email;
        console.log("[ShieldBox] Extracted email data:", emailData);
        // Now send to backend
        fetch("http://127.0.0.1:5000/scan-email", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify(emailData)
        })
          .then(res => res.json())
          .then(result => {
            manualEmailResult.textContent = `Status: ${result.status.toUpperCase()} (${result.reason})`;
            // Apply CSS class based on status
            if (result.status.toLowerCase() === "safe" || result.status.toLowerCase() === "legitimate") {
              manualEmailResult.className = "result-box safe";
              console.log("[ShieldBox] Applied CSS class: safe");
            } else if (result.status.toLowerCase() === "fraudulent" || result.status.toLowerCase() === "phishing") {
              manualEmailResult.className = "result-box fraudulent";
              console.log("[ShieldBox] Applied CSS class: fraudulent"); 
            } else {
              manualEmailResult.className = "result-box";
              console.log("[ShieldBox] Applied CSS class: default");
            }
          })
          .catch(err => {
            console.error("Error sending email to backend:", err);
            manualEmailResult.textContent = "Error contacting server.";
            manualEmailResult.className = "result-box neutral";
          });
      });
    });
  }
          } else {
            manualEmailResult.className = "result-box";
            console.log("[ShieldBox] Applied CSS class: default");
          }ainer) {
  // --- Elements ---
  const scanBtn = shadow.getElementById("scanBtn");
  const urlInput = shadow.getElementById("urlInput");
  const manualLinkResult = shadow.getElementById("manual-link-result");
  const manualEmailResult = shadow.getElementById("manual-email-result");
  const scanEmailBtn = shadow.getElementById("scanEmailBtn");
  const autoScanResult = shadow.getElementById("auto-scan-result");

  // Manual link scan
  if (scanBtn && urlInput && manualLinkResult) {
    scanBtn.addEventListener("click", () => {
      const url = urlInput.value.trim();
      if (!url) {
        const msg = "Please enter a URL.";
        manualLinkResult.textContent = msg;
        console.log("[ShieldBox]", msg);
        return;
      }
      // Basic URL format validation
      const urlPattern = /^(https?:\/\/)?([a-zA-Z0-9-]+\.)+[a-zA-Z]{2,}(\/.*)?$/;
      if (!urlPattern.test(url)) {
        const msg = "Please enter a valid URL.";
        manualLinkResult.textContent = msg;
        console.log("[ShieldBox]", msg);
        return;
      }
      manualLinkResult.textContent = "Scanning...";
      manualLinkResult.className = "result-box scanning";
      console.log("[ShieldBox] Scanning URL:", url);
      const msg = { action: "scanLink", data: url };
      console.log("[ShieldBox] Sending message:", msg);
      chrome.runtime.sendMessage(msg, (response) => {
        console.log("[ShieldBox] Got response:", response);
        if (response?.result) {
          const status = response.result.status || "Unknown";
          manualLinkResult.textContent = `Status: ${status.toUpperCase()}`;
          // Apply CSS class based on status
          if (status.toLowerCase() === "safe") {
            manualLinkResult.className = "result-box safe";
            console.log("[ShieldBox] Applied CSS class: safe");
          } else if (status.toLowerCase() === "phishing") {
            manualLinkResult.className = "result-box phishing";
            console.log("[ShieldBox] Applied CSS class: phishing");
          } else {
            manualLinkResult.className = "result-box";
            console.log("[ShieldBox] Applied CSS class: default");
          }
        } else {
          manualLinkResult.textContent = "Scan failed. Please try again.";
          manualLinkResult.className = "result-box neutral";
          console.error("[ShieldBox] No response or error in response.");
        }
      });
    });
  }

  // Email scan
  if (scanEmailBtn && manualEmailResult) {
    scanEmailBtn.addEventListener("click", () => {
      console.log("[ShieldBox] Manual email scan triggered.");
      manualEmailResult.textContent = "Scanning email content...";
      manualEmailResult.className = "result-box scanning";
      chrome.runtime.sendMessage({ action: "request_email_extraction" }, (response) => {
        if (!response || response.error) {
          console.error("[ShieldBox] Failed to extract email:", response?.error);
          manualEmailResult.textContent = "Could not extract email content.";
          manualEmailResult.className = "result-box neutral";
          return;
        }
        const emailData = response.email;
        console.log("[ShieldBox] Extracted email data:", emailData);
        // Now send to backend
        fetch("http://127.0.0.1:5000/scan-email", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify(emailData)
        })
          .then(res => res.json())
          .then(result => {
            manualEmailResult.textContent = `Status: ${result.status.toUpperCase()} (${result.reason})`;
            // Apply CSS class based on status
            if (result.status.toLowerCase() === "safe" || result.status.toLowerCase() === "legitimate") {
              manualEmailResult.className = "result-box safe";
              console.log("[ShieldBox] Applied CSS class: safe");
            } else if (result.status.toLowerCase() === "fraudulent" || result.status.toLowerCase() === "phishing") {
              manualEmailResult.className = "result-box fraudulent";
              console.log("[ShieldBox] Applied CSS class: fraudulent"); 
            } else {
              manualEmailResult.className = "result-box";
              console.log("[ShieldBox] Applied CSS class: default");
            }
          })
          .catch(err => {
            console.error("Error sending email to backend:", err);
            manualEmailResult.textContent = "Error contacting server.";
            manualEmailResult.className = "result-box neutral";
          });
      });
    });
  }

  // 🔁 Listen for result updates
  // (Listener moved outside for robustness)

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

  // After all element setup, always update auto-scan-result if we have a cached value
  if (autoScanResult && window.lastAutoScanResult) {
    autoScanResult.textContent = window.lastAutoScanResult;
    console.log("[ShieldBox FloatingPanel] Restored cached auto-scan-result after reinjection:", window.lastAutoScanResult);
  }
}

function injectFloatingPanel() {
  if (document.getElementById('shieldbox-floating-panel')) {
    // Already injected
    return;
  }
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
      // Inject CSS with cache-busting
      const cssUrl = chrome.runtime.getURL('style.css') + '?v=' + Date.now();
      fetch(cssUrl)
        .then(res => res.text())
        .then(css => {
          const styleTag = document.createElement('style');
          styleTag.textContent = css;
          shadow.appendChild(styleTag);
        });
      document.body.appendChild(container);
      initializeFloatingPanel(shadow, container);
    });
}

// Initial injection
injectFloatingPanel();

// MutationObserver to reinject if removed (SPA robustness)
const observer = new MutationObserver(() => {
  if (!document.getElementById('shieldbox-floating-panel')) {
    injectFloatingPanel();
  }
});
observer.observe(document.body, { childList: true, subtree: false });

let lastAutoScanResult = null;

// Persistent message listener for auto scan result display
chrome.runtime.onMessage.addListener((message) => {
  if (message.action === "displayAutoScanResult") {
    lastAutoScanResult = message.result;
    const shadowRoot = document.querySelector('#shieldbox-floating-panel')?.shadowRoot;
    const autoScanResult = shadowRoot?.getElementById("auto-scan-result");
    if (autoScanResult) {
      autoScanResult.textContent = message.result;
      console.log("[ShieldBox FloatingPanel] Updated auto-scan-result:", message.result);
    } else {
      console.warn("[ShieldBox FloatingPanel] auto-scan-result not found in shadow DOM");
    }
    const external = document.getElementById("auto-email-result");
    if (external) external.textContent = message.result;
  }
});
