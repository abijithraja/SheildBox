# 🛡️ ShieldBox Clean Architecture

## 📋 Single Telegram Alert Logic

✅ **FIXED**: Removed duplicate Telegram logic to prevent double notifications.

## 🔄 Clean Data Flow:

```
Chrome Extension
      ↓
   main.py (ML model + classification)
      ↓
  [HTTP POST to mqtt_service.py:5001/mqtt-publish]
      ↓
mqtt_service.py
   ├─→ MQTT to ESP32
   └─→ Telegram Alert (if threat detected)
```

## 🎯 Key Changes Made:

### ✅ 1. main.py (Port 5000)
- **REMOVED**: All Telegram alert logic
- **REMOVED**: `/send-telegram` endpoint 
- **KEPT**: ML model processing
- **KEPT**: HTTP calls to mqtt_service.py
- **SIMPLIFIED**: Clean separation of concerns

### ✅ 2. mqtt_service.py (Port 5001)  
- **HANDLES**: All Telegram alerts
- **HANDLES**: All MQTT to ESP32
- **ENDPOINTS**:
  - `POST /mqtt-publish` - Sends MQTT + Telegram
  - `POST /send-telegram` - Direct Telegram only
  - `GET /forward-alert` - Forward alerts
  - `GET /health` - Health check

## 📡 How It Works Now:

### Email Scanning Flow:
1. **Extension** scans email
2. **main.py** processes with ML model
3. **main.py** calls `mqtt_service.py/mqtt-publish`
4. **mqtt_service.py** sends:
   - MQTT message to ESP32
   - Telegram alert (if threat detected)

### Automatic Telegram Alerts:
- ✅ **Phishing** → `🚨 ShieldBox THREAT DETECTED: Phishing email detected!`
- ✅ **Scam** → `🚨 ShieldBox THREAT DETECTED: Scam email detected!`
- ✅ **Fraudulent** → `🚨 ShieldBox THREAT DETECTED: Fraudulent email detected!`
- ✅ **Suspicious** → `🚨 ShieldBox THREAT DETECTED: Suspicious content detected!`
- ❌ **Safe** → No Telegram alert (reduces spam)

## 🧪 Testing:

### Run Clean Architecture Test:
```bash
python test_telegram.py
```

### Manual MQTT + Telegram Test:
```bash
curl -X POST http://127.0.0.1:5001/mqtt-publish \
  -H "Content-Type: application/json" \
  -d '{"message": "phishing", "telegram_enabled": true}'
```

### Direct Telegram Test:
```bash
curl -X POST http://127.0.0.1:5001/send-telegram \
  -H "Content-Type: application/json" \
  -d '{"message": "Test alert", "type": "test"}'
```

## 🎯 Benefits:

1. **No Double Alerts** - Single Telegram logic point
2. **Clean Separation** - main.py focuses on ML, mqtt_service.py handles notifications  
3. **Easy Maintenance** - All Telegram config in one place
4. **Better Performance** - No duplicate processing
5. **Scalable** - Easy to add more notification channels

## 🔧 Configuration:

All Telegram settings are in `mqtt_service.py`:
```python
TELEGRAM_BOT_TOKEN = "8380628852:AAFd9hx8yYWCsDo1chnnhMKQMfkAM1psyDw"
TELEGRAM_CHAT_ID = "-4977450000"
```

## 🚀 Usage:

1. **Start main app**: `python main.py`
2. **Start MQTT service**: `python mqtt_service.py`
3. **Use extension** - alerts automatically flow through clean architecture

**Result**: Single, clean notification flow with no duplicates! 🎯
