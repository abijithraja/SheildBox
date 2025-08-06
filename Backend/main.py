
from flask import Flask, request, jsonify
from flask_cors import CORS
import joblib
import numpy as np
from feature_extractor import extract_features
from auto_email_model_loader import load_auto_email_model
import requests

# --- Flask App Setup ---
app = Flask(__name__)
CORS(app)  # Allow extension to access API

# --- Integration Function for MQTT Service ---
def send_to_mqtt_service(label, topic="shieldbox/email_scan", iot_enabled=True):
    """Send classification result to dedicated MQTT service"""
    if not iot_enabled:
        print("🔇 IoT disabled - MQTT message not sent")
        return
    
    try:
        response = requests.post("http://127.0.0.1:5001/mqtt-publish", json={
            "message": label,
            "topic": topic
        })
        print("📡 Sent to MQTT Service:", response.json())
    except Exception as e:
        print("❌ Failed to send to MQTT Service:", e)

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
    iot_enabled = data.get("iot_enabled", True)  # Default to True for backward compatibility

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
        
        # Publish classification result to ESP32 via MQTT Service
        send_to_mqtt_service(label, "shieldbox/email_scan", iot_enabled)
        
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
    iot_enabled = data.get("iot_enabled", True)  # Default to True for backward compatibility

    if not url.startswith("http"):
        return jsonify({ "url": url, "status": "invalid", "reason": "Not a valid URL" })

    try:
        features = extract_features(url)
        features_scaled = scaler.transform([features])
        prob = phishing_model.predict_proba(features_scaled)[0][1]
        is_phishing = int(prob >= threshold)
        
        # Determine classification result
        classification = "phishing" if is_phishing else "safe"
        
        # Publish classification result to ESP32 via MQTT Service
        send_to_mqtt_service(classification, "shieldbox/url_scan", iot_enabled)

        return jsonify({
            "url": url,
            "status": classification,
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
    iot_enabled = data.get("iot_enabled", True)  # Default to True for backward compatibility

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

        # Publish classification result to ESP32 via MQTT Service
        send_to_mqtt_service(label, "shieldbox/email_scan", iot_enabled)

        return jsonify({
            "status": label,
            "reason": reason,
            "subject": subject,
            "body": body
        })
    except Exception as e:
        return jsonify({"error": "Model inference failed", "reason": str(e)}), 500

# --- ESP32 Alert Forwarding Route (for extension proxy) ---
@app.route('/forward-alert', methods=['GET'])
def forward_alert():
    alert_type = request.args.get("type", "safe")
    iot_enabled = request.args.get("iot_enabled", "true").lower() == "true"  # Default to True
    
    try:
        # Publish to ESP32 via MQTT Service
        send_to_mqtt_service(alert_type, "shieldbox/extension_alert", iot_enabled)
        
        return jsonify({"status": "sent", "type": alert_type}), 200
    except Exception as e:
        print(f"❌ MQTT forward failed: {e}")
        return jsonify({"error": str(e)}), 500

# --- MQTT Publish Route (for extension status messages) ---
@app.route('/mqtt-publish', methods=['POST'])
def mqtt_publish():
    try:
        data = request.get_json()
        message = data.get("message", "safe")
        topic = data.get("topic", "shieldbox/extension_alert")
        iot_enabled = data.get("iot_enabled", True)  # Default to True for backward compatibility
        
        # Publish to ESP32 via MQTT Service
        send_to_mqtt_service(message, topic, iot_enabled)
        
        return jsonify({"status": "published", "message": message, "topic": topic}), 200
    except Exception as e:
        print(f"❌ MQTT publish failed: {e}")
        return jsonify({"error": str(e)}), 500


# --- Run App ---
if __name__ == '__main__':
    app.run(debug=True)
