let autoScanEnabled = true; // Default to enabled
let isExtensionValid = true; // Track extension context validity

// Check if extension context is still valid
function checkExtensionContext() {
  try {
    if (chrome.runtime && chrome.runtime.id) {
      return true;
    }
  } catch (error) {
    console.warn("[ShieldBox AutoScan] Extension context invalidated:", error);
    isExtensionValid = false;
    return false;
  }
  return false;
}

// Safe chrome.storage operations with context validation
function safeStorageGet(keys, callback) {
  if (!checkExtensionContext()) {
    console.warn("[ShieldBox AutoScan] Skipping storage operation - context invalid");
    return;
  }
  try {
    chrome.storage.sync.get(keys, callback);
  } catch (error) {
    console.warn("[ShieldBox AutoScan] Storage operation failed:", error);
    isExtensionValid = false;
  }
}

// Safe chrome.runtime.sendMessage with context validation
function safeSendMessage(message) {
  if (!checkExtensionContext()) {
    console.warn("[ShieldBox AutoScan] Skipping message send - context invalid");
    return;
  }
  try {
    chrome.runtime.sendMessage(message);
  } catch (error) {
    console.warn("[ShieldBox AutoScan] Message send failed:", error);
    isExtensionValid = false;
  }
}

// Status extraction function for MQTT
function extractStatusLabel(statusText) {
  // Extract status like 'SCAM' from "Status: SCAM (Model classification)"
  const match = statusText.match(/Status:\s*(\w+)/i);
  if (match && match[1]) {
    return match[1].toLowerCase();  // e.g. "scam"
  }
  return null;
}

// Send status to ESP32 via MQTT
function sendStatusToESP32(statusText) {
  if (!checkExtensionContext()) {
    console.warn("[ShieldBox AutoScan] Skipping ESP32 send - context invalid");
    return;
  }
  
  const label = extractStatusLabel(statusText);
  if (label) {
    fetch("http://127.0.0.1:5001/mqtt-publish", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ 
        message: label, 
        topic: "shieldbox/email_scan" 
      })
    })
    .then(response => response.json())
    .then(data => {
      console.log('[ShieldBox AutoScan] ESP32 MQTT alert sent:', data);
    })
    .catch(error => {
      console.error('[ShieldBox AutoScan] Failed to send ESP32 alert:', error);
    });
  }
}

safeStorageGet("autoScan", (data) => {
  console.log("[ShieldBox] autoEmailScanner.js loaded");
  console.log("[ShieldBox] autoScan value:", data.autoScan);
  autoScanEnabled = data.autoScan !== false; // Default to true
  if (autoScanEnabled && checkExtensionContext()) {
    waitForEmailView();
  }
});

if (checkExtensionContext()) {
  chrome.storage.onChanged.addListener((changes, area) => {
    if (area === "sync" && changes.autoScan) {
      autoScanEnabled = changes.autoScan.newValue !== false;
      console.log("[ShieldBox] autoScan toggled:", autoScanEnabled);
      if (autoScanEnabled) {
        waitForEmailView();
      } else {
        // Clear the auto scan result when disabled
        updateAutoScanResultBox("Auto scan disabled");
        safeSendMessage({
          action: "displayAutoScanResult",
          result: "Auto scan disabled"
        });
      }
    }
  });
}

let lastScannedId = null;
let emailPreviouslyDetected = false;

function waitForEmailView() {
  if (!autoScanEnabled || !checkExtensionContext()) {
    console.log("[ShieldBox AutoScan] Auto scan is disabled or context invalid. Not starting observer.");
    return;
  }
  
  const body = document.body;
  if (!body) {
    console.warn("[ShieldBox AutoScan] <body> not found. Retrying...");
    setTimeout(() => {
      if (checkExtensionContext()) {
        waitForEmailView();
      }
    }, 1000);
    return;
  }

  console.log("[ShieldBox AutoScan] Observing entire body for debugging...");

  const observer = new MutationObserver(() => {
    // Check if extension context is still valid and auto scan is enabled
    if (!autoScanEnabled || !checkExtensionContext()) {
      console.log("[ShieldBox AutoScan] Auto scan disabled or context invalid, stopping observer.");
      observer.disconnect();
      return;
    }
    
    // Wait 200ms for DOM to settle, then check again
    setTimeout(() => {
      if (!checkExtensionContext()) {
        observer.disconnect();
        return;
      }
      
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
          safeSendMessage({
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
    if (!checkExtensionContext()) {
      observer.disconnect();
      return;
    }
    
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
  if (!autoScanEnabled || !checkExtensionContext()) {
    console.log("[ShieldBox AutoScan] Skipped: auto scan is disabled or context invalid.");
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
  if (!checkExtensionContext()) {
    console.warn("[ShieldBox AutoScan] Skipping scan - context invalid");
    return;
  }
  
  fetch("http://127.0.0.1:5000/scan-email-auto", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(emailData),
  })
    .then((res) => res.json())
    .then((result) => {
      if (!checkExtensionContext()) {
        console.warn("[ShieldBox AutoScan] Context invalid during result processing");
        return;
      }
      
      const message = `🛡️ Status: ${result.status.toUpperCase()} (${result.reason})`;
      console.log("[ShieldBox AutoScan]", message);
      updateAutoScanResultBox(message);
      
      // Send to ESP32 via MQTT if IoT alerts are enabled
      safeStorageGet('iotEnabled', (data) => {
        if (data.iotEnabled && checkExtensionContext()) {
          sendStatusToESP32(message);
        }
      });
      
      safeSendMessage({
        action: "displayAutoScanResult",
        result: message,
      });
    })
    .catch((err) => {
      console.error("[ShieldBox AutoScan] Error:", err);
      if (err.message && err.message.includes("Extension context invalidated")) {
        isExtensionValid = false;
        console.warn("[ShieldBox AutoScan] Extension context invalidated - stopping operations");
      }
    });
}

