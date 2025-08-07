
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
def send_to_mqtt_service(label, topic="shieldbox/email_scan", iot_enabled=True, telegram_enabled=True):
    """Send classification result to dedicated MQTT service with Telegram handling"""
    import threading
    
    def _async_send():
        if not iot_enabled:
            print("🔇 IoT disabled - MQTT message not sent")
        else:
            try:
                response = requests.post("http://127.0.0.1:5001/mqtt-publish", 
                                       json={
                                           "message": label, 
                                           "topic": topic,
                                           "telegram_enabled": telegram_enabled
                                       },
                                       timeout=2)  # Quick timeout to avoid blocking
                print("📡 Sent to MQTT Service:", response.json())
            except Exception as e:
                print("❌ Failed to send to MQTT Service:", e)
    
    # Run in background thread to avoid blocking main request
    thread = threading.Thread(target=_async_send, daemon=True)
    thread.start()

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
print("🚀 Loading auto email model with ultra-fast optimizations...")
auto_email_model_package = load_auto_email_model()

# === ULTRA-FAST OPTIMIZATION: Bypass all checks and cache everything ===
# Determine model type once and extract all components
try:
    if hasattr(auto_email_model_package, 'predict'):
        # Direct pipeline - fastest path
        _FAST_MODEL = auto_email_model_package
        _MODEL_MODE = 'direct'
        print("✅ Direct pipeline model - FASTEST mode")
    elif isinstance(auto_email_model_package, dict):
        if 'model' in auto_email_model_package and hasattr(auto_email_model_package['model'], 'predict'):
            if 'vectorizer' in auto_email_model_package:
                # Complete package
                _FAST_MODEL = auto_email_model_package['model'] 
                _FAST_VECTORIZER = auto_email_model_package['vectorizer']
                _FAST_ENCODER = auto_email_model_package['label_encoder']
                _MODEL_MODE = 'complete'
                print("✅ Complete model cached - OPTIMIZED mode")
            else:
                # Pipeline in dict
                _FAST_MODEL = auto_email_model_package['model']
                _MODEL_MODE = 'pipeline'
                print("✅ Pipeline model cached - FAST mode")
        else:
            raise ValueError("Invalid model package")
    else:
        # Fallback - create from individual components
        _FAST_MODEL = email_model
        _FAST_VECTORIZER = email_vectorizer  
        _FAST_ENCODER = email_label_encoder
        _MODEL_MODE = 'fallback'
        print("⚠️ Using fallback email model")
except Exception as e:
    print(f"⚠️ Model loading issue: {e}, using fallback")
    _FAST_MODEL = email_model
    _FAST_VECTORIZER = email_vectorizer  
    _FAST_ENCODER = email_label_encoder
    _MODEL_MODE = 'fallback'

print(f"🚀 ULTRA-FAST model ready. Mode: {_MODEL_MODE}")

# === ULTRA-FAST PATTERNS: Enhanced fraud detection patterns ===
import re
_INSTANT_PATTERNS = re.compile(
    r'\b(?:donate.*(?:bank|transfer|wire|account)|'
    r'charity.*(?:details|money|send)|'
    r'urgent.*(?:donation|sponsor|child|life|help)|'
    r'sponsor.*(?:child|life|save)|'
    r'save.*(?:life|child|children)|'
    r'shelter.*(?:gone|destroyed|need)|'
    r'lives.*(?:in.*your.*hands|depend|urgent)|'
    r'exclusive.*(?:deal|fast)|'
    r'limited.*(?:time|stock)|'
    r'you.*won.*claim|'
    r'congratulations.*prize|'
    r'flash.*sale.*hurry|'
    r'amazing.*deal.*now|'
    r'their.*shelter.*is.*gone|'
    r'urgent.*sponsor.*child|'
    r'dear.*(?:kind|friend).*urgent)\b', 
    re.IGNORECASE | re.DOTALL
)

_LEGIT_DOMAINS = re.compile(r'(?:github|google|microsoft|amazon|linkedin|stackoverflow|medium|dev\.to|atlassian|slack|discord|reddit|twitter|facebook|instagram)\.com', re.IGNORECASE)

# === INSTANT CACHE: Bigger cache for better hit rate ===
_INSTANT_CACHE = {}
_CACHE_SIZE = 0
MAX_CACHE = 1000  # Even larger cache for better hit rates

# === WARMUP CACHE: Pre-load common responses ===
_WARMUP_RESPONSES = {
    "": ("safe", "empty content"),
    "no content": ("safe", "no content"),
    "loading": ("safe", "loading state"),
    "please wait": ("safe", "system message"),
    "hello": ("safe", "greeting"),
    "hi": ("safe", "greeting"),
    "thanks": ("safe", "polite message"),
    "thank you": ("safe", "polite message"),
}

# Pre-populate cache with common responses
for text, response in _WARMUP_RESPONSES.items():
    text_key = hash(text[:200]) % 50000
    _INSTANT_CACHE[text_key] = response
    _CACHE_SIZE += 1

print(f"🚀 Cache warmed up with {len(_WARMUP_RESPONSES)} common responses")

# === PATTERN CACHE: Pre-compile for ultra speed ===
_PATTERN_CACHE = {}

def _ultra_fast_predict(text):
    """Ultra-optimized prediction with minimal overhead"""
    global _CACHE_SIZE
    
    # Ultra-fast cache check with better hashing
    text_key = hash(text[:300]) % 100000  # Even better hash distribution
    if text_key in _INSTANT_CACHE:
        return _INSTANT_CACHE[text_key]
    
    # === INSTANT PATTERN CHECK: Check patterns first for speed ===
    text_lower = text.lower()  # Single lowercase conversion
    
    # Quick length check - very short texts are usually safe
    if len(text_lower.strip()) < 10:
        result = ("safe", "too short to analyze")
        if _CACHE_SIZE < MAX_CACHE:
            _INSTANT_CACHE[text_key] = result
            _CACHE_SIZE += 1
        return result
    
    # Legitimate source check (fastest path)
    if _LEGIT_DOMAINS.search(text_lower):
        result = ("safe", "legitimate source")
        if _CACHE_SIZE < MAX_CACHE:
            _INSTANT_CACHE[text_key] = result
            _CACHE_SIZE += 1
        return result
    
    # Pattern-based detection (faster than model)
    if _INSTANT_PATTERNS.search(text_lower):
        result = ("fraudulent", "scam patterns detected")
        if _CACHE_SIZE < MAX_CACHE:
            _INSTANT_CACHE[text_key] = result
            _CACHE_SIZE += 1
        return result
    
    # === ENHANCED FRAUD DETECTION: Match manual scan logic ===
    # Check for donation scam patterns (same as manual scan)
    donation_scam_patterns = [
        ("urgent", "sponsor"), ("shelter", "gone"), ("lives", "hands"),
        ("donate", "child"), ("save", "life"), ("urgent", "help"),
        ("charity", "children"), ("sponsor", "child"), ("fund", "urgent"),
        ("donation", "urgent"), ("help", "children"), ("save", "children")
    ]
    
    # Check for promotional spam patterns
    promotional_spam_patterns = [
        ("exclusive deal", "act fast"), ("limited time", "only"), 
        ("flash sale", "hurry up"), ("you've won", "claim now"),
        ("amazing deal", "order now"), ("special offer", "limited stock"),
        ("congratulations", "prize"), ("discount", "expires")
    ]
    
    # Enhanced pattern matching
    has_donation_scam = any(
        all(kw in text_lower for kw in pattern) 
        for pattern in donation_scam_patterns
    )
    
    has_promotional_spam = any(
        all(kw in text_lower for kw in pattern) 
        for pattern in promotional_spam_patterns
    )
    
    if has_donation_scam or has_promotional_spam:
        result = ("fraudulent", "donation scam patterns detected" if has_donation_scam else "promotional spam detected")
        if _CACHE_SIZE < MAX_CACHE:
            _INSTANT_CACHE[text_key] = result
            _CACHE_SIZE += 1
        return result
    
    # Model prediction - optimized path (only if no patterns match)
    try:
        if _MODEL_MODE == 'direct':
            label = _FAST_MODEL.predict([text_lower])[0]
        elif _MODEL_MODE == 'complete':
            vector = _FAST_VECTORIZER.transform([text_lower])
            prediction = _FAST_MODEL.predict(vector)[0]
            label = _FAST_ENCODER.inverse_transform([prediction])[0]
        elif _MODEL_MODE == 'pipeline':
            label = _FAST_MODEL.predict([text_lower])[0]
        else:  # fallback - use manual scan model for consistency
            vector = _FAST_VECTORIZER.transform([text_lower])
            prediction = _FAST_MODEL.predict(vector)[0]
            label = _FAST_ENCODER.inverse_transform([prediction])[0]
        
        # === CONSISTENCY CHECK: Override if model says safe but has suspicious keywords ===
        if label.lower() in ['safe', 'legitimate']:
            # Additional fraud keyword check for edge cases
            suspicious_keywords = [
                'urgent', 'sponsor', 'donate', 'charity', 'fund', 'help children',
                'save life', 'shelter gone', 'lives in your hands', 'dear kind'
            ]
            keyword_count = sum(1 for keyword in suspicious_keywords if keyword in text_lower)
            
            if keyword_count >= 2:  # Multiple suspicious keywords
                label = "fraudulent" 
                reason = f"model override - {keyword_count} suspicious keywords detected"
            else:
                reason = "model classification"
        else:
            reason = "model classification"
            
    except Exception as e:
        # Fallback on any model error
        label = "safe"
        reason = f"model error: {str(e)[:50]}"
    
    # Cache result with aggressive caching
    result = (label, reason)
    if _CACHE_SIZE < MAX_CACHE:
        _INSTANT_CACHE[text_key] = result
        _CACHE_SIZE += 1
    
    return result

# --- Auto Email Scanner Route (subject + body -> multi-class) ---
@app.route('/scan-email-auto', methods=['POST'])
def scan_email_auto():
    import time
    start_time = time.time()
    
    data = request.get_json()
    subject = data.get("subject", "")
    body = data.get("body", "")
    iot_enabled = data.get("iot_enabled", True)  # Default to True for backward compatibility

    if not subject and not body:
        return jsonify({"error": "Missing subject and body"}), 400

    try:
        text = (subject + " " + body).lower()
        
        # === ULTRA-FAST PREDICTION: Single optimized function ===
        prediction_start = time.time()
        label, reason = _ultra_fast_predict(text)
        prediction_time = time.time() - prediction_start
        
        # === DEBUG: Log prediction details for troubleshooting ===
        print(f"🔍 Auto-scan DEBUG: '{text[:100]}...' → {label} ({reason})")
        
        result = {
            "status": label,
            "reason": reason,
            "subject": subject,
            "body": body,
            "performance": {
                "prediction_time": round(prediction_time * 1000, 2),  # ms
                "total_time": round((time.time() - start_time) * 1000, 2)  # ms
            }
        }
        
        # Publish classification result to ESP32 via MQTT Service (async-style)
        mqtt_start = time.time()
        send_to_mqtt_service(label, "shieldbox/email_scan", iot_enabled)
        mqtt_time = time.time() - mqtt_start
        
        result["performance"]["mqtt_time"] = round(mqtt_time * 1000, 2)
        
        total_time = time.time() - start_time
        print(f"📊 Auto scan completed in {total_time:.3f}s (prediction: {prediction_time:.3f}s, mqtt: {mqtt_time:.3f}s)")
        
        return jsonify(result)
    except Exception as e:
        total_time = time.time() - start_time
        print(f"❌ Auto scan failed after {total_time:.3f}s: {e}")
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

        # === DEBUG: Log manual scan details for comparison ===
        print(f"🔍 Manual scan DEBUG: '{text[:100]}...' → {label} ({reason})")

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

# --- Run App ---
if __name__ == '__main__':
    app.run(debug=True)
