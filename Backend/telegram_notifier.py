import requests

class TelegramNotifier:
    def __init__(self, bot_token="8380628852:AAFd9hx8yYWCsDo1chnnhMKQMfkAM1psyDw"):
        self.bot_token = bot_token
        self.base_url = f"https://api.telegram.org/bot{bot_token}"
    
    def send_alert(self, chat_id, alert_type, details=None):
        """Send different types of ShieldBox alerts"""
        
        # Alert templates
        templates = {
            "phishing": "🎣 **PHISHING DETECTED**\n🚨 ShieldBox Alert: Phishing email detected!",
            "scam": "⚠️ **SCAM DETECTED**\n🚨 ShieldBox Alert: Scam email detected!",
            "fraudulent": "🚫 **FRAUD DETECTED**\n🚨 ShieldBox Alert: Fraudulent content detected!",
            "suspicious_url": "🔗 **SUSPICIOUS LINK**\n🚨 ShieldBox Alert: Dangerous URL detected!",
            "safe": "✅ **SAFE CONTENT**\n🛡️ ShieldBox: Content verified as safe",
        }
        
        # Get message template
        message = templates.get(alert_type.lower(), f"🚨 ShieldBox Alert: {alert_type}")
        
        # Add details if provided
        if details:
            message += f"\n\n📋 Details: {details}"
        
        # Add timestamp
        from datetime import datetime
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        message += f"\n\n⏰ Time: {timestamp}"
        
        return self.send_message(chat_id, message)
    
    def send_message(self, chat_id, text):
        """Send a message to Telegram chat"""
        url = f"{self.base_url}/sendMessage"
        payload = {
            "chat_id": chat_id,
            "text": text,
            "parse_mode": "Markdown"  # For formatting
        }
        
        try:
            response = requests.post(url, json=payload)
            if response.status_code == 200:
                print("✅ Message sent to Telegram")
                return True
            else:
                print("❌ Failed to send message:", response.text)
                return False
        except Exception as e:
            print(f"❌ Error sending Telegram message: {e}")
            return False

# Usage examples:
if __name__ == "__main__":
    notifier = TelegramNotifier()
    
    # Example chat ID (replace with your actual chat ID)
    CHAT_ID = "-4977450000"
    
    # Test different alert types
    print("Testing different alert types...")
    
    # Phishing alert
    notifier.send_alert(CHAT_ID, "phishing", "Subject: Urgent donation needed")
    
    # URL alert  
    notifier.send_alert(CHAT_ID, "suspicious_url", "URL: http://fake-bank.com/login")
    
    # Safe content
    notifier.send_alert(CHAT_ID, "safe", "Email from legitimate sender")
    
    # Custom message
    notifier.send_message(CHAT_ID, "🛡️ ShieldBox system is online and monitoring!")
