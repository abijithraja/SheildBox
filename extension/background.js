chrome.action.onClicked.addListener((tab) => {
  // Inject CSS
  chrome.scripting.insertCSS({
    target: { tabId: tab.id },
    files: ['style.css']
  }).catch(err => console.error('CSS injection failed:', err));

  // Inject JS
  chrome.scripting.executeScript({
    target: { tabId: tab.id },
    files: ['floatingPanel.js']
  }).catch(err => console.error('JS injection failed:', err));
});
