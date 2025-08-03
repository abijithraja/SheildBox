function extractEmailDetails() {
  let subject = document.querySelector('h2.hP')?.innerText || "";
  let sender = document.querySelector('.gD')?.innerText || "";
  let body = document.querySelector('.a3s')?.innerText || "";

  return { subject, sender, body };
}

// 1. Manual message trigger (already working)
chrome.runtime.onMessage.addListener((msg, sender, sendResponse) => {
  if (msg.action === "extract_email") {
    const emailData = extractEmailDetails();
    sendResponse(emailData);
  }
});

// 2. Auto scan when new email is opened in Gmail
let lastEmailId = null;

function getCurrentEmailId() {
  const match = window.location.href.match(/#inbox\/([^\/]+)/);
  return match ? match[1] : null;
}

function autoScanEmail() {
  const currentId = getCurrentEmailId();
  if (!currentId || currentId === lastEmailId) {
    return;
  }
  lastEmailId = currentId;

  const { subject, sender, body } = extractEmailDetails();
  const emailData = { subject, sender, body };
  console.log("autoScanEmail: Detected new email.", emailData);

  if (typeof chrome === "undefined" || !chrome.runtime) {
    console.warn("autoScanEmail: chrome.runtime not available, skipping sendMessage.");
    return;
  }
  if (chrome.runtime?.id) {
    try {
      chrome.runtime.sendMessage(
        { action: "scanAutoEmail", data: emailData },
        (response) => {
          console.log("autoScanEmail: Message sent to background, response:", response);
        }
      );
    } catch (e) {
      console.error("autoScanEmail: Failed to send message – extension context invalidated", e);
    }
  } else {
    console.warn("autoScanEmail: chrome.runtime not available, skipping sendMessage.");
  }
}

// Observe DOM changes to detect when user opens new email
const observer = new MutationObserver(() => {
  autoScanEmail();
});

observer.observe(document.body, { childList: true, subtree: true });

// Trigger once on initial load
autoScanEmail();
