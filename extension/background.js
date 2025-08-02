// background.js

chrome.runtime.onInstalled.addListener(() => {
  console.log("🔐 Shield Box installed.");
});

// Optional: Listen for messages from popup or content script
chrome.runtime.onMessage.addListener((message, sender, sendResponse) => {
  if (message.type === "log") {
    console.log("Message from popup:", message.data);
  }
});
