# 📱 ShieldBox Telegram Integration Guide

## 🚀 Available Endpoints:

### 1. Main Flask App (port 5000)
```
POST http://127.0.0.1:5000/send-telegram
```
**Body:**
```json
{
    "message": "Your alert message",
    "type": "test|phishing|scam|fraudulent|alert"
}
```

### 2. MQTT Service (port 5001)  
```
POST http://127.0.0.1:5001/send-telegram
```
**Body:**
```json
{
    "message": "Your alert message", 
    "type": "test|phishing|scam|fraudulent|alert"
}
```

## 📋 Message Types:

- **test**: `🧪 ShieldBox Test: [message]`
- **phishing**: `🚨 ShieldBox THREAT DETECTED: [message]`
- **scam**: `🚨 ShieldBox THREAT DETECTED: [message]`
- **fraudulent**: `🚨 ShieldBox THREAT DETECTED: [message]`
- **suspicious**: `🚨 ShieldBox THREAT DETECTED: [message]`
- **alert** (default): `ℹ️ ShieldBox: [message]`

## 🧪 Testing:

### Quick Test:
```bash
python test_telegram.py
```

### Manual Test:
```bash
python send_telegram.py
```

### cURL Examples:

#### Test Message:
```bash
curl -X POST http://127.0.0.1:5000/send-telegram \
  -H "Content-Type: application/json" \
  -d '{"message": "Testing ShieldBox!", "type": "test"}'
```

#### Threat Alert:
```bash
curl -X POST http://127.0.0.1:5000/send-telegram \
  -H "Content-Type: application/json" \
  -d '{"message": "Phishing email detected!", "type": "phishing"}'
```

## ⚙️ Integration Examples:

### From Python Code:
```python
import requests

# Send test message
requests.post("http://127.0.0.1:5000/send-telegram", json={
    "message": "ShieldBox is online!",
    "type": "test"
})

# Send threat alert
requests.post("http://127.0.0.1:5000/send-telegram", json={
    "message": "Dangerous email detected in user inbox!",
    "type": "phishing"
})
```

### From Extension JavaScript:
```javascript
// Send alert from browser extension
fetch("http://127.0.0.1:5000/send-telegram", {
    method: "POST",
    headers: {"Content-Type": "application/json"},
    body: JSON.stringify({
        message: "Suspicious link clicked!",
        type: "suspicious"
    })
});
```

## 🔧 Setup:

1. **Start Main App**: `python main.py`
2. **Start MQTT Service**: `python mqtt_service.py` 
3. **Test Integration**: `python test_telegram.py`

Both services will automatically send Telegram alerts when threats are detected!
