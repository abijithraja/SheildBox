import requests

BOT_TOKEN = "8380628852:AAFd9hx8yYWCsDo1chnnhMKQMfkAM1psyDw"
CHAT_ID = "-4977450000"  # Use the ID you got from getUpdates
MESSAGE = "🚨 ShieldBox Alert: A phishing email was detected!"

url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
payload = {
    "chat_id": CHAT_ID,
    "text": MESSAGE
}

response = requests.post(url, json=payload)

if response.status_code == 200:
    print("✅ Message sent to Telegram group")
else:
    print("❌ Failed to send message:", response.text)
