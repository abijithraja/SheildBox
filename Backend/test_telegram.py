import requests
import time

def test_telegram_mqtt_service():
    """Test Telegram via MQTT service (port 5001) - PRIMARY METHOD"""
    print("🧪 Testing Telegram via MQTT Service (port 5001)...")
    
    try:
        response = requests.post("http://127.0.0.1:5001/send-telegram", json={
            "message": "Testing from MQTT service!",
            "type": "test"
        })
        
        if response.status_code == 200:
            print("✅ MQTT service Telegram test successful!")
            print(f"Response: {response.json()}")
        else:
            print(f"❌ MQTT service test failed: {response.text}")
            
    except Exception as e:
        print(f"❌ MQTT service exception: {e}")

def test_integrated_flow():
    """Test the integrated flow: main.py -> mqtt_service.py -> Telegram"""
    print("\n🔄 Testing Integrated Flow (main.py -> mqtt_service.py)...")
    
    try:
        # This should trigger both MQTT and Telegram via mqtt_service.py
        response = requests.post("http://127.0.0.1:5001/mqtt-publish", json={
            "message": "phishing",
            "topic": "shieldbox/test", 
            "telegram_enabled": True
        })
        
        if response.status_code == 200:
            print("✅ Integrated flow test successful!")
            result = response.json()
            print(f"MQTT sent: {result.get('status')}")
            print(f"Telegram sent: {result.get('telegram_sent')}")
        else:
            print(f"❌ Integrated flow test failed: {response.text}")
            
    except Exception as e:
        print(f"❌ Integrated flow exception: {e}")

def test_email_scan_flow():
    """Test actual email scanning that triggers alerts"""
    print("\n� Testing Email Scan Flow (should trigger Telegram for threats)...")
    
    try:
        # Test with phishing email - should trigger Telegram alert
        response = requests.post("http://127.0.0.1:5000/scan-email-auto", json={
            "subject": "Urgent donation needed",
            "body": "Please donate to our charity bank transfer wire account details urgent",
            "iot_enabled": True
        })
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Email scan successful!")
            print(f"Status: {result['status']}")
            print(f"Reason: {result['reason']}")
            print("📱 Check your Telegram for alert if status is fraudulent/phishing!")
        else:
            print(f"❌ Email scan failed: {response.text}")
            
    except Exception as e:
        print(f"❌ Email scan exception: {e}")

def test_original_script():
    """Test the original send_telegram.py script"""
    print("\n📱 Testing Original Telegram Script...")
    
    try:
        import subprocess
        result = subprocess.run(["python", "send_telegram.py"], 
                              capture_output=True, text=True, cwd=".")
        
        if result.returncode == 0:
            print("✅ Original script test successful!")
            print(f"Output: {result.stdout}")
        else:
            print(f"❌ Original script failed: {result.stderr}")
            
    except Exception as e:
        print(f"❌ Original script exception: {e}")

if __name__ == "__main__":
    print("🚀 ShieldBox Clean Telegram Integration Test")
    print("=" * 50)
    print("📋 New Architecture:")
    print("   Chrome Extension -> main.py -> mqtt_service.py -> ESP32 + Telegram")
    print("\nMake sure both main.py and mqtt_service.py are running!")
    print("\nStarting tests in 3 seconds...")
    time.sleep(3)
    
    # Test the clean architecture
    test_telegram_mqtt_service()
    time.sleep(2)
    
    test_integrated_flow() 
    time.sleep(2)
    
    test_email_scan_flow()
    time.sleep(2)
    
    test_original_script()
    
    print("\n" + "=" * 50)
    print("🏁 All tests completed!")
    print("📱 Check your Telegram group for alerts!")
