let autoScanEnabled = true; // Default to enabled

chrome.storage.sync.get("autoScan", (data) => {
  console.log("[ShieldBox] autoEmailScanner.js loaded");
  console.log("[ShieldBox] autoScan value:", data.autoScan);
  autoScanEnabled = data.autoScan !== false; // Default to true
  if (autoScanEnabled) waitForEmailView();
});

chrome.storage.onChanged.addListener((changes, area) => {
  if (area === "sync" && changes.autoScan) {
    autoScanEnabled = changes.autoScan.newValue !== false;
    console.log("[ShieldBox] autoScan toggled:", autoScanEnabled);
    if (autoScanEnabled) {
      waitForEmailView();
    } else {
      // Clear the auto scan result when disabled
      updateAutoScanResultBox("Auto scan disabled");
      chrome.runtime.sendMessage({
        action: "displayAutoScanResult",
        result: "Auto scan disabled"
      });
    }
  }
});

let lastScannedId = null;
let emailPreviouslyDetected = false;

function waitForEmailView() {
  if (!autoScanEnabled) {
    console.log("[ShieldBox AutoScan] Auto scan is disabled. Not starting observer.");
    return;
  }
  
  const body = document.body;
  if (!body) {
    console.warn("[ShieldBox AutoScan] <body> not found. Retrying...");
    setTimeout(waitForEmailView, 1000);
    return;
  }

  console.log("[ShieldBox AutoScan] Observing entire body for debugging...");

  const observer = new MutationObserver(() => {
    // Check if auto scan is still enabled
    if (!autoScanEnabled) {
      console.log("[ShieldBox AutoScan] Auto scan disabled, stopping observer.");
      observer.disconnect();
      return;
    }
    
    // Wait 200ms for DOM to settle, then check again
    setTimeout(() => {
      const emailElement = document.querySelector("div[role='main'] .a3s"); // modern Gmail email body
      if (emailElement) {
        const id = emailElement.innerText.slice(0, 100); // crude but unique
        if (id !== lastScannedId) {
          lastScannedId = id;
          emailPreviouslyDetected = true;
          console.log("[ShieldBox AutoScan] 📩 New email detected. Scanning...");
          extractAndScan(emailElement);
        }
      } else {
        // No email element found
        if (emailPreviouslyDetected) {
          // Only update if previously an email was detected
          emailPreviouslyDetected = false;
          lastScannedId = null;
          updateAutoScanResultBox("No mail detected");
          chrome.runtime.sendMessage({
            action: "displayAutoScanResult",
            result: "No mail detected"
          });
        }
      }
    }, 200); // delay to let Gmail render inner content
  });

  observer.observe(body, {
    childList: true,
    subtree: true,
  });

  // Initial scan in case email is already open
  setTimeout(() => {
    const emailElement = document.querySelector("div[role='main'] .a3s");
    if (emailElement) {
      const id = emailElement.innerText.slice(0, 100);
      if (id !== lastScannedId) {
        lastScannedId = id;
        console.log("[ShieldBox AutoScan] 📩 Initial email detected. Scanning...");
        extractAndScan(emailElement);
      }
    }
  }, 500);
}

function extractAndScan(emailElement) {
  if (!autoScanEnabled) {
    console.log("[ShieldBox AutoScan] Skipped: auto scan is disabled.");
    return;
  }
  const subject = document.querySelector('h2.hP')?.innerText || "";
  const sender = document.querySelector('.gD')?.innerText || "";
  const body = emailElement.innerText || "";

  if (!subject || !sender || !body) {
    console.warn("[ShieldBox AutoScan] Missing subject, sender, or body. Skipping scan.");
    return;
  }

  const emailData = { subject, sender, body };
  console.log("[ShieldBox AutoScan] Extracted Email:", emailData);
  scanAutomatically(emailData);
}

function updateAutoScanResultBox(message) {
  const timestamp = new Date().toLocaleTimeString();
  const displayMessage = `${message} [${timestamp}]`;
  const interval = setInterval(() => {
    // Only update the auto-scan-result box, not manual scan boxes
    const panel = document.getElementById("shieldbox-panel") || document.getElementById("shieldbox-floating-panel");
    if (panel && panel.shadowRoot) {
      const resultBox = panel.shadowRoot.getElementById("auto-scan-result");
      if (resultBox) {
        resultBox.textContent = displayMessage;
        console.log("[ShieldBox AutoScan] Result shown in auto-scan-result box:", displayMessage);
        clearInterval(interval);
      }
    }
  }, 500);
}

// In scanAutomatically, call updateAutoScanResultBox ONLY for auto scan
function scanAutomatically(emailData) {
  fetch("http://127.0.0.1:5000/scan-email-auto", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(emailData),
  })
    .then((res) => res.json())
    .then((result) => {
      const message = `🛡️ Status: ${result.status.toUpperCase()} (${result.reason})`;
      console.log("[ShieldBox AutoScan]", message);
      updateAutoScanResultBox(message);
      chrome.runtime.sendMessage({
        action: "displayAutoScanResult",
        result: message,
      });
    })
    .catch((err) => {
      console.error("[ShieldBox AutoScan] Error:", err);
    });
}

