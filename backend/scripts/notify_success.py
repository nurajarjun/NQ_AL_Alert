
import os
import requests
import sys

def send_notification():
    token = os.getenv("TELEGRAM_BOT_TOKEN")
    chat_id = os.getenv("TELEGRAM_CHAT_ID")
    
    if not token or not chat_id:
        print("Error: TELEGRAM_BOT_TOKEN or TELEGRAM_CHAT_ID not found in env.")
        sys.exit(1)
        
    message = """
✅ **SYSTEM RESTORED**

The NQ AI Brain is back online.
All systems normal.
Latencies fixed.

You may use `/help` now.
"""

    url = f"https://api.telegram.org/bot{token}/sendMessage"
    data = {
        "chat_id": chat_id,
        "text": message,
        "parse_mode": "Markdown"
    }
    
    try:
        response = requests.post(url, json=data, timeout=10)
        response.raise_for_status()
        print("✅ Notification sent successfully!")
    except Exception as e:
        print(f"❌ Failed to send notification: {e}")
        if response:
            print(response.text)

if __name__ == "__main__":
    send_notification()
