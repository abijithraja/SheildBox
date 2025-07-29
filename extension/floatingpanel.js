document.addEventListener("DOMContentLoaded", () => {
  const scanBtn = document.getElementById("scanBtn");
  const resultBox = document.getElementById("resultBox");
  const resultText = document.getElementById("result");
  const darkToggle = document.getElementById("darkModeToggle");
  const autoToggle = document.getElementById("autoScanToggle");

  // Restore toggle states
  chrome.storage.sync.get(["darkMode", "autoScan"], (data) => {
    darkToggle.checked = data.darkMode || false;
    autoToggle.checked = data.autoScan || false;
    if (data.darkMode) document.body.classList.add("dark");
  });

  // Dark Mode Toggle
  darkToggle.addEventListener("change", (e) => {
    const enabled = e.target.checked;
    document.body.classList.toggle("dark", enabled);
    chrome.storage.sync.set({ darkMode: enabled });
  });

  // Auto Scan Toggle
  autoToggle.addEventListener("change", (e) => {
    chrome.storage.sync.set({ autoScan: e.target.checked });
  });

  // Scan Email button
  scanBtn.addEventListener("click", () => {
    resultText.innerText = "Scanning...";
    resultBox.classList.remove("hidden");

    chrome.tabs.query({ active: true, currentWindow: true }, (tabs) => {
      const tab = tabs[0];
      if (tab.url.includes("mail.google.com")) {
        chrome.tabs.sendMessage(tab.id, { action: "scanEmail" });
      } else {
        resultText.innerText = "Please open Gmail to scan emails.";
      }
    });
  });

  // Listen for scan result
  chrome.runtime.onMessage.addListener((request) => {
    if (request.action === "displayResult") {
      resultText.innerText = request.message;
      resultBox.classList.remove("hidden");
    }
  });
});
