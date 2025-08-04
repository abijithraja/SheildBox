
from flask import Flask, request, jsonify
from flask_cors import CORS
import joblib
import numpy as np
from feature_extractor import extract_features

# --- Flask App Setup ---
app = Flask(__name__)
CORS(app)  # Allow extension to access API

# --- Load Trained URL Phishing Model ---
print("Loading phishing model...")
phishing_model_package = joblib.load("phishing_model.pkl")
phishing_model = phishing_model_package["model"]
scaler = phishing_model_package["scaler"]
threshold = phishing_model_package["threshold"]
print(f"Phishing model loaded. Threshold: {threshold}")

# --- Load Trained Email Model (3-class: phishing, scam, safe) ---
print("Loading email model...")
email_model = joblib.load("email_model.pkl")
email_vectorizer = joblib.load("email_vectorizer.pkl")
email_label_encoder = joblib.load("email_label_encoder.pkl")
print("Email model loaded.")

# --- URL Scanner Route ---
@app.route('/scan-link', methods=['POST'])
def scan_link():
    data = request.get_json()
    url = data.get('url', '')

    if not url.startswith("http"):
        return jsonify({ "url": url, "status": "invalid", "reason": "Not a valid URL" })

    try:
        features = extract_features(url)
        features_scaled = scaler.transform([features])
        prob = phishing_model.predict_proba(features_scaled)[0][1]
        is_phishing = int(prob >= threshold)

        return jsonify({
            "url": url,
            "status": "phishing" if is_phishing else "safe",
            "probability": round(float(prob), 4)
        })

    except Exception as e:
        return jsonify({ "url": url, "status": "error", "reason": str(e) })


# --- Email Scanner Route (subject + body -> phishing/scam/safe) ---
@app.route('/scan-email', methods=['POST'])
def scan_email():
    data = request.get_json()
    subject = data.get("subject", "")
    body = data.get("body", "")

    if not subject and not body:
        return jsonify({"error": "Missing subject and body"}), 400

    try:
        text = (subject + " " + body).lower()
        vector = email_vectorizer.transform([text])
        prediction = email_model.predict(vector)[0]
        label = email_label_encoder.inverse_transform([prediction])[0]

        return jsonify({
            "status": label,
            "subject": subject,
            "body": body
        })
    except Exception as e:
        return jsonify({"error": "Model inference failed", "reason": str(e)}), 500


# --- Run App ---
if __name__ == '__main__':
    app.run(debug=True)
