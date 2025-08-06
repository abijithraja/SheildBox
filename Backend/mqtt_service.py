from flask import Flask, request, jsonify
from flask_cors import CORS
import paho.mqtt.publish as publish

app = Flask(__name__)
CORS(app)  # Allow frontend or extension access

# === [POST] Publish MQTT Message ===
@app.route("/mqtt-publish", methods=["POST"])
def mqtt_publish():
    try:
        data = request.json
        message = data.get("message", "")
        topic = data.get("topic", "shieldbox/email_scan")  # default topic
        
        if message:
            print(f"📡 MQTT: Publishing '{message}' to topic '{topic}'")
            publish.single(topic, message, hostname="broker.hivemq.com")
            return jsonify({
                "status": "success",
                "message": message,
                "topic": topic
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
