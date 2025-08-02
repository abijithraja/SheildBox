// content-script.js

if (!document.getElementById("shieldbox-shadow-host")) {
  const host = document.createElement("div");
  host.id = "shieldbox-shadow-host";
  host.style.position = "fixed";
  host.style.top = "100px";
  host.style.right = "20px";
  host.style.zIndex = "999999";
  host.style.width = "320px";

  const shadow = host.attachShadow({ mode: "open" });

  fetch(chrome.runtime.getURL("popup.html"))
    .then(res => res.text())
    .then(html => {
      shadow.innerHTML = html;

      const styleLink = document.createElement("link");
      styleLink.rel = "stylesheet";
      styleLink.href = chrome.runtime.getURL("popup.css");
      shadow.appendChild(styleLink);

      const scriptTag = document.createElement("script");
      scriptTag.src = chrome.runtime.getURL("popup.js");
      shadow.appendChild(scriptTag);
    });

  document.body.appendChild(host);
}
