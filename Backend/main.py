
from flask import Flask, request, jsonify
from flask_cors import CORS
import joblib
import numpy as np
from feature_extractor import extract_features
from auto_email_model_loader import load_auto_email_model

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


# --- Load Trained Email Model (manual scan) ---
print("Loading email model...")
email_model = joblib.load("email_model.pkl")
email_vectorizer = joblib.load("email_vectorizer.pkl")
email_label_encoder = joblib.load("email_label_encoder.pkl")
print("Email model loaded.")

# --- Load Auto Email Model (auto scan) ---
auto_email_model_package = load_auto_email_model()

# --- Auto Email Scanner Route (subject + body -> multi-class) ---
@app.route('/scan-email-auto', methods=['POST'])
def scan_email_auto():
    data = request.get_json()
    subject = data.get("subject", "")
    body = data.get("body", "")

    if not subject and not body:
        return jsonify({"error": "Missing subject and body"}), 400

    try:
        text = (subject + " " + body).lower()
        
        # Handle different model package formats
        if isinstance(auto_email_model_package, dict):
            if 'vectorizer' in auto_email_model_package:
                # Complete model package
                vectorizer = auto_email_model_package['vectorizer']
                model = auto_email_model_package['model']
                label_encoder = auto_email_model_package['label_encoder']
                
                vector = vectorizer.transform([text])
                prediction = model.predict(vector)[0]
                label = label_encoder.inverse_transform([prediction])[0]
            else:
                # Pipeline model
                model = auto_email_model_package['model']
                label = model.predict([text])[0]
        else:
            # Direct pipeline
            label = auto_email_model_package.predict([text])[0]
        
        # Add contextual checks for scam patterns (more specific than just keywords)
        # Check for legitimate domains first
        legitimate_domains = [
            "github.com", "google.com", "microsoft.com", "amazon.com", "linkedin.com",
            "stackoverflow.com", "medium.com", "dev.to", "atlassian.com", "slack.com",
            "discord.com", "reddit.com", "twitter.com", "facebook.com", "instagram.com"
        ]
        
        is_from_legitimate_source = any(domain in text for domain in legitimate_domains)
        
        # Only apply keyword detection if NOT from legitimate sources
        if not is_from_legitimate_source:
            # More specific scam patterns (combinations of keywords)
            donation_scam_patterns = [
                ("donate", "bank transfer"), ("charity", "account details"), 
                ("fund", "wire"), ("urgent", "donation"), ("relief", "payment"),
                ("ngo", "send money"), ("foundation", "transfer")
            ]
            
            promotional_spam_patterns = [
                ("exclusive deal", "act fast"), ("limited time", "only"), 
                ("flash sale", "hurry up"), ("you've won", "claim now"),
                ("amazing deal", "order now"), ("special offer", "limited stock"),
                ("congratulations", "prize"), ("discount", "expires")
            ]
            
            # Check for donation scam patterns
            has_donation_scam = any(
                all(kw in text for kw in pattern) 
                for pattern in donation_scam_patterns
            )
            
            # Check for promotional spam patterns
            has_promotional_spam = any(
                all(kw in text for kw in pattern) 
                for pattern in promotional_spam_patterns
            )
            
            # Override classification if it's marked as safe but has scam patterns
            if label.lower() in ['safe', 'legitimate'] and (has_donation_scam or has_promotional_spam):
                label = "fraudulent"
                reason = "Contains suspicious scam patterns"
            else:
                reason = "Model classification"
        else:
            reason = "Model classification (legitimate source)"
        
        return jsonify({
            "status": label,
            "reason": reason,
            "subject": subject,
            "body": body
        })
    except Exception as e:
        return jsonify({"error": "Auto model inference failed", "reason": str(e)}), 500

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

        # Add contextual checks for scam patterns (same as auto scan - more specific than just keywords)
        # Check for legitimate domains first
        legitimate_domains = [
            "github.com", "google.com", "microsoft.com", "amazon.com", "linkedin.com",
            "stackoverflow.com", "medium.com", "dev.to", "atlassian.com", "slack.com",
            "discord.com", "reddit.com", "twitter.com", "facebook.com", "instagram.com"
        ]
        
        is_from_legitimate_source = any(domain in text for domain in legitimate_domains)
        
        # Only apply keyword detection if NOT from legitimate sources
        if not is_from_legitimate_source:
            # More specific scam patterns (combinations of keywords)
            donation_scam_patterns = [
                ("donate", "bank transfer"), ("charity", "account details"), 
                ("fund", "wire"), ("urgent", "donation"), ("relief", "payment"),
                ("ngo", "send money"), ("foundation", "transfer")
            ]
            
            promotional_spam_patterns = [
                ("exclusive deal", "act fast"), ("limited time", "only"), 
                ("flash sale", "hurry up"), ("you've won", "claim now"),
                ("amazing deal", "order now"), ("special offer", "limited stock"),
                ("congratulations", "prize"), ("discount", "expires")
            ]
            
            # Check for donation scam patterns
            has_donation_scam = any(
                all(kw in text for kw in pattern) 
                for pattern in donation_scam_patterns
            )
            
            # Check for promotional spam patterns
            has_promotional_spam = any(
                all(kw in text for kw in pattern) 
                for pattern in promotional_spam_patterns
            )
            
            # Override classification if it's marked as safe but has scam patterns
            if label.lower() in ['safe', 'legitimate'] and (has_donation_scam or has_promotional_spam):
                label = "fraudulent"
                reason = "Contains suspicious scam patterns"
            else:
                reason = "Model classification"
        else:
            reason = "Model classification (legitimate source)"

        return jsonify({
            "status": label,
            "reason": reason,
            "subject": subject,
            "body": body
        })
    except Exception as e:
        return jsonify({"error": "Model inference failed", "reason": str(e)}), 500


# --- Run App ---
if __name__ == '__main__':
    app.run(debug=True)
