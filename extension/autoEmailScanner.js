chrome.storage.local.get("autoScan", (data) => {
  console.log("[ShieldBox] autoEmailScanner.js loaded");
  console.log("[ShieldBox] autoScan value:", data.autoScan);
  if (data.autoScan) waitForEmailView();
});

let lastScannedId = null;

function waitForEmailView() {
  const body = document.body;
  if (!body) {
    console.warn("[ShieldBox AutoScan] <body> not found. Retrying...");
    setTimeout(waitForEmailView, 1000);
    return;
  }

  console.log("[ShieldBox AutoScan] Observing entire body for debugging...");

  const observer = new MutationObserver(() => {
    // Wait 200ms for DOM to settle, then check again
    setTimeout(() => {
      const emailElement = document.querySelector("div[role='main'] .a3s"); // modern Gmail email body
      if (emailElement) {
        const id = emailElement.innerText.slice(0, 100); // crude but unique
        if (id !== lastScannedId) {
          lastScannedId = id;
          console.log("[ShieldBox AutoScan] 📩 New email detected. Scanning...");
          extractAndScan(emailElement);
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

function updateResultBox(message) {
  const interval = setInterval(() => {
    // Try both possible panel IDs for robustness
    const panel = document.getElementById("shieldbox-panel") || document.getElementById("shieldbox-floating-panel");
    if (panel && panel.shadowRoot) {
      const resultBox = panel.shadowRoot.getElementById("auto-scan-result");
      if (resultBox) {
        resultBox.textContent = message;
        console.log("[ShieldBox AutoScan] Result shown in result box:", message);
        clearInterval(interval);
      }
    }
  }, 500);
}

function scanAutomatically(emailData) {
  fetch("http://127.0.0.1:5000/scan-email", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(emailData),
  })
    .then((res) => res.json())
    .then((result) => {
      const message = `🛡️ Status: ${result.status.toUpperCase()} (${result.reason})`;
      console.log("[ShieldBox AutoScan]", message);
      updateResultBox(message);
      chrome.runtime.sendMessage({
        action: "displayAutoScanResult",
        result: message,
      });
    })
    .catch((err) => {
      console.error("[ShieldBox AutoScan] Error:", err);
    });
}

