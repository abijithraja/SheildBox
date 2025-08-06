from flask import Flask, request, jsonify
from flask_cors import CORS
import paho.mqtt.publish as publish
import requests

app = Flask(__name__)
CORS(app)  # Allow frontend or extension access

# --- Telegram Alert Integration ---
TELEGRAM_BOT_TOKEN = "8380628852:AAFd9hx8yYWCsDo1chnnhMKQMfkAM1psyDw"
TELEGRAM_CHAT_ID = "-4977450000"  # Replace with your actual group ID

def send_telegram_alert(message):
    """Send alert to Telegram group"""
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": f"⚠️ ShieldBox Alert: {message}"
    }
    try:
        response = requests.post(url, json=payload)
        if response.status_code == 200:
            print("📨 Telegram alert sent successfully")
        else:
            print(f"❌ Telegram alert failed: {response.text}")
    except Exception as e:
        print(f"❌ Telegram exception: {e}")

# === [POST] Send Telegram Alert Directly ===
@app.route("/send-telegram", methods=["POST"])
def send_telegram():
    """Direct endpoint to send Telegram alerts"""
    try:
        data = request.json
        message = data.get("message", "")
        alert_type = data.get("type", "alert")
        
        if not message:
            return jsonify({"error": "No message provided"}), 400
            
        # Format message based on type
        if alert_type == "test":
            formatted_message = f"🧪 ShieldBox Test: {message}"
        elif alert_type in ['phishing', 'scam', 'fraudulent', 'suspicious']:
            formatted_message = f"🚨 ShieldBox THREAT DETECTED: {message}"
        else:
            formatted_message = f"ℹ️ ShieldBox: {message}"
        
        # Send to Telegram
        url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
        payload = {
            "chat_id": TELEGRAM_CHAT_ID,
            "text": formatted_message
        }
        
        response = requests.post(url, json=payload)
        
        if response.status_code == 200:
            print(f"📨 Telegram alert sent: {formatted_message}")
            return jsonify({
                "status": "success",
                "message": formatted_message,
                "telegram_response": response.json()
            }), 200
        else:
            print(f"❌ Telegram failed: {response.text}")
            return jsonify({
                "error": "Telegram API error",
                "details": response.text
            }), 500
            
    except Exception as e:
        print(f"❌ Telegram send exception: {e}")
        return jsonify({"error": str(e)}), 500
@app.route("/mqtt-publish", methods=["POST"])
def mqtt_publish():
    try:
        data = request.json
        message = data.get("message", "")
        topic = data.get("topic", "shieldbox/email_scan")  # default topic
        telegram_enabled = data.get("telegram_enabled", True)  # Enable Telegram by default
        
        if message:
            print(f"📡 MQTT: Publishing '{message}' to topic '{topic}'")
            publish.single(topic, message, hostname="broker.hivemq.com")
            
            # Send Telegram alert for dangerous classifications
            if telegram_enabled and message.lower() in ['phishing', 'scam', 'fraudulent', 'suspicious']:
                alert_messages = {
                    'phishing': 'Phishing email detected!',
                    'scam': 'Scam email detected!', 
                    'fraudulent': 'Fraudulent email detected!',
                    'suspicious': 'Suspicious content detected!'
                }
                alert_msg = alert_messages.get(message.lower(), f'{message} content detected!')
                send_telegram_alert(alert_msg)
            
            return jsonify({
                "status": "success",
                "message": message,
                "topic": topic,
                "telegram_sent": telegram_enabled and message.lower() in ['phishing', 'scam', 'fraudulent', 'suspicious']
            }), 200
        else:
            return jsonify({"error": "No message provided"}), 400

    except Exception as e:
        print(f"❌ MQTT publish failed: {e}")
        return jsonify({"error": str(e)}), 500

# === [GET] Forward alert from browser/extension (e.g., test via browser) ===
@app.route("/forward-alert", methods=["GET"])
def forward_alert():
    try:
        alert_type = request.args.get("type", "safe")  # e.g. phishing, scam
        topic = "shieldbox/extension_alert"

        print(f"📡 MQTT: Forwarding alert '{alert_type}' to ESP32")
        publish.single(topic, alert_type, hostname="broker.hivemq.com")

        return jsonify({
            "status": "sent",
            "type": alert_type
        }), 200
    except Exception as e:
        print(f"❌ MQTT forward failed: {e}")
        return jsonify({"error": str(e)}), 500

# === [GET] Health check ===
@app.route("/health", methods=["GET"])
def health_check():
    return jsonify({
        "status": "MQTT service running",
        "broker": "broker.hivemq.com"
    }), 200

# === Start Service ===
if __name__ == '__main__':
    print("🚀 Starting MQTT Service on port 5001...")
    app.run(host='0.0.0.0', port=5001, debug=True)
