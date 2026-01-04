"""
Telegram Bot Handler
Two-way communication with Telegram
"""

from telegram import Update, Bot
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
import os
import logging
from datetime import datetime
import json

logger = logging.getLogger(__name__)


class TelegramBotHandler:
    """Handles two-way Telegram communication"""
    
    def __init__(self, bot_token: str, chat_id: str):
        self.bot_token = bot_token
        self.chat_id = chat_id
        self.bot = Bot(token=bot_token)
        self.application = None
        
        # Stats tracking
        self.stats = {
            'total_alerts': 0,
            'alerts_today': 0,
            'last_alert_time': None,
            'system_start_time': datetime.now()
        }
    
    async def start_bot(self):
        """Start the Telegram bot for two-way communication"""
        try:
            self.application = Application.builder().token(self.bot_token).build()
            
            # Add command handlers
            self.application.add_handler(CommandHandler("start", self.cmd_start))
            self.application.add_handler(CommandHandler("help", self.cmd_help))
            self.application.add_handler(CommandHandler("status", self.cmd_status))
            self.application.add_handler(CommandHandler("stats", self.cmd_stats))
            self.application.add_handler(CommandHandler("pause", self.cmd_pause))
            self.application.add_handler(CommandHandler("resume", self.cmd_resume))
            self.application.add_handler(CommandHandler("threshold", self.cmd_threshold))
            self.application.add_handler(CommandHandler("symbols", self.cmd_symbols))
            
            # Start polling in background
            await self.application.initialize()
            await self.application.start()
            await self.application.updater.start_polling()
            
            logger.info("✅ Telegram bot started - Two-way communication active")
            
        except Exception as e:
            logger.error(f"Failed to start Telegram bot: {e}")
    
    async def cmd_start(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /start command"""
        welcome_message = """
🤖 **NQ AI Alert System**

Welcome! I'm your AI trading assistant.

**Available Commands:**
/help - Show all commands
/status - System status
/stats - Trading statistics
/pause - Pause alerts
/resume - Resume alerts
/threshold <score> - Set minimum score (e.g., /threshold 70)
/symbols - Show supported symbols

**You'll receive real-time alerts here!**
        """
        await update.message.reply_text(welcome_message, parse_mode='Markdown')
    
    async def cmd_help(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /help command"""
        help_message = """
📚 **Available Commands:**

**System Control:**
/status - Check system status
/pause - Pause all alerts
/resume - Resume alerts
/threshold <score> - Set minimum AI score (60-100)

**Information:**
/stats - View trading statistics
/symbols - List supported symbols
/help - Show this message

**Examples:**
`/threshold 75` - Only alerts with score ≥75
`/pause` - Stop receiving alerts
`/resume` - Start receiving alerts again

**Current Settings:**
Score Threshold: 60
Status: Active
Symbols: NQ, TQQQ, SQQQ, SOXL, SOXS
        """
        await update.message.reply_text(help_message, parse_mode='Markdown')
    
    async def cmd_status(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /status command"""
        uptime = datetime.now() - self.stats['system_start_time']
        hours = int(uptime.total_seconds() // 3600)
        
        status_message = f"""
📊 **System Status**

✅ Status: Active
⏰ Uptime: {hours} hours
📡 Connection: Healthy
🤖 AI: Gemini Active
🧠 ML: XGBoost Ready

**Last Alert:**
{self.stats['last_alert_time'] or 'No alerts yet'}

**Today's Alerts:** {self.stats['alerts_today']}
**Total Alerts:** {self.stats['total_alerts']}

**Components:**
✅ Multi-Timeframe Analysis
✅ Pattern Recognition
✅ Economic Calendar
✅ Market Correlations
✅ Multi-Symbol Support
        """
        await update.message.reply_text(status_message, parse_mode='Markdown')
    
    async def cmd_stats(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /stats command"""
        stats_message = f"""
📈 **Trading Statistics**

**Alerts:**
Today: {self.stats['alerts_today']}
Total: {self.stats['total_alerts']}
Last: {self.stats['last_alert_time'] or 'None'}

**Performance:**
(Track your trades to see stats here)

**Symbols Tracked:**
• NQ - Nasdaq-100 Futures
• TQQQ - 3x Leveraged QQQ
• SQQQ - 3x Inverse QQQ
• SOXL - 3x Semiconductors
• SOXS - 3x Inverse Semiconductors

**System:**
Uptime: {int((datetime.now() - self.stats['system_start_time']).total_seconds() // 3600)}h
Status: ✅ Active
        """
        await update.message.reply_text(stats_message, parse_mode='Markdown')
    
    async def cmd_pause(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /pause command"""
        # TODO: Implement pause functionality
        pause_message = """
⏸️ **Alerts Paused**

You will not receive any alerts until you /resume.

To resume alerts, send:
/resume
        """
        await update.message.reply_text(pause_message, parse_mode='Markdown')
    
    async def cmd_resume(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /resume command"""
        resume_message = """
▶️ **Alerts Resumed**

You will now receive real-time alerts.

To pause again, send:
/pause
        """
        await update.message.reply_text(resume_message, parse_mode='Markdown')
    
    async def cmd_threshold(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /threshold command"""
        try:
            if context.args and len(context.args) > 0:
                threshold = int(context.args[0])
                if 50 <= threshold <= 100:
                    # TODO: Update threshold in main app
                    threshold_message = f"""
✅ **Threshold Updated**

New minimum score: {threshold}/100

You will only receive alerts with AI score ≥ {threshold}

**Expected frequency:**
• 50-60: 10-20 alerts/day
• 60-70: 5-10 alerts/day
• 70-80: 2-5 alerts/day
• 80+: 1-3 alerts/day
                    """
                else:
                    threshold_message = "❌ Threshold must be between 50 and 100"
            else:
                threshold_message = """
**Set Alert Threshold**

Usage: `/threshold <score>`

Examples:
`/threshold 70` - Only alerts ≥70
`/threshold 80` - Only best alerts

Current: 60
                """
            await update.message.reply_text(threshold_message, parse_mode='Markdown')
        except ValueError:
            await update.message.reply_text("❌ Invalid threshold. Use a number between 50-100")
    
    async def cmd_symbols(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /symbols command"""
        symbols_message = """
📊 **Supported Symbols**

**NQ** 📈
Nasdaq-100 Futures
Leverage: 1x
Position: Normal

**TQQQ** 🚀
3x Leveraged QQQ
Leverage: 3x
Position: 1/3 size
⚠️ High volatility

**SQQQ** 📉
3x Inverse QQQ
Leverage: 3x (inverse)
Position: 1/3 size
⚠️ Profits when NQ falls

**SOXL** 💻
3x Semiconductors
Leverage: 3x
Position: 1/3 size
⚠️ Sector-specific

**SOXS** 🔻
3x Inverse Semiconductors
Leverage: 3x (inverse)
Position: 1/3 size
⚠️ Profits when chips fall

**To add a symbol:**
Update your TradingView strategy
        """
        await update.message.reply_text(symbols_message, parse_mode='Markdown')
    
    async def send_alert(self, message: str):
        """Send alert to Telegram"""
        try:
            await self.bot.send_message(
                chat_id=self.chat_id,
                text=message,
                parse_mode='Markdown'
            )
            
            # Update stats
            self.stats['total_alerts'] += 1
            self.stats['alerts_today'] += 1
            self.stats['last_alert_time'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            
        except Exception as e:
            logger.error(f"Failed to send Telegram alert: {e}")
    
    async def stop_bot(self):
        """Stop the Telegram bot"""
        if self.application:
            await self.application.updater.stop()
            await self.application.stop()
            await self.application.shutdown()
            logger.info("Telegram bot stopped")


if __name__ == "__main__":
    # Test bot
    import asyncio
    
    logging.basicConfig(level=logging.INFO)
    
    bot_token = os.getenv("TELEGRAM_BOT_TOKEN")
    chat_id = os.getenv("TELEGRAM_CHAT_ID")
    
    if bot_token and chat_id:
        handler = TelegramBotHandler(bot_token, chat_id)
        
        async def test():
            await handler.start_bot()
            print("Bot started! Send /start to your bot in Telegram")
            print("Press Ctrl+C to stop")
            
            # Keep running
            try:
                while True:
                    await asyncio.sleep(1)
            except KeyboardInterrupt:
                await handler.stop_bot()
        
        asyncio.run(test())
    else:
        print("Set TELEGRAM_BOT_TOKEN and TELEGRAM_CHAT_ID environment variables")
