import asyncio
from telegram import Bot
from dotenv import load_dotenv
import os

load_dotenv()

async def test_telegram():
    bot_token = os.getenv("TELEGRAM_BOT_TOKEN")
    chat_id = os.getenv("TELEGRAM_CHAT_ID")
    
    print(f"Bot Token: {bot_token[:20]}...")
    print(f"Chat ID: {chat_id}")
    
    bot = Bot(token=bot_token)
    
    message = """
🚨 TEST ALERT

This is a test message from your NQ AI Alert System!

If you're seeing this, everything is working! ✅

Time: Now
Status: Connected
    """
    
    try:
        result = await bot.send_message(chat_id=chat_id, text=message)
        print(f"\n✅ SUCCESS! Message sent!")
        print(f"Message ID: {result.message_id}")
        return True
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        return False

if __name__ == "__main__":
    success = asyncio.run(test_telegram())
    if success:
        print("\n🎉 Telegram is working! Check your phone!")
    else:
        print("\n❌ Something went wrong. Check the error above.")
