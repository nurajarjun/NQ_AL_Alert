"""
Simplified main.py for initial deployment
This version starts with minimal dependencies to ensure the server starts
"""
from fastapi import FastAPI, Request
from telegram import Bot
import os
from dotenv import load_dotenv
import logging
import uvicorn
import asyncio

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize FastAPI
app = FastAPI(
    title="NQ AI Alert System",
    description="Simple, actionable AI trading alerts",
    version="3.0.0"
)

# Initialize Telegram Bot
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

bot = None
if not TELEGRAM_BOT_TOKEN or not TELEGRAM_CHAT_ID:
    logger.error("❌ Telegram credentials not found!")
else:
    try:
        bot = Bot(token=TELEGRAM_BOT_TOKEN)
        logger.info("✅ Telegram bot initialized")
    except Exception as e:
        logger.error(f"❌ Failed to initialize Telegram bot: {e}")

@app.get("/")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "NQ AI Alert System",
        "version": "3.0.0-simplified",
        "telegram": "configured" if bot else "not configured"
    }

@app.get("/test")
async def test_telegram():
    """Test Telegram connection"""
    if not bot:
        return {"status": "error", "message": "Telegram bot not configured"}
    
    try:
        await bot.send_message(
            chat_id=TELEGRAM_CHAT_ID,
            text="🧪 Test message from NQ AI Alert System (Simplified)"
        )
        return {"status": "success", "message": "Test message sent"}
    except Exception as e:
        logger.error(f"Failed to send test message: {e}")
        return {"status": "error", "message": str(e)}

@app.post("/webhook/tradingview")
async def tradingview_webhook(request: Request):
    """Receive TradingView alerts"""
    try:
        data = await request.json()
        logger.info(f"📊 Received TradingView alert: {data}")
        
        if not bot:
            return {"status": "error", "message": "Telegram bot not configured"}
        
        # Send simple notification
        message = f"📊 TradingView Alert Received\n\n{data}"
        await bot.send_message(chat_id=TELEGRAM_CHAT_ID, text=message)
        
        return {"status": "success", "message": "Alert received and sent to Telegram"}
    except Exception as e:
        logger.error(f"❌ Failed to process alert: {e}")
        return {"status": "error", "message": str(e)}

if __name__ == "__main__":
    logger.info("=" * 60)
    logger.info("🚀 Starting NQ AI Alert System (Simplified)")
    logger.info("=" * 60)
    logger.info(f"Telegram Bot Token: {'✅ Configured' if TELEGRAM_BOT_TOKEN else '❌ Missing'}")
    logger.info(f"Telegram Chat ID: {'✅ Configured' if TELEGRAM_CHAT_ID else '❌ Missing'}")
    logger.info(f"Port: 8001")
    logger.info(f"Host: 0.0.0.0")
    logger.info("=" * 60)
    
    try:
        uvicorn.run(
            app,
            host="0.0.0.0",
            port=8001,
            log_level="info"
        )
    except Exception as e:
        logger.error(f"❌ Failed to start server: {e}")
        raise
