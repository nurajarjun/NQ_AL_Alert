import requests
import time
import random

# Webhook Endpoint (Local)
url = "http://localhost:8001/webhook/tradingview"

# Base prices for NQ
base_price = 16500.0

alerts = [
    {
        "symbol": "NQ",
        "direction": "LONG",
        "entry": base_price,
        "stop": base_price - 50,
        "target1": base_price + 50,
        "target2": base_price + 100,
        "rsi": 55.5,
        "atr": 45.0,
        "volume_ratio": 1.2,
        "note": "Alert 1: Mild Bullish"
    },
    {
        "symbol": "NQ",
        "direction": "SHORT",
        "entry": base_price + 100,
        "stop": base_price + 150,
        "target1": base_price + 50,
        "target2": base_price,
        "rsi": 42.0,
        "atr": 48.0,
        "volume_ratio": 1.1,
        "note": "Alert 2: Mild Bearish"
    },
    {
        "symbol": "NQ",
        "direction": "LONG",
        "entry": base_price - 20,
        "stop": base_price - 70,
        "target1": base_price + 80,
        "target2": base_price + 180,
        "rsi": 65.0,
        "atr": 55.0,
        "volume_ratio": 2.5,
        "note": "Alert 3: Strong Momentum Long"
    },
    {
        "symbol": "NQ",
        "direction": "SHORT",
        "entry": base_price + 200,
        "stop": base_price + 250,
        "target1": base_price + 100,
        "target2": base_price + 50,
        "rsi": 32.0,
        "atr": 60.0,
        "volume_ratio": 1.8,
        "note": "Alert 4: Oversold/Reversal Watch"
    },
    {
        "symbol": "NQ",
        "direction": "LONG",
        "entry": base_price + 50,
        "stop": base_price,
        "target1": base_price + 100,
        "target2": base_price + 200,
        "rsi": 61.0,
        "atr": 40.0,
        "volume_ratio": 1.5,
        "note": "Alert 5: Standard Trend Join"
    }
]

print(f"🚀 Sending 5 Simulated Alerts to {url}...\n")

for i, alert in enumerate(alerts, 1):
    print(f"Sending {alert['note']}...")
    try:
        # Note: 'note' field isn't in spec but won't hurt
        response = requests.post(url, json=alert)
        if response.status_code == 200:
            print(f"✅ Alert {i} Sent! Response: {response.json()}")
        else:
            print(f"❌ Alert {i} Failed: {response.status_code} - {response.text}")
    except Exception as e:
        print(f"❌ Connection Error (is server running?): {e}")
    
    if i < 5:
        time.sleep(2)

print("\nDONE.")
