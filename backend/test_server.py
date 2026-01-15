import requests
import json

print("🧪 Testing the NQ Alert Server...\n")

# Test 1: Health check
print("1. Testing health endpoint...")
try:
    response = requests.get("http://localhost:8000/")
    print(f"   ✅ Server is running: {response.json()}")
except Exception as e:
    print(f"   ❌ Error: {e}")

# Test 2: Test alert
print("\n2. Sending test alert to Telegram...")
try:
    response = requests.get("http://localhost:8000/test")
    result = response.json()
    print(f"   ✅ {result['message']}")
    print("   📱 Check your Telegram!")
except Exception as e:
    print(f"   ❌ Error: {e}")

# Test 3: Simulate TradingView webhook
print("\n3. Simulating TradingView alert...")
try:
    alert_data = {
        "direction": "LONG",
        "entry": 16850.5,
        "stop": 16820.0,
        "target1": 16920.0,
        "target2": 16980.0,
        "rsi": 58.5,
        "atr": 45.2,
        "volume_ratio": 1.4
    }
    
    response = requests.post(
        "http://localhost:8000/webhook/tradingview",
        json=alert_data
    )
    result = response.json()
    print(f"   ✅ {result['message']}")
    print("   📱 Check your Telegram for the NQ LONG alert!")
except Exception as e:
    print(f"   ❌ Error: {e}")

print("\n✅ All tests complete!")
