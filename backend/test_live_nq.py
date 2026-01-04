"""
LIVE TEST - NQ AI Alert System
Current NQ Price: 21880
This will send a REAL AI-analyzed alert to your Telegram
"""

import requests
import json

print("="*60)
print("🚀 TESTING NQ AI ALERT SYSTEM")
print("="*60)
print("\nCurrent NQ Price: 21880")
print("Testing with a LONG setup example...\n")

# Example NQ LONG setup at current price
alert_data = {
    "direction": "LONG",
    "entry": 21880.0,
    "stop": 21850.0,      # 30 points risk
    "target1": 21940.0,   # 60 points reward (2:1 R/R)
    "target2": 22000.0,   # 120 points reward (4:1 R/R)
    "rsi": 55.0,          # Neutral RSI
    "atr": 35.0,          # Average True Range
    "volume_ratio": 1.3   # Above average volume
}

print("📊 SETUP DETAILS:")
print(f"  Direction: {alert_data['direction']}")
print(f"  Entry: {alert_data['entry']}")
print(f"  Stop Loss: {alert_data['stop']} (Risk: {alert_data['entry'] - alert_data['stop']} pts)")
print(f"  Target 1: {alert_data['target1']} (Reward: {alert_data['target1'] - alert_data['entry']} pts)")
print(f"  Target 2: {alert_data['target2']} (Reward: {alert_data['target2'] - alert_data['entry']} pts)")
print(f"  RSI: {alert_data['rsi']}")
print(f"  ATR: {alert_data['atr']}")
print(f"  Volume: {alert_data['volume_ratio']}x average")

print("\n" + "="*60)
print("🤖 SENDING TO AI FOR ANALYSIS...")
print("="*60)

try:
    # Send to local server
    response = requests.post(
        "http://localhost:8000/webhook/tradingview",
        json=alert_data,
        timeout=30
    )
    
    if response.status_code == 200:
        result = response.json()
        print("\n✅ SUCCESS! Alert processed by AI")
        print("\nAI Response:")
        print(json.dumps(result, indent=2))
        
        if result.get('status') == 'success':
            print("\n" + "="*60)
            print("📱 CHECK YOUR TELEGRAM!")
            print("="*60)
            print("\nYou should receive an AI-analyzed alert that includes:")
            print("  • AI Quality Score (0-100)")
            print("  • Recommendation (YES/NO/MAYBE)")
            print("  • Risk Level (LOW/MEDIUM/HIGH)")
            print("  • Position Size Suggestion")
            print("  • Market Context (Sentiment, SPY trend)")
            print("  • AI Reasoning and Insights")
            print("\n" + "="*60)
        elif result.get('status') == 'filtered':
            print("\n" + "="*60)
            print("🔴 ALERT FILTERED OUT BY AI")
            print("="*60)
            print(f"\nAI Score: {result.get('score')}/100")
            print(f"Recommendation: {result.get('recommendation')}")
            print("\nThis means the AI determined this setup is LOW QUALITY")
            print("and protected you from a potentially bad trade!")
            print("\n" + "="*60)
    else:
        print(f"\n❌ Error: Server returned status code {response.status_code}")
        print(response.text)
        
except requests.exceptions.ConnectionError:
    print("\n❌ ERROR: Cannot connect to server")
    print("\nThe server is not running. Please start it first:")
    print("\n  1. Open a terminal")
    print("  2. cd d:\\Google\\.gemini\\antigravity\\scratch\\NQ-AI-Alerts\\backend")
    print("  3. python main.py")
    print("\nThen run this test again!")
    
except Exception as e:
    print(f"\n❌ ERROR: {str(e)}")
    print("\nCheck that:")
    print("  • Server is running (python main.py)")
    print("  • Dependencies installed (pip install -r requirements.txt)")
    print("  • .env file configured with API keys")

print("\n" + "="*60)
