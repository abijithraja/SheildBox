
// Inject floatingpanel.html as a shadow DOM panel
fetch(chrome.runtime.getURL('floatingpanel.html'))
  .then(res => res.text())
  .then(html => {
    const container = document.createElement('div');
    container.id = 'phishvault-root';
    container.style.position = 'fixed';
    container.style.top = '0';
    container.style.left = '0';
    container.style.zIndex = '999999';
    const shadow = container.attachShadow({ mode: 'open' });
    shadow.innerHTML = html;

    // Add CSS
    const styleLink = document.createElement('link');
    styleLink.rel = 'stylesheet';
    styleLink.href = chrome.runtime.getURL('floatingpanel.css');
    shadow.appendChild(styleLink);

    // Add JS
    const scriptTag = document.createElement('script');
    scriptTag.src = chrome.runtime.getURL('floatingpanel.js');
    shadow.appendChild(scriptTag);

    document.body.appendChild(container);
  });
