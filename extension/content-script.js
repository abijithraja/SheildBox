fetch(chrome.runtime.getURL('floatingpanel.html'))
  .then(res => res.text())
  .then(html => {
    const wrapper = document.createElement('div');
    const shadow = wrapper.attachShadow({ mode: 'open' });
    shadow.innerHTML = html;

    // Attach external CSS and JS
    const style = document.createElement('link');
    style.setAttribute('rel', 'stylesheet');
    style.setAttribute('href', chrome.runtime.getURL('floatingpanel.css'));
    shadow.appendChild(style);

    const script = document.createElement('script');
    script.setAttribute('src', chrome.runtime.getURL('floatingpanel.js'));
    shadow.appendChild(script);

    document.body.appendChild(wrapper);
  });
