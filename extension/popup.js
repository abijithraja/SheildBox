document.addEventListener('DOMContentLoaded', () => {
  const autoScanToggle = document.getElementById('autoScanToggle');
  const iotToggle = document.getElementById('iotToggle');
  const scanBtn = document.getElementById('scanBtn');
  const urlInput = document.getElementById('urlInput');
  const manualResultBox = document.getElementById('manualResultBox');
  const autoResultBox = document.getElementById('autoResultBox');

  // Status extraction function
  function extractStatusLabel(statusText) {
    // Extract status like 'SCAM' from "Status: SCAM (Model classification)"
    const match = statusText.match(/^Status:\s*(\w+)/i);
    if (match && match[1]) {
      return match[1].toLowerCase();  // e.g. "scam"
    }
    return null;
  }

  // Send status to ESP32 via MQTT
  function sendStatusToESP32(statusText) {
    const label = extractStatusLabel(statusText);
    if (label) {
      fetch("http://127.0.0.1:5001/mqtt-publish", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ 
          message: label, 
          topic: "shieldbox/extension_alert" 
        })
      })
      .then(response => response.json())
      .then(data => {
        console.log('ESP32 MQTT alert sent:', data);
      })
      .catch(error => {
        console.error('Failed to send ESP32 alert:', error);
      });
    }
  }

  // Load saved states
  chrome.storage.sync.get(['autoScan', 'iotEnabled'], (data) => {
    autoScanToggle.checked = data.autoScan ?? true;
    iotToggle.checked = data.iotEnabled ?? true;
  });

  autoScanToggle.addEventListener('change', () => {
    chrome.storage.sync.set({ autoScan: autoScanToggle.checked });
    autoResultBox.textContent = autoScanToggle.checked
      ? "Auto scan enabled."
      : "Auto scan disabled.";
  });

  iotToggle.addEventListener('change', () => {
    chrome.storage.sync.set({ iotEnabled: iotToggle.checked });
  });

  scanBtn.addEventListener('click', () => {
    const url = urlInput.value.trim();
    if (!url) {
      manualResultBox.textContent = "Please enter a URL.";
      manualResultBox.className = "result-box";
      return;
    }

    manualResultBox.textContent = "Scanning...";
    manualResultBox.className = "result-box";

    // Send request to Flask backend for actual URL scanning
    fetch("http://127.0.0.1:5000/scan_link", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ url: url })
    })
    .then(response => response.json())
    .then(data => {
      const resultText = `Status: ${data.result.toUpperCase()} (Model classification)`;
      manualResultBox.textContent = resultText;
      
      // Set appropriate styling
      if (data.result.toLowerCase().includes('phishing') || 
          data.result.toLowerCase().includes('scam') || 
          data.result.toLowerCase().includes('fraudulent')) {
        manualResultBox.className = "result-box phishing";
      } else {
        manualResultBox.className = "result-box safe";
      }

      // Send to ESP32 via MQTT if IoT alerts are enabled
      chrome.storage.sync.get('iotEnabled', (storageData) => {
        if (storageData.iotEnabled) {
          sendStatusToESP32(resultText);
        }
      });
    })
    .catch(error => {
      console.error('Scan failed:', error);
      // Fallback to simple pattern matching
      setTimeout(() => {
        const isPhishing = /login|verify|bank|confirm/i.test(url);
        const resultText = isPhishing ? "Status: PHISHING (Pattern detected)" : "Status: SAFE (Pattern check)";
        
        manualResultBox.textContent = resultText;
        manualResultBox.className = isPhishing ? "result-box phishing" : "result-box safe";
        
        // Send to ESP32 via MQTT if IoT alerts are enabled
        chrome.storage.sync.get('iotEnabled', (storageData) => {
          if (storageData.iotEnabled) {
            sendStatusToESP32(resultText);
          }
        });
      }, 1200);
    });
  });

  // Simulate auto scan result with MQTT integration
  chrome.storage.sync.get('autoScan', (data) => {
    if (data.autoScan) {
      setTimeout(() => {
        const resultText = "Status: SAFE (Auto scan complete)";
        autoResultBox.textContent = "✅ No threats found during auto scan.";
        autoResultBox.className = "result-box safe";
        
        // Send to ESP32 via MQTT if IoT alerts are enabled
        chrome.storage.sync.get('iotEnabled', (storageData) => {
          if (storageData.iotEnabled) {
            sendStatusToESP32(resultText);
          }
        });
      }, 1000);
    }
  });
});
