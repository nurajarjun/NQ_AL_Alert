import os
import requests

# Get from environment or use the token from logs
BOT_TOKEN = "8593056133:AAHs1NOBNAa5uV_3iHhTBxh0GINIqzxDHwE"
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID", "")

if not CHAT_ID:
    print("ERROR: TELEGRAM_CHAT_ID not set")
    print("Please set it in your environment or edit this script")
    exit(1)

url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"

message = """
🔧 **DIRECT API TEST**

If you see this message, the Telegram API connection is working!

This was sent directly via HTTP request, bypassing the bot framework.

Next step: Debug why the bot framework times out.
"""

data = {
    "chat_id": CHAT_ID,
    "text": message,
    "parse_mode": "Markdown"
}

try:
    print(f"Sending test message to chat_id: {CHAT_ID}")
    response = requests.post(url, json=data, timeout=30)
    
    if response.status_code == 200:
        print("SUCCESS! Message sent successfully!")
        print(f"Response: {response.json()}")
    else:
        print(f"FAILED! HTTP {response.status_code}")
        print(f"Response: {response.text}")
        
except Exception as e:
    print(f"ERROR: {e}")
