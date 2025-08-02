document.getElementById('scanBtn').addEventListener('click', async () => {
  const url = document.getElementById('urlInput').value;
  const mode = document.querySelector('input[name="scanMode"]:checked').value;

  if (!url) {
    alert("Please enter a URL to scan.");
    return;
  }

  // Mock result – real API call will go here later
  const risk = Math.floor(Math.random() * 100); // random risk for now

  const riskBar = document.getElementById('riskBar');
  const riskText = document.getElementById('riskText');
  const resultBox = document.getElementById('resultBox');
  resultBox.classList.remove('hidden');

  // Set color based on risk level
  if (risk < 30) {
    riskBar.style.background = "#00ff00";
    riskText.innerText = "Low Risk (" + risk + "%)";
  } else if (risk < 70) {
    riskBar.style.background = "#ffff00";
    riskText.innerText = "Medium Risk (" + risk + "%)";
  } else {
    riskBar.style.background = "#ff0000";
    riskText.innerText = "High Risk (" + risk + "%)";
  }

  riskBar.style.width = `${risk}%`;
});
