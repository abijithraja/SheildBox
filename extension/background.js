chrome.runtime.onMessage.addListener((message, sender, sendResponse) => {
  if (message.type === "email-scan") {
    chrome.storage.local.set({ emailScanResult: message.result });
  }
});
