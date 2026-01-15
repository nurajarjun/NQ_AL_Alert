import requests
import time
from datetime import datetime

# Test alert endpoint
url = "http://localhost:8001/test"

# Send 5 alerts with 2-second intervals
print("Sending 5 test alerts to Telegram...\n")

for i in range(1, 6):
    try:
        current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        print(f"Alert {i}/5 - Sending at {current_time}...")
        
        response = requests.get(url)
        
        if response.status_code == 200:
            print(f"✅ Alert {i} sent successfully!")
        else:
            print(f"❌ Alert {i} failed: {response.status_code}")
        
        # Wait 2 seconds before next alert (except after the last one)
        if i < 5:
            print(f"Waiting 2 seconds...\n")
            time.sleep(2)
    
    except Exception as e:
        print(f"❌ Error sending alert {i}: {str(e)}")

print("\n✅ All 5 alerts sent!")
print("Check your Telegram for the test messages!")
