from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)  # Allow extension to access API

@app.route('/scan-link', methods=['POST'])
def scan_link():
    data = request.get_json()
    url = data.get('url', '')

    # 🔐 Dummy logic — Replace with ML or rules
    if "phish" in url or "fake" in url:
        result = "phishing"
    else:
        result = "safe"

    return jsonify({ "url": url, "status": result })

if __name__ == '__main__':
    app.run(debug=True)
