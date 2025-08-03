// Bridge: Listen for window.postMessage from injected panel and relay to background
window.addEventListener('message', (event) => {
  if (event.source !== window) return;
  if (event.data && event.data.type === 'scan_link') {
    chrome.runtime.sendMessage({
      type: 'scan_link',
      url: event.data.url
    }, (response) => {
      window.postMessage({ type: 'scan_link_result', result: response }, '*');
    });
  }
  if (event.data && event.data.type === 'scan_email_request') {
    chrome.runtime.sendMessage({ type: 'scan_email_request' }, (response) => {
      window.postMessage({ type: 'scan_email_result', result: response && response.result ? response.result : 'Scan failed.' }, '*');
    });
  }
});
