ShieldBox - Advanced Email, URL & IoT Security System
ShieldBox is a comprehensive Chrome extension with IoT integration that protects users from phishing attacks, fraudulent emails, spam, and malware by analyzing both URLs and email content in real-time using advanced machine learning algorithms. It not only alerts you in the browser but also sends real-time phishing alerts to an IoT device, complete with LED indicators, an LCD/OLED display, buzzer/voice module, and Telegram notifications for maximum security awareness.

🚀 Features
Email Security & Analysis
Real-time Email Scanning: Automatically detects phishing emails as you open them

Manual Email Analysis: Scan specific emails on-demand with detailed threat assessment

Advanced Threat Detection: Identifies phishing, fraud, malware, spam, and legitimate emails

Visual Security Indicators: Color-coded badges and alerts for different threat levels

Gmail Integration: Seamless integration with Gmail interface

Auto-Scan Toggle: Enable/disable automatic email monitoring with intelligent UI hiding

URL & Link Protection
Manual URL Scanning: Paste and analyze any URL for security threats

Link Validation: Advanced URL pattern matching and threat detection

Real-time Results: Instant feedback on link safety status

Multiple Threat Categories: Detects phishing, spam, fraud, malware, and safe links

IoT Security Alerts
ESP32 Integration: Connects your ShieldBox backend to an ESP32-based IoT security device

LED Indicators:

🔴 Red LED for dangerous/phishing/fraud/malware emails

🟢 Green LED for safe/legitimate emails

LCD/OLED Display: Shows email classification, risk percentage, and sender authenticity

Buzzer/Voice Alerts: Plays alert tones or voice warnings for dangerous emails

Telegram Notifications: Sends real-time alerts to your mobile device via Telegram Bot API

MQTT Protocol: Secure and lightweight messaging between backend and IoT hardware

📁 Project Structure
bash
Copy
Edit
ShieldBox/
├── Backend/                     # Python ML backend
│   ├── dataset_phishing.csv
│   ├── feature_extractor.py
│   ├── feature_scaler.pkl
│   ├── main.py                   # FastAPI backend server
│   ├── mqtt_server.py            # MQTT + Telegram alert handling
│   ├── phishing_model.pkl
│   ├── phishing_model_package.pkl
│   ├── requirements.txt
│   └── train_model.py
│
├── extension/                    # Chrome extension
│   ├── background.js
│   ├── content-script.js
│   ├── emailParser.js
│   ├── floatingpanel.html
│   ├── floatingpanel.js
│   ├── manifest.json
│   ├── popup.html
│   ├── popup.js
│   └── style.css
│
└── IoT/                          # ESP32 IoT firmware
    ├── shieldbox_iot.ino          # Main Arduino/ESP32 code
    ├── libraries/                 # Required libraries (WiFi, PubSubClient, etc.)
    └── wiring_diagram.png         # Hardware connection diagram
🔍 Email Classification System
Email Type	Description	Visual Indicator	Browser Behavior	IoT Behavior
Phishing	Steals credentials/personal info	🚨 Red badge	High-priority warning	Red LED, buzzer, Telegram alert
Fraud	Financial scams & deception	💰 Orange badge	Financial threat alert	Red LED, buzzer
Malware	Harmful attachments/links	🦠 Purple badge	Malware warning	Red LED, buzzer
Spam	Unsolicited marketing	📧 Yellow badge	Spam notification	Yellow icon on LCD
Safe	Verified safe emails	✅ Green badge	Safe confirmation	Green LED

🛠 IoT Hardware Setup
Components:

ESP32 development board

RGB LED or separate Red/Green LEDs

LCD/OLED Display (e.g., 16x2 I2C LCD)

Active Buzzer or ISD1820 Voice Module for audio alerts

220Ω Resistor (for LEDs)

Mini Breadboard & Jumper Wires

Functionality Flow:

Email is scanned in Chrome extension

Classification & risk percentage sent to backend

Backend publishes alert via MQTT to ESP32

ESP32 displays data on LCD, lights LED, and triggers buzzer/voice alert

Telegram message is sent simultaneously for remote alerts

🔧 Installation & Setup
Backend + IoT Setup
Start backend server (python main.py)

Start MQTT server (python mqtt_server.py)

Flash ESP32 firmware (shieldbox_iot.ino) via Arduino IDE

Connect ESP32 to Wi-Fi and MQTT broker

Open Gmail — IoT alerts will trigger automatically

🤝 Team Members
Abijith Raja B — Lead Developer, Chrome Extension & Backend

[Teammate Name 1] — IoT Hardware & ESP32 Programming

[Teammate Name 2] — Machine Learning & Model Training

[Teammate Name 3] — UI/UX Design & Frontend Integration
