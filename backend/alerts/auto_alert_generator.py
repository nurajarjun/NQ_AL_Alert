"""
Automatic Alert Generator
Continuously scans for high-quality setups and sends Telegram alerts
"""
import asyncio
import logging
from datetime import datetime, time
import pytz
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from utils.telegram_bot import TelegramBotHandler

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class AutoAlertGenerator:
    def __init__(self, telegram_bot):
        self.telegram_bot = telegram_bot
        self.symbols = ["NQ", "ES", "TQQQ", "SQQQ", "SOXL", "SOXS"]  # Futures + ETFs
        self.scan_interval = 900  # 15 minutes
        self.last_alert_time = {}
        self.min_alert_gap = 3600  # 1 hour between alerts for same symbol
        self.timezone = pytz.timezone('US/Eastern')
        
    async def should_scan(self):
        """Check if we should scan now (avoid pre-market/after-hours)"""
        now_et = datetime.now(self.timezone)
        current_time = now_et.time()
        
        # Market hours: 9:30 AM - 4:00 PM ET
        market_open = time(9, 30)
        market_close = time(16, 0)
        
        # After-hours: 4:00 PM - 8:00 PM ET (high win rate from backtest)
        after_hours_end = time(20, 0)
        
        # Scan during market hours and after-hours
        if market_open <= current_time <= after_hours_end:
            return True
        
        return False
    
    async def scan_for_setup(self, symbol):
        """Scan a symbol for high-quality setup"""
        try:
            # Import here to avoid circular dependencies
            from main import mobile_app_prediction_callback
            
            # Get prediction
            result = await mobile_app_prediction_callback(symbol)
            
            # Check if it's a real setup (not an error message)
            if "❌" in result or "No setup" in result or "NEUTRAL" in result:
                return None
            
            # Check if it contains entry/stop/target (indicates real setup)
            if "Entry:" in result and "Stop:" in result and "Target" in result:
                # Check confidence
                if "HIGH" in result or "MEDIUM" in result:
                    return result
            
            return None
            
        except Exception as e:
            logger.error(f"Error scanning {symbol}: {e}")
            return None
    
    async def send_alert(self, symbol, setup_message):
        """Send alert to Telegram"""
        try:
            # Check if we sent an alert recently for this symbol
            last_time = self.last_alert_time.get(symbol, 0)
            current_time = datetime.now().timestamp()
            
            if current_time - last_time < self.min_alert_gap:
                logger.info(f"Skipping {symbol} - alert sent {int((current_time - last_time)/60)} min ago")
                return
            
            # Send alert
            alert_header = f"🚨 AUTO ALERT - {symbol} SETUP DETECTED\n\n"
            full_message = alert_header + setup_message
            
            await self.telegram_bot.send_message(full_message)
            
            # Update last alert time
            self.last_alert_time[symbol] = current_time
            logger.info(f"✅ Alert sent for {symbol}")
            
        except Exception as e:
            logger.error(f"Error sending alert for {symbol}: {e}")
    
    async def run_continuous_scan(self):
        """Main loop - continuously scan for setups"""
        logger.info("🤖 Auto Alert Generator started")
        logger.info(f"Scanning: {', '.join(self.symbols)}")
        logger.info(f"Interval: {self.scan_interval/60:.0f} minutes")
        logger.info(f"Min gap between alerts: {self.min_alert_gap/60:.0f} minutes\n")
        
        while True:
            try:
                # Check if we should scan now
                if not await self.should_scan():
                    logger.info("Outside trading hours - sleeping...")
                    await asyncio.sleep(self.scan_interval)
                    continue
                
                logger.info(f"🔍 Scanning at {datetime.now().strftime('%H:%M:%S')}")
                
                # Scan each symbol
                for symbol in self.symbols:
                    setup = await self.scan_for_setup(symbol)
                    
                    if setup:
                        logger.info(f"✅ Setup found for {symbol}!")
                        await self.send_alert(symbol, setup)
                    else:
                        logger.info(f"  {symbol}: No setup")
                
                # Wait before next scan
                logger.info(f"Next scan in {self.scan_interval/60:.0f} minutes\n")
                await asyncio.sleep(self.scan_interval)
                
            except Exception as e:
                logger.error(f"Error in scan loop: {e}")
                await asyncio.sleep(60)  # Wait 1 min on error

async def main():
    """Start the auto alert generator"""
    # Initialize Telegram bot
    TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
    TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")
    
    if not TELEGRAM_BOT_TOKEN or not TELEGRAM_CHAT_ID:
        logger.error("❌ Telegram credentials not set")
        return
    
    telegram_bot = TelegramBotHandler(TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID)
    
    # Create and run generator
    generator = AutoAlertGenerator(telegram_bot)
    await generator.run_continuous_scan()

if __name__ == "__main__":
    asyncio.run(main())
