chrome.runtime.onInstalled.addListener(() => {
  if (chrome.storage && chrome.storage.sync) {
    chrome.storage.sync.set({ autoScan: false, darkMode: false });
  }
});
