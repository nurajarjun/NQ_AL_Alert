import requests

# Your bot token
BOT_TOKEN = "YOUR_BOT_TOKEN_HERE"

print("🔍 Checking for messages sent to your bot...\n")

# Get updates using simple HTTP request
url = f"https://api.telegram.org/bot{BOT_TOKEN}/getUpdates"
response = requests.get(url)

if response.status_code == 200:
    data = response.json()
    
    if data['ok'] and data['result']:
        # Get the most recent message
        latest_update = data['result'][-1]
        chat_id = latest_update['message']['chat']['id']
        
        print(f"✅ SUCCESS! Your Chat ID is: {chat_id}")
        print(f"\n📝 COPY THIS NUMBER: {chat_id}")
        print("\nYou'll need this for the next step!")
    else:
        print("❌ No messages found yet.")
        print("\nPlease:")
        print("1. Open Telegram")
        print("2. Search for your bot")
        print("3. Click 'START' button")
        print("4. Send any message (like 'Hello')")
        print("5. Run this script again: python get_chat_id_simple.py")
else:
    print(f"❌ Error: {response.status_code}")
    print("Check your bot token!")
