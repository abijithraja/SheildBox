function extractEmailDetails() {
  let subject = document.querySelector('h2.hP')?.innerText || "";
  let sender = document.querySelector('.gD')?.innerText || "";
  let body = document.querySelector('.a3s')?.innerText || "";

  return { subject, sender, body };
}

// ✅ Only manual scan – working listener
chrome.runtime.onMessage.addListener((msg, sender, sendResponse) => {
  if (msg.action === "extract_email") {
    const emailData = extractEmailDetails();
    console.log("Extracted email data:", emailData);
    sendResponse(emailData);
  }
});
