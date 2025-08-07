#include <WiFi.h>
#include <PubSubClient.h>

// WiFi credentials
const char* ssid = "User";
const char* password = "ABIJITHRAJA";

// MQTT
const char* mqtt_server = "broker.hivemq.com";
WiFiClient espClient;
PubSubClient client(espClient);

// Pins
#define RED_LED 5
#define GREEN_LED 18
#define BUZZER 19

void setup_wifi() {
  delay(10);
  Serial.println("Connecting to WiFi...");
  WiFi.begin(ssid, password);
  while (WiFi.status() != WL_CONNECTED) {
    delay(1000);
    Serial.print(".");
  }
  Serial.println("\nWiFi connected");
  Serial.print("IP address: ");
  Serial.println(WiFi.localIP());
}

void callback(char* topic, byte* payload, unsigned int length) {
  Serial.println("📡 MQTT callback triggered!");

  String message;
  for (unsigned int i = 0; i < length; i++) {
    message += (char)payload[i];
  }

  message.trim(); // 💡 IMPORTANT: Remove trailing whitespace
  message.toLowerCase(); // 💡 Case-insensitive matching

  Serial.print("📩 MQTT message received: ");
  Serial.println(message);

  // Reset outputs
  digitalWrite(RED_LED, LOW);
  digitalWrite(GREEN_LED, LOW);
  digitalWrite(BUZZER, LOW);

  // 🚨 Danger Messages
  if (message == "phishing" || message == "scam" ||
      message == "malware" || message == "fraudulent") {
    digitalWrite(RED_LED, HIGH);
    digitalWrite(BUZZER, HIGH);
    Serial.println("🚨 Alert: Dangerous Email!");
    delay(2000);  // Alert duration
    digitalWrite(RED_LED, LOW);
    digitalWrite(BUZZER, LOW);
  }

  // ⚠️ Spam Message
  else if (message == "spam") {
    Serial.println("⚠️ Warning: Spam Email");
    for (int i = 0; i < 3; i++) {
      digitalWrite(RED_LED, HIGH);
      delay(200);
      digitalWrite(RED_LED, LOW);
      delay(200);
    }
  }

  // ✅ Safe Email
  else if (message == "safe" || message == "legitimate") {
    digitalWrite(GREEN_LED, HIGH);
    Serial.println("✅ Safe Email");
  }

  // ❓ Unknown message
  else {
    Serial.println("❓ Unrecognized message received.");
  }
}

void reconnect() {
  while (!client.connected()) {
    Serial.print("Attempting MQTT connection...");
    if (client.connect("ESP32_ShieldBox")) {
      Serial.println("connected");
      client.subscribe("shieldbox/email_scan");
      Serial.println("✅ Subscribed to shieldbox/email_scan");
    } else {
      Serial.print("Failed, rc=");
      Serial.print(client.state());
      Serial.println(" retrying in 5 seconds...");
      delay(5000);
    }
  }
}

void setup() {
  Serial.begin(115200);

  pinMode(RED_LED, OUTPUT);
  pinMode(GREEN_LED, OUTPUT);
  pinMode(BUZZER, OUTPUT);

  digitalWrite(RED_LED, LOW);
  digitalWrite(GREEN_LED, LOW);
  digitalWrite(BUZZER, LOW);

  setup_wifi();
  client.setServer(mqtt_server, 1883);
  client.setCallback(callback);
}

void loop() {
  if (!client.connected()) {
    reconnect();
  }
  client.loop();
}
