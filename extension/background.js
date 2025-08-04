chrome.runtime.onMessage.addListener((message, sender, sendResponse) => {
  if (message.action === "request_email_extraction") {
    chrome.tabs.query({ active: true, currentWindow: true }, (tabs) => {
      if (!tabs[0]) {
        sendResponse({ error: "No active tab." });
        return;
      }

      chrome.tabs.sendMessage(tabs[0].id, { action: "extract_email" }, (response) => {
        if (chrome.runtime.lastError || !response) {
          sendResponse({ error: chrome.runtime.lastError?.message || "No response from content script" });
        } else {
          sendResponse({ email: response });
        }
      });
    });

    // Must return true to keep the message channel open
    return true;
  }
});
// ...existing code...
// Listen for messages from popup or floating panel
chrome.runtime.onMessage.addListener((message, sender, sendResponse) => {
  // Handle link scanning

  if (message.action === "scanLink") {
    fetch("http://127.0.0.1:5000/scan-link", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ url: message.data })
    })
      .then(res => res.json())
      .then(data => {
        sendResponse({ result: data });
      })
      .catch(error => {
        console.error("[ShieldBox] Scan error:", error);
        sendResponse({ result: null });
      });
    return true;
  }

  if (message.action === "scanEmail") {
    // Ask content script to get the latest email content
    chrome.tabs.query({ active: true, currentWindow: true }, function (tabs) {
      chrome.tabs.sendMessage(tabs[0].id, { action: "getEmailContent" }, (response) => {
        if (!response || !response.body) {
          chrome.runtime.sendMessage({
            action: "displayResult",
            source: "email",
            result: "❌ Failed to extract email content."
          });
          return;
        }
        fetch("http://127.0.0.1:5000/scan-email", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ body: response.body, subject: response.subject })
        })
          .then(res => res.json())
          .then(data => {
            chrome.runtime.sendMessage({
              action: "displayResult",
              source: "email",
              result: `📩 ${data.status ? data.status.toUpperCase() : 'UNKNOWN'} — ${data.reason || data.result || ''}`
            });
          })
          .catch(err => {
            console.error("Email scan error:", err);
            chrome.runtime.sendMessage({
              action: "displayResult",
              source: "email",
              result: "❌ Error while scanning email."
            });
          });
      });
    });
    return true;
  }
});
