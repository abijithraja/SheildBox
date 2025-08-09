let autoScanEnabled = true; // Default to enabled
let isExtensionValid = true; // Track extension context validity
let lastScannedId = null;
let emailPreviouslyDetected = false;
let scanDebounceTimer = null; // Debounce timer for performance
let lastSentLabel = null; // Track last label sent to prevent duplicates

// === ULTRA-FAST PERFORMANCE: Debounced scanning ===
function debouncedScan(emailElement, delay = 300) {
  if (scanDebounceTimer) {
    clearTimeout(scanDebounceTimer);
  }
  
  scanDebounceTimer = setTimeout(() => {
    extractAndScan(emailElement);
  }, delay);
}

// === PERFORMANCE: Faster email content hashing ===
function quickEmailHash(emailElement) {
  const text = emailElement.textContent || "";
  // Use first 100 chars + last 50 chars + length for fast unique ID
  return text.substring(0, 100) + text.substring(text.length - 50) + text.length;
}

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

// Send status to ESP32 via MQTT with duplicate prevention
function sendStatusToESP32(statusText) {
  if (!checkExtensionContext()) {
    console.warn("[ShieldBox AutoScan] Skipping ESP32 send - context invalid");
    return;
  }
  
  const label = extractStatusLabel(statusText);
  if (label) {
    // Prevent sending same label repeatedly after no_mail
    if (lastSentLabel === "no_mail" && label === lastSentLabel) {
      console.log("[ShieldBox AutoScan] Blocked duplicate signal after no_mail:", label);
      return;
    }
    
    lastSentLabel = label; // Update last sent label
    
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

// Send "no_mail" signal to ESP32 to reset LED/Buzzer
function sendNoMailToESP32() {
  if (!checkExtensionContext()) {
    console.warn("[ShieldBox AutoScan] Skipping no_mail send - context invalid");
    return;
  }
  
  // Prevent sending no_mail repeatedly
  if (lastSentLabel === "no_mail") {
    console.log("[ShieldBox AutoScan] Blocked duplicate no_mail signal");
    return;
  }
  
  lastSentLabel = "no_mail"; // Update last sent label
  
  fetch("http://127.0.0.1:5001/mqtt-publish", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ 
      message: "no_mail", 
      topic: "shieldbox/email_scan",
      risk: 0
    })
  })
  .then(response => response.json())
  .then(data => {
    console.log('[ShieldBox AutoScan] ESP32 no_mail signal sent:', data);
  })
  .catch(error => {
    console.error('[ShieldBox AutoScan] Failed to send no_mail signal:', error);
  });
}

safeStorageGet("autoScan", (data) => {
  console.log("[ShieldBox] autoEmailScanner.js loaded");
  console.log("[ShieldBox] autoScan value:", data.autoScan);
  autoScanEnabled = data.autoScan !== false; // Default to true
  if (autoScanEnabled && checkExtensionContext()) {
    waitForEmailView();
    setupNavigationListeners(); // Set up no_mail detection
  }
});

if (checkExtensionContext()) {
  chrome.storage.onChanged.addListener((changes, area) => {
    if (area === "sync" && changes.autoScan) {
      autoScanEnabled = changes.autoScan.newValue !== false;
      console.log("[ShieldBox] autoScan toggled:", autoScanEnabled);
      if (autoScanEnabled) {
        waitForEmailView();
        setupNavigationListeners(); // Re-setup listeners when enabled
      } else {
        // Clear the auto scan result when disabled and send no_mail
        updateAutoScanResultBox("Auto scan disabled");
        safeSendMessage({
          action: "displayAutoScanResult",
          result: "Auto scan disabled"
        });
        
        // Send no_mail signal when auto scan is disabled
        safeStorageGet('iotEnabled', (data) => {
          if (data.iotEnabled && emailPreviouslyDetected) {
            console.log("[ShieldBox AutoScan] 📴 Auto scan disabled - sending no_mail signal");
            sendNoMailToESP32();
            emailPreviouslyDetected = false;
            lastScannedId = null;
            lastSentLabel = null; // Reset label tracking
          }
        });
      }
    }
  });
}

// Setup listeners to detect when user navigates away from emails
function setupNavigationListeners() {
  if (!checkExtensionContext()) {
    console.warn("[ShieldBox AutoScan] Skipping navigation listeners - context invalid");
    return;
  }

  // Detect when user leaves the page entirely
  window.addEventListener("beforeunload", () => {
    if (emailPreviouslyDetected && checkExtensionContext()) {
      console.log("[ShieldBox AutoScan] 📴 Page unloading - sending no_mail signal");
      safeStorageGet('iotEnabled', (data) => {
        if (data.iotEnabled) {
          sendNoMailToESP32();
        }
      });
    }
  });

  // Detect when tab becomes hidden (user switches tabs)
  document.addEventListener("visibilitychange", () => {
    if (document.hidden && emailPreviouslyDetected && checkExtensionContext()) {
      console.log("[ShieldBox AutoScan] 📴 Tab hidden - sending no_mail signal");
      safeStorageGet('iotEnabled', (data) => {
        if (data.iotEnabled) {
          sendNoMailToESP32();
        }
      });
    }
  });

  // Detect Gmail navigation changes (when user navigates within Gmail)
  let lastUrl = location.href;
  const urlObserver = new MutationObserver(() => {
    if (location.href !== lastUrl) {
      lastUrl = location.href;
      console.log("[ShieldBox AutoScan] 📴 URL changed - sending no_mail signal");
      if (emailPreviouslyDetected && checkExtensionContext()) {
        safeStorageGet('iotEnabled', (data) => {
          if (data.iotEnabled) {
            sendNoMailToESP32();
          }
        });
        // Reset email detection state
        emailPreviouslyDetected = false;
        lastScannedId = null;
      }
    }
  });
  
  urlObserver.observe(document.body, { 
    childList: true, 
    subtree: true 
  });

  console.log("[ShieldBox AutoScan] 🔧 Navigation listeners setup complete");
}

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
    
    // === ULTRA-FAST: Immediate check with debounced scanning ===
    if (!checkExtensionContext()) {
      observer.disconnect();
      return;
    }
    
    const emailElement = document.querySelector("div[role='main'] .a3s"); // modern Gmail email body
    if (emailElement) {
      const emailHash = quickEmailHash(emailElement); // Fast hash
      if (emailHash !== lastScannedId) {
        lastScannedId = emailHash;
        emailPreviouslyDetected = true;
        lastSentLabel = null; // Reset label tracking for new email
        console.log("[ShieldBox AutoScan] 📩 New email detected. Debounced scanning...");
        debouncedScan(emailElement, 200); // Fast debounced scan
      }
    } else {
      // No email element found - send no_mail signal
      if (emailPreviouslyDetected) {
        // Only update if previously an email was detected
        emailPreviouslyDetected = false;
        lastScannedId = null;
        updateAutoScanResultBox("No mail detected");
        safeSendMessage({
          action: "displayAutoScanResult",
          result: "No mail detected"
        });
        
        // Send no_mail signal to ESP32 to reset LED/Buzzer
        safeStorageGet('iotEnabled', (data) => {
          if (data.iotEnabled && checkExtensionContext()) {
            console.log("[ShieldBox AutoScan] 📴 Sending no_mail signal to ESP32");
            sendNoMailToESP32();
          }
        });
      }
    }
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
        lastSentLabel = null; // Reset label tracking for initial email
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
  
  // === ULTRA-FAST FETCH with minimal data and longer timeout ===
  const startTime = performance.now();
  
  // Show scanning indicator
  updateAutoScanResultBox("🔄 Scanning...");
  
  fetch("http://127.0.0.1:5000/scan-email-auto", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      subject: emailData.subject,
      body: emailData.body.substring(0, 2000) // Limit body size for speed
    }),
    signal: AbortSignal.timeout(15000) // Increased to 15 seconds for better reliability
  })
    .then((res) => {
      if (!res.ok) throw new Error(`HTTP ${res.status}`);
      return res.json();
    })
    .then((result) => {
      const scanTime = performance.now() - startTime;
      
      if (!checkExtensionContext()) {
        console.warn("[ShieldBox AutoScan] Context invalid during result processing");
        return;
      }
      
      // Enhanced message with performance data if available
      let message = `🛡️ Status: ${result.status.toUpperCase()} (${result.reason})`;
      
      if (result.performance) {
        message += ` [${Math.round(scanTime)}ms total, ${result.performance.prediction_time}ms ML]`;
        console.log(`[ShieldBox AutoScan] Performance: Total=${Math.round(scanTime)}ms, ML=${result.performance.prediction_time}ms, MQTT=${result.performance.mqtt_time}ms`);
      } else {
        message += ` [${Math.round(scanTime)}ms]`;
      }
      
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
      const scanTime = performance.now() - startTime;
      
      // Better error handling for different error types
      let errorMessage = "❌ Scan failed";
      
      if (err.name === 'TimeoutError' || err.name === 'AbortError') {
        if (scanTime > 14000) { // Near the 15s timeout
          errorMessage = "⏱️ Scan timeout (>15s) - check backend";
        } else {
          errorMessage = "⏱️ Scan timeout - server slow";
        }
        console.error(`[ShieldBox AutoScan] Timeout after ${Math.round(scanTime)}ms`);
      } else if (err.message && err.message.includes("Failed to fetch")) {
        errorMessage = "🔌 Connection failed - backend offline?";
        console.error(`[ShieldBox AutoScan] Connection error after ${Math.round(scanTime)}ms:`, err);
      } else {
        console.error(`[ShieldBox AutoScan] Error after ${Math.round(scanTime)}ms:`, err);
      }
      
      updateAutoScanResultBox(`${errorMessage} [${Math.round(scanTime)}ms]`);
      
      if (err.message && err.message.includes("Extension context invalidated")) {
        isExtensionValid = false;
        console.warn("[ShieldBox AutoScan] Extension context invalidated - stopping operations");
      }
    });
}

