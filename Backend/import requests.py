import requests

BOT_TOKEN = "AAFd9hx8yYWCsDo1chnnhMKQMfkAM1psyDw"

# Get updates (after you've sent a test message in the group)
response = requests.get(f"https://api.telegram.org/bot{BOT_TOKEN}/getUpdates")
data = response.json()

for result in data["result"]:
    try:
        chat = result["message"]["chat"]
        print(f"Group Name: {chat.get('title', 'Private Chat')} | Chat ID: {chat['id']}")
    except KeyError:
        pass
