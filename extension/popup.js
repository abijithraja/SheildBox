document.addEventListener('DOMContentLoaded', () => {
  const autoScanToggle = document.getElementById('autoScanToggle');
  const iotToggle = document.getElementById('iotToggle');
  const scanBtn = document.getElementById('scanBtn');
  const urlInput = document.getElementById('urlInput');
  const manualResultBox = document.getElementById('manualResultBox');
  const autoResultBox = document.getElementById('autoResultBox');

  // Load toggle states
  chrome.storage.sync.get(['autoScan', 'iotEnabled'], (data) => {
    autoScanToggle.checked = data.autoScan ?? true;
    iotToggle.checked = data.iotEnabled ?? true;
  });

  autoScanToggle.addEventListener('change', () => {
    chrome.storage.sync.set({ autoScan: autoScanToggle.checked });
    autoResultBox.textContent = autoScanToggle.checked
      ? "Auto scan is enabled."
      : "Auto scan is disabled.";
  });

  iotToggle.addEventListener('change', () => {
    chrome.storage.sync.set({ iotEnabled: iotToggle.checked });
  });

  scanBtn.addEventListener('click', () => {
    const url = urlInput.value.trim();
    if (!url) {
      manualResultBox.textContent = "Please enter a valid URL.";
      return;
    }

    manualResultBox.textContent = "Scanning...";
    setTimeout(() => {
      const isPhishing = /login|verify|bank/i.test(url);
      if (isPhishing) {
        chrome.storage.sync.get('iotEnabled', (data) => {
          const iotStatus = data.iotEnabled;
          manualResultBox.textContent = iotStatus
            ? "⚠️ Phishing detected. IoT alert sent!"
            : "⚠️ Phishing detected.";
        });
      } else {
        manualResultBox.textContent = "✅ Link is safe.";
      }
    }, 1500);
  });

  // Simulate an auto scan result
  chrome.storage.sync.get('autoScan', (data) => {
    if (data.autoScan) {
      setTimeout(() => {
        autoResultBox.textContent = "✅ No threats detected during auto scan.";
      }, 1000);
    }
  });
});
