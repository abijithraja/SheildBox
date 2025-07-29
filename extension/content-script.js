// content-script.js

// Inject floating panel if not already there
if (!document.getElementById("shieldbox-root")) {
  const panel = document.createElement("div");
  panel.id = "shieldbox-root";
  panel.style.position = "fixed";
  panel.style.top = "100px";
  panel.style.right = "20px";
  panel.style.zIndex = "999999";
  panel.style.width = "300px";
  panel.innerHTML = `
    <div style="
      background: #fff;
      border: 2px solid #222;
      border-radius: 12px;
      box-shadow: 0 0 10px rgba(0,0,0,0.2);
      padding: 15px;
      font-family: Arial, sans-serif;
    ">
      <h3 style="margin-top: 0;">Shield Box</h3>
      <p><strong>Email Subject:</strong> "Reset Your Password Now!"</p>
      <p><strong>Detected Risk:</strong> <span style="color: red; font-weight: bold;">High (Phishing)</span></p>
      <p><strong>Suspicious Link:</strong><br><code>http://secure-login-support.io/reset</code></p>
    </div>
  `;
  document.body.appendChild(panel);
}
