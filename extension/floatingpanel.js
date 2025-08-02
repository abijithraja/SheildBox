// Inject floatingpanel.html inside Shadow DOM
fetch(chrome.runtime.getURL('floatingpanel.html'))
  .then(res => res.text())
  .then(html => {
    const container = document.createElement('div');
    container.id = 'shieldbox-floating-panel';
    container.style.position = 'fixed';
    container.style.top = '100px';
    container.style.left = '100px';
    container.style.zIndex = '999999';

    const shadow = container.attachShadow({ mode: 'open' });
    shadow.innerHTML = html;

    const styleLink = document.createElement('link');
    styleLink.rel = 'stylesheet';
    styleLink.href = chrome.runtime.getURL('style.css');
    shadow.appendChild(styleLink);

    document.body.appendChild(container);

    // Theme toggle logic
    const interval = setInterval(() => {
      const darkModeToggle = shadow.getElementById("darkModeToggle");
      if (!darkModeToggle) return;

      clearInterval(interval); // Wait until it's available

      const savedTheme = localStorage.getItem("theme");

      function applyTheme(mode) {
        if (mode === "dark") {
          shadow.host.classList.add("dark-mode");
          darkModeToggle.checked = true;
        } else {
          shadow.host.classList.remove("dark-mode");
          darkModeToggle.checked = false;
        }
        localStorage.setItem("theme", mode);
      }

      darkModeToggle.addEventListener("change", () => {
        const newMode = darkModeToggle.checked ? "dark" : "light";
        applyTheme(newMode);
      });

      applyTheme(savedTheme || "light");
    }, 50);

    // Draggable logic
    let isDragging = false, offsetX, offsetY;
    container.onmousedown = e => {
      isDragging = true;
      offsetX = e.clientX - container.offsetLeft;
      offsetY = e.clientY - container.offsetTop;
    };
    document.onmousemove = e => {
      if (isDragging) {
        container.style.left = `${e.clientX - offsetX}px`;
        container.style.top = `${e.clientY - offsetY}px`;
      }
    };
    document.onmouseup = () => (isDragging = false);
  });
