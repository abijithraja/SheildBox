document.addEventListener('DOMContentLoaded', () => {
  const autoScanToggle = document.getElementById('autoScanToggle');
  const iotToggle = document.getElementById('iotToggle');
  const scanBtn = document.getElementById('scanBtn');
  const urlInput = document.getElementById('urlInput');
  const manualResultBox = document.getElementById('manualResultBox');
  const autoResultBox = document.getElementById('autoResultBox');

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

    setTimeout(() => {
      const isPhishing = /login|verify|bank|confirm/i.test(url);
      if (isPhishing) {
        chrome.storage.sync.get('iotEnabled', (data) => {
          const iotStatus = data.iotEnabled;
          manualResultBox.textContent = iotStatus
            ? "⚠️ Phishing detected. IoT alert sent!"
            : "⚠️ Phishing detected.";
          manualResultBox.className = "result-box phishing";
        });
      } else {
        manualResultBox.textContent = "✅ Link is safe.";
        manualResultBox.className = "result-box safe";
      }
    }, 1200);
  });

  // Simulate auto scan result
  chrome.storage.sync.get('autoScan', (data) => {
    if (data.autoScan) {
      setTimeout(() => {
        autoResultBox.textContent = "✅ No threats found during auto scan.";
        autoResultBox.className = "result-box safe";
      }, 1000);
    }
  });
});
