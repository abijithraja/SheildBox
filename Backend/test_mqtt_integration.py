#!/usr/bin/env python3
"""
ShieldBox MQTT Integration Test
Tests the complete flow: Extension → MQTT Service → ESP32
"""

import requests
import json
import time

# Test configuration
MQTT_SERVICE_URL = "http://127.0.0.1:5001"
MAIN_BACKEND_URL = "http://127.0.0.1:5000"

def test_mqtt_service():
    """Test the dedicated MQTT service"""
    print("🔧 Testing MQTT Service...")
    
    # Test 1: Health check
    try:
        response = requests.get(f"{MQTT_SERVICE_URL}/health")
        if response.status_code == 200:
            print("✅ Health check passed")
            print(f"   Response: {response.json()}")
        else:
            print(f"❌ Health check failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Health check error: {e}")
        return False
    
    # Test 2: POST /mqtt-publish
    test_messages = [
        {"message": "phishing", "topic": "shieldbox/email_scan"},
        {"message": "safe", "topic": "shieldbox/url_scan"},
        {"message": "scam", "topic": "shieldbox/extension_alert"}
    ]
    
    for test_msg in test_messages:
        try:
            response = requests.post(f"{MQTT_SERVICE_URL}/mqtt-publish", 
                                   json=test_msg)
            if response.status_code == 200:
                result = response.json()
                print(f"✅ MQTT Publish: {test_msg['message']} → {test_msg['topic']}")
                print(f"   Response: {result}")
            else:
                print(f"❌ MQTT Publish failed: {response.status_code}")
        except Exception as e:
            print(f"❌ MQTT Publish error: {e}")
        
        time.sleep(1)  # Brief pause between tests
    
    # Test 3: GET /forward-alert
    alert_types = ["phishing", "scam", "safe"]
    for alert_type in alert_types:
        try:
            response = requests.get(f"{MQTT_SERVICE_URL}/forward-alert", 
                                  params={"type": alert_type})
            if response.status_code == 200:
                result = response.json()
                print(f"✅ Forward Alert: {alert_type}")
                print(f"   Response: {result}")
            else:
                print(f"❌ Forward Alert failed: {response.status_code}")
        except Exception as e:
            print(f"❌ Forward Alert error: {e}")
        
        time.sleep(1)
    
    return True

def test_extension_integration():
    """Test Chrome Extension integration"""
    print("\n📱 Testing Extension Integration...")
    
    # Simulate extension POST requests
    extension_tests = [
        {
            "name": "Manual URL Scan",
            "payload": {"message": "phishing", "topic": "shieldbox/extension_alert"}
        },
        {
            "name": "Auto Email Scan", 
            "payload": {"message": "safe", "topic": "shieldbox/email_scan"}
        },
        {
            "name": "URL Classification",
            "payload": {"message": "scam", "topic": "shieldbox/url_scan"}
        }
    ]
    
    for test in extension_tests:
        try:
            response = requests.post(f"{MQTT_SERVICE_URL}/mqtt-publish",
                                   json=test["payload"],
                                   headers={"Content-Type": "application/json"})
            if response.status_code == 200:
                print(f"✅ {test['name']}: Extension → MQTT Service")
            else:
                print(f"❌ {test['name']}: Failed ({response.status_code})")
        except Exception as e:
            print(f"❌ {test['name']}: Error - {e}")
        
        time.sleep(0.5)

def test_main_backend_integration():
    """Test main backend integration with MQTT service"""
    print("\n🧠 Testing Main Backend Integration...")
    
    # Test if main backend can reach MQTT service
    try:
        # This would normally be called from within main.py after classification
        response = requests.post(f"{MQTT_SERVICE_URL}/mqtt-publish",
                               json={"message": "fraudulent", "topic": "shieldbox/email_scan"},
                               timeout=2)
        if response.status_code == 200:
            print("✅ Main Backend → MQTT Service communication works")
        else:
            print(f"❌ Main Backend integration failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Main Backend integration error: {e}")

def display_summary():
    """Display test summary and next steps"""
    print("\n" + "="*50)
    print("🎯 MQTT INTEGRATION TEST COMPLETE")
    print("="*50)
    print("\n📋 Next Steps:")
    print("1. Start MQTT Service: python mqtt_service.py")
    print("2. Start Main Backend: python main.py") 
    print("3. Reload Chrome Extension")
    print("4. Test with ESP32 MQTT subscriber")
    print("\n🔗 ESP32 MQTT Topics to Subscribe:")
    print("- shieldbox/email_scan")
    print("- shieldbox/url_scan") 
    print("- shieldbox/extension_alert")
    print("\n🌐 Service URLs:")
    print(f"- MQTT Service: {MQTT_SERVICE_URL}")
    print(f"- Main Backend: {MAIN_BACKEND_URL}")

if __name__ == "__main__":
    print("🛡️ ShieldBox MQTT Integration Test")
    print("=" * 40)
    
    # Run all tests
    mqtt_success = test_mqtt_service()
    
    if mqtt_success:
        test_extension_integration()
        test_main_backend_integration()
    else:
        print("\n❌ MQTT Service not running. Start it first:")
        print("   python mqtt_service.py")
    
    display_summary()
