import asyncio
from telegram import Bot

# Your bot token
BOT_TOKEN = "YOUR_BOT_TOKEN_HERE"

async def get_chat_id():
    bot = Bot(token=BOT_TOKEN)
    
    print("🔍 Getting your Chat ID...")
    print("\n📱 IMPORTANT: Send a message to your bot in Telegram NOW!")
    print("   (Search for your bot and send any message like 'Hello')\n")
    
    await asyncio.sleep(3)  # Give you time to send a message
    
    try:
        # Get updates (messages sent to the bot)
        updates = await bot.get_updates()
        
        if updates:
            # Get the chat ID from the most recent message
            chat_id = updates[-1].message.chat.id
            print(f"\n✅ SUCCESS! Your Chat ID is: {chat_id}")
            print(f"\n📝 SAVE THIS NUMBER: {chat_id}")
            print("\nYou'll need this for the .env file!")
        else:
            print("\n❌ No messages found.")
            print("Make sure you:")
            print("1. Found your bot in Telegram")
            print("2. Clicked 'Start' or sent a message")
            print("3. Run this script again")
    
    except Exception as e:
        print(f"\n❌ Error: {e}")

if __name__ == "__main__":
    asyncio.run(get_chat_id())
