// Listen for messages from popup or floating panel
chrome.runtime.onMessage.addListener((message, sender, sendResponse) => {
  // Handle link scanning
  if (message.action === "scanLink") {
    const scanUrl = "http://127.0.0.1:5000/scan-link"; // Flask backend API

    console.log("[ShieldBox] Received scanLink request:", message.data);

    fetch(scanUrl, {
      method: "POST",
      headers: {
        "Content-Type": "application/json"
      },
      body: JSON.stringify({ url: message.data })
    })
    .then((res) => res.json())
    .then((data) => {
      console.log("[ShieldBox] Scan result received:", data);
      sendResponse({ result: data });
    })
    .catch((err) => {
      console.error("[ShieldBox] Error during scan:", err);
      sendResponse({ error: "Scan failed" });
    });

    // Keep the message channel open for async response
    return true;
  }

  // Add more actions here later (e.g., scanAutoEmail, saveHistory, etc.)
});
