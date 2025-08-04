from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)  # Allow extension to access API

# --- Manual URL Scan ---
@app.route('/scan-link', methods=['POST'])
def scan_link():
    data = request.get_json()
    url = data.get('url', '')
    
    # Basic detection logic
    if not url.startswith("http"):
        return jsonify({ "url": url, "status": "invalid", "reason": "Not a valid URL" })

    if "phish" in url or "fake" in url:
        result = "phishing"
    else:
        result = "safe"

    return jsonify({ "url": url, "status": result })

# --- Manual/Auto Email Scan ---
@app.route('/scan-email', methods=['POST'])
def scan_email():
    data = request.get_json()
    body = data.get('body', '').lower()
    subject = data.get('subject', '').lower()

    suspicious_phrases = ["verify your account", "login here", "reset your password"]
    phishing_links = ["phish", "fake", "scam"]

    found_links = [word for word in body.split() if word.startswith("http")]
    suspicious = any(phrase in body for phrase in suspicious_phrases)
    link_suspicious = any(any(p in link for p in phishing_links) for link in found_links)

    if suspicious or link_suspicious:
        return jsonify({
            "status": "phishing",
            "reason": f"Suspicious content{' and links' if link_suspicious else ''} detected",
            "links": found_links
        })
    elif found_links:
        return jsonify({
            "status": "safe",
            "reason": "Links found but no suspicious patterns",
            "links": found_links
        })
    else:
        return jsonify({
            "status": "safe",
            "reason": "No links or threats found"
        })

if __name__ == '__main__':
    app.run(debug=True)
from flask import Flask, request, jsonify
from flask_cors import CORS

@app.route('/scan-email', methods=['POST'])
def scan_email():
    data = request.get_json()
    body = data.get('body', '')
    subject = data.get('subject', '')

    # Simple rule-based detection
    if "http://phishingsite.com" in body or "verify account" in body.lower():
        return jsonify({
            "status": "phishing",
            "reason": "Suspicious link found in email body"
        })
    else:
        return jsonify({
            "status": "safe",
            "reason": "No threats detected"
        })
from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)  # Allow extension to access API

@app.route('/scan-link', methods=['POST'])
def scan_link():
    data = request.get_json()
    url = data.get('url', '')
    if "phish" in url or "fake" in url:
        result = "phishing"
    else:
        result = "safe"

    return jsonify({ "url": url, "status": result })

if __name__ == '__main__':
    app.run(debug=True)
