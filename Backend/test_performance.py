import requests
import time

def test_backend_performance():
    """Test backend performance with different email types"""
    
    test_cases = [
        {
            "name": "Short safe email",
            "subject": "Hi there",
            "body": "Just wanted to say hello!"
        },
        {
            "name": "Long legitimate email",
            "subject": "Weekly newsletter from GitHub",
            "body": "Welcome to your weekly update from GitHub. Here are the trending repositories this week..." * 10
        },
        {
            "name": "Phishing attempt",
            "subject": "Urgent donation needed",
            "body": "Please donate to our charity bank transfer wire account details urgent"
        },
        {
            "name": "Cached duplicate",
            "subject": "Hi there", 
            "body": "Just wanted to say hello!"
        }
    ]
    
    print("🚀 Testing Backend Performance...\n")
    
    for i, test in enumerate(test_cases, 1):
        print(f"Test {i}: {test['name']}")
        
        start_time = time.time()
        
        try:
            response = requests.post("http://127.0.0.1:5000/scan-email-auto", 
                                   json={
                                       "subject": test["subject"],
                                       "body": test["body"]
                                   },
                                   timeout=10)
            
            end_time = time.time()
            
            if response.status_code == 200:
                result = response.json()
                total_time = (end_time - start_time) * 1000
                
                print(f"  ✅ Status: {result['status']}")
                print(f"  ⏱️  Total time: {total_time:.2f}ms")
                
                if 'performance' in result:
                    perf = result['performance']
                    print(f"  🧠 ML prediction: {perf.get('prediction_time', 'N/A')}ms")
                    print(f"  📡 MQTT time: {perf.get('mqtt_time', 'N/A')}ms")
                
                print(f"  💡 Reason: {result['reason']}")
            else:
                print(f"  ❌ Error: HTTP {response.status_code}")
                
        except requests.exceptions.Timeout:
            print(f"  ⏱️  Timeout after 10s")
        except Exception as e:
            print(f"  ❌ Exception: {e}")
        
        print()  # Empty line
        time.sleep(1)  # Brief pause between tests

if __name__ == "__main__":
    print("Make sure main.py is running first!")
    print("Starting performance tests in 3 seconds...\n")
    time.sleep(3)
    test_backend_performance()
