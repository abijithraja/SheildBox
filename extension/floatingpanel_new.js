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

  // Listen for result updates
  chrome.runtime.onMessage.addListener((message, sender, sendResponse) => {
    console.log("[ShieldBox FloatingPanel] Message received:", message);

    if (message.action === "displayAutoScanResult" && autoScanResult) {
      window.lastAutoScanResult = message.result;
      autoScanResult.textContent = message.result;
      console.log("[ShieldBox FloatingPanel] Auto-scan result updated:", message.result);

      // Apply CSS class based on result status
      if (message.result.toLowerCase().includes("safe") || message.result.toLowerCase().includes("legitimate")) {
        autoScanResult.className = "result-box safe";
      } else if (message.result.toLowerCase().includes("fraudulent") || message.result.toLowerCase().includes("phishing")) {
        autoScanResult.className = "result-box fraudulent";
      } else {
        autoScanResult.className = "result-box neutral";
      }
    }
  });

  // Dark mode toggle
  const darkModeToggle = shadow.getElementById("darkModeToggle");
  if (darkModeToggle && container) {
    // Load saved dark mode preference
    chrome.storage.sync.get("darkMode", (data) => {
      const isDarkMode = data.darkMode || false;
      darkModeToggle.checked = isDarkMode;
      if (isDarkMode) {
        container.classList.add("dark-mode");
      }
    });

    darkModeToggle.addEventListener("change", () => {
      const isDarkMode = darkModeToggle.checked;
      chrome.storage.sync.set({ darkMode: isDarkMode });
      if (isDarkMode) {
        container.classList.add("dark-mode");
      } else {
        container.classList.remove("dark-mode");
      }
    });
  }

  // Auto scan toggle
  const autoScanToggle = shadow.getElementById("autoScanToggle");
  if (autoScanToggle) {
    // Load saved auto scan preference
    chrome.storage.sync.get("autoScan", (data) => {
      const isAutoScanEnabled = data.autoScan !== false; // Default to true
      autoScanToggle.checked = isAutoScanEnabled;
    });

    autoScanToggle.addEventListener("change", () => {
      const isAutoScanEnabled = autoScanToggle.checked;
      chrome.storage.sync.set({ autoScan: isAutoScanEnabled });
      console.log("[ShieldBox] Auto scan toggled:", isAutoScanEnabled);
    });
  }

  // IoT toggle
  const iotToggle = shadow.getElementById("iotToggle");
  if (iotToggle) {
    // Load saved IoT preference
    chrome.storage.sync.get("iotEnabled", (data) => {
      const isIotEnabled = data.iotEnabled !== false; // Default to true
      iotToggle.checked = isIotEnabled;
    });

    iotToggle.addEventListener("change", () => {
      const isIotEnabled = iotToggle.checked;
      chrome.storage.sync.set({ iotEnabled: isIotEnabled });
      console.log("[ShieldBox] IoT alerts toggled:", isIotEnabled);
    });
  }

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
      container.style.right = '20px';
      container.style.zIndex = '10000';
      container.style.fontFamily = 'Arial, sans-serif';

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

// Export for debugging
window.shieldBoxFloatingPanel = {
  injectFloatingPanel,
  lastAutoScanResult: () => lastAutoScanResult
};
