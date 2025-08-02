chrome.action.onClicked.addListener((tab) => {
  chrome.scripting.insertCSS({
    target: { tabId: tab.id },
    files: ['shieldPanel.css']
  }).catch(err => console.error('CSS injection failed:', err));

  chrome.scripting.executeScript({
    target: { tabId: tab.id },
    files: ['shieldPanel.js']
  }).catch(err => console.error('JS injection failed:', err));
});
