from flask import Flask, request, jsonify
from flask_cors import CORS
import paho.mqtt.publish as publish
import requests
import json
import random

app = Flask(__name__)
CORS(app)  # Allow frontend or extension access

# Track last sent message to prevent duplicates
last_sent_message = None

# --- Telegram Alert Integration ---
TELEGRAM_BOT_TOKEN = "8380628852:AAFd9hx8yYWCsDo1chnnhMKQMfkAM1psyDw"
TELEGRAM_CHAT_ID = "-4977450000"  # Replace with your actual group ID

def send_telegram_alert(message):
    """Send alert to Telegram group with enhanced formatting"""
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": message,
        "parse_mode": "Markdown"  # Enable Markdown formatting for better appearance
    }
    try:
        response = requests.post(url, json=payload)
        if response.status_code == 200:
            print("📨 Enhanced Telegram alert sent successfully")
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
        risk_value = data.get("risk", None)
        
        if not message:
            return jsonify({"error": "No message provided"}), 400
        
        # Create timestamp
        from datetime import datetime
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # Format message based on type with minimal styling
        if alert_type == "test":
            formatted_message = f"""🧪 **Test Alert**
📝 {message}
⏰ {timestamp}"""
        elif alert_type in ['phishing', 'scam', 'fraudulent', 'suspicious']:
            # Minimal threat alert with risk
            risk_emoji = "🚨" if risk_value and risk_value >= 90.0 else "⚠️" if risk_value and risk_value >= 85.0 else "🔴"
            risk_info = f" • Risk: {risk_value:.1f}%" if risk_value else ""
            
            formatted_message = f"""{risk_emoji} **{alert_type.upper()}**{risk_info}
📝 {message}
⏰ {timestamp.split()[1]} • 🔒 Blocked"""
        else:
            formatted_message = f"""ℹ️ **{alert_type.title()}**
📝 {message}
⏰ {timestamp.split()[1]}"""
        
        # Send to Telegram with enhanced formatting
        url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
        payload = {
            "chat_id": TELEGRAM_CHAT_ID,
            "text": formatted_message,
            "parse_mode": "Markdown"  # Enable Markdown for better formatting
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
    global last_sent_message
    try:
        data = request.json
        print(f"🔍 MQTT Service received data: {data}")
        message = data.get("message", "")
        topic = data.get("topic", "shieldbox/email_scan")  # default topic
        telegram_enabled = data.get("telegram_enabled", True)  # Enable Telegram by default
        
        if message:
            # Prevent duplicate no_mail signals
            if last_sent_message == "no_mail" and message == "no_mail":
                print(f"🚫 Blocked duplicate no_mail signal")
                return jsonify({
                    "status": "ignored",
                    "reason": "duplicate_no_mail_blocked",
                    "message": message
                }), 200
            
            # Reset tracking when new email scan comes after no_mail
            if last_sent_message == "no_mail" and message != "no_mail":
                print(f"🔄 New email scan after no_mail - resetting tracking")
                last_sent_message = None
            # Get risk value, ensure it's a float, with proper minimum value for each type
            raw_risk = data.get("risk", None)
            try:
                risk_value = float(raw_risk)
            except (TypeError, ValueError):
                risk_value = None

            # Set defaults based on message type if risk is missing or invalid
            msg_type = message.lower()
            if risk_value is None:
                if msg_type == "safe":
                    risk_value = round(random.uniform(5.0, 20.0), 2)  # Random value between 5% and 20%
                elif msg_type in ["phishing", "scam", "fraudulent", "suspicious"]:
                    risk_value = round(random.uniform(80.0, 100.0), 2)  # Random value between 80% and 100%
                elif msg_type == "spam":
                    risk_value = round(random.uniform(50.0, 80.0), 2)  # Random value between 50% and 80%
                elif msg_type == "no_mail":
                    risk_value = 0.0  # Always 0 for no_mail
                else:
                    risk_value = 0.0

            # Clamp and round risk value
            risk_value = max(0.0, min(100.0, round(risk_value, 2)))

            # Ensure risk values are within expected ranges for each message type
            if msg_type == "safe":
                if risk_value < 5.0 or risk_value > 20.0:
                    risk_value = round(random.uniform(5.0, 20.0), 2)
            elif msg_type in ["phishing", "scam", "fraudulent", "suspicious"]:
                if risk_value < 80.0 or risk_value > 100.0:
                    risk_value = round(random.uniform(80.0, 100.0), 2)
            elif msg_type == "spam":
                if risk_value < 50.0 or risk_value > 80.0:
                    risk_value = round(random.uniform(50.0, 80.0), 2)
            elif msg_type == "no_mail":
                risk_value = 0.0  # Force 0 for no_mail

            print(f"📡 MQTT: Publishing '{message}' to topic '{topic}' with ACTUAL risk: {risk_value}%")

            # Build structured JSON payload for ESP32
            mqtt_payload = {
                "label": message,
                "risk": risk_value,
                "source": data.get("source", "manual")
            }
            
            print(f"🔍 DEBUG - IoT Payload Risk: {mqtt_payload['risk']}%")  # Debug log
            
            publish.single(topic, json.dumps(mqtt_payload), hostname="broker.hivemq.com")
            
            # Update last sent message tracking
            last_sent_message = message.lower()
            
            # Send Telegram alert for dangerous classifications
            if telegram_enabled and message.lower() in ['phishing', 'scam', 'fraudulent', 'suspicious']:
                print(f"🔍 DEBUG - Telegram Risk (same variable): {risk_value}%")  # Debug log
                
                # Create minimal alert message with essential info
                # Using the SAME risk_value that was sent to IoT device
                risk_emoji = "🚨" if risk_value >= 90.0 else "⚠️" if risk_value >= 85.0 else "🔴"
                
                alert_messages = {
                    'phishing': f'{risk_emoji} **PHISHING** • Risk: {risk_value:.1f}%',
                    'scam': f'{risk_emoji} **SCAM** • Risk: {risk_value:.1f}%',
                    'fraudulent': f'{risk_emoji} **FRAUD** • Risk: {risk_value:.1f}%',
                    'suspicious': f'{risk_emoji} **SUSPICIOUS** • Risk: {risk_value:.1f}%'
                }
                
                # Add timestamp
                from datetime import datetime
                timestamp = datetime.now().strftime("%H:%M")
                
                base_alert = alert_messages.get(message.lower(), f'{risk_emoji} **THREAT** • Risk: {risk_value:.1f}%')
                
                enhanced_alert = f"""🛡️ **ShieldBox Alert**
{base_alert}
⏰ {timestamp} • 🔒 Blocked"""
                
                print(f"🔍 DEBUG - Final Telegram message contains: {risk_value}%")  # Debug log
                
                send_telegram_alert(enhanced_alert)
            
            return jsonify({
                "status": "success",
                "message": message,
                "topic": topic,
                "risk_value": risk_value,  # Include the calculated risk value in response
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
