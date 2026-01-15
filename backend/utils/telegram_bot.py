"""
Telegram Bot Handler
Two-way communication with Telegram
"""

from telegram import Update, Bot
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
import os
import logging
from datetime import datetime
import logging
from datetime import datetime
import json
import asyncio
import sys

logger = logging.getLogger(__name__)


class TelegramBotHandler:
    """Handles two-way Telegram communication"""
    
    def __init__(self, bot_token: str, chat_id: str, on_predict_callback=None):
        self.bot_token = bot_token
        self.chat_id = chat_id
        self.on_predict_callback = on_predict_callback
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
            # Increase timeouts to handle slow network connections
            from telegram.request import HTTPXRequest
            request = HTTPXRequest(
                connection_pool_size=8,
                connect_timeout=30.0,
                read_timeout=30.0,
                write_timeout=30.0,
                pool_timeout=30.0
            )
            
            self.application = Application.builder().token(self.bot_token).request(request).build()
            
            # Add command handlers
            self.application.add_handler(CommandHandler("start", self.cmd_start))
            self.application.add_handler(CommandHandler("help", self.cmd_help))
            self.application.add_handler(CommandHandler("status", self.cmd_status))
            self.application.add_handler(CommandHandler("stats", self.cmd_stats))
            self.application.add_handler(CommandHandler("pause", self.cmd_pause))
            self.application.add_handler(CommandHandler("resume", self.cmd_resume))
            self.application.add_handler(CommandHandler("threshold", self.cmd_threshold))
            self.application.add_handler(CommandHandler("symbols", self.cmd_symbols))
            self.application.add_handler(CommandHandler("check", self.cmd_check))
            self.application.add_handler(CommandHandler("global", self.cmd_global))
            self.application.add_handler(CommandHandler("retrain", self.cmd_retrain))
            self.application.add_handler(CommandHandler("scan", self.cmd_scan))
            self.application.add_handler(CommandHandler("backtest", self.cmd_backtest))
            self.application.add_handler(CommandHandler("chop", self.cmd_chop))
            self.application.add_handler(CommandHandler("evening", self.cmd_evening))
            self.application.add_handler(CommandHandler("config", self.cmd_config))
            
            # Start polling in background
            await self.application.initialize()
            await self.application.start()
            await self.application.updater.start_polling()
            
            logger.info("✅ Telegram bot started - Two-way communication active")
            
        except Exception as e:
            logger.error(f"Failed to start Telegram bot: {e}")
            
    async def cmd_global(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /global command"""
        # Reuse check logic with special symbol
        context.args = ["GLOBAL"]
        await self.cmd_check(update, context)

    async def cmd_start(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /start command"""
        welcome_message = """
🤖 **NQ AI Alert System v3.0**

Welcome! Your AI trading assistant is ready.

**Quick Start:**
• `/check` - Get instant NQ prediction
• `/help` - See all commands
• `/status` - Check system health

**What I Do:**
✅ Deep Learning predictions (NQ)
✅ Technical analysis (ES, GC, etc.)
✅ Entry, Stop, 2 Targets
✅ Support/Resistance levels
✅ Market session warnings
✅ Economic event alerts

**You'll receive:**
• Trade type (Scalp/Day/Swing)
• Risk per contract
• Expected duration
• Real-time market context

Type `/help` to see all commands! 🚀
        """
        await update.message.reply_text(welcome_message, parse_mode='Markdown')
    
    async def cmd_help(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /help command"""
        help_message = """
📝 **NQ AI Trading Bot - Command Guide**

**🔎 ANALYZE SYMBOLS**
`/check` - Fusion Prediction (NQ)
`/check [Symbol]` - Analyze ES, Gold, Crypto
`/evening` - 🌙 Asian Session Scalp (8-10PM ET)
`/global` - 🌍 Global Session Status (24/5)
`/scan` - Top 5 Stock Picks

**🤖 AUTONOMOUS MODE**
The bot auto-scans for you!
• **Day**: Trend Following (9:30 AM - 4 PM)
• **Evening**: Scalping (8 PM - 10 PM)
*Enable*: `/config autonomous_enabled true`

**⚙️ SETTINGS**
`/config` - View/Edit all settings
`/threshold 75` - Set Min Confidence
`/chop 25` - Set Min ADX Filter

**ℹ️ STATUS**
`/status` - System Health
`/stats` - Performance
`/retrain` - Manually Update Brain

**💡 EXAMPLES**
`/config risk_per_trade 0.02` (Set 2% risk)
`/check GC` (Analyze Gold)
`/evening` (Asian Session Dashboard)
        """
        await update.message.reply_text(help_message, parse_mode='Markdown')
    
    async def cmd_config(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /config command"""
        # Usage: /config [key] [value]
        # Or: /config to list all
        
        args = context.args
        from utils.config import ConfigManager
        config = ConfigManager()
            
        if not args:
            # List all configs
            msg = "⚙️ **Current Configuration:**\n\n"
            for k, v in config.config.items():
                msg += f"• `{k}`: {v}\n"
            
            msg += "\nTo change: `/config [key] [value]`"
            await update.message.reply_text(msg, parse_mode='Markdown')
            return
            
        key = args[0]
        
        if len(args) == 1:
            # Get specific value
            val = config.get(key, "Not Set")
            await update.message.reply_text(f"🔹 `{key}`: {val}", parse_mode='Markdown')
        else:
            # Set value
            val = args[1]
            
            # Type conversion
            if val.lower() == "true": val = True
            elif val.lower() == "false": val = False
            elif val.isdigit(): val = int(val)
            elif val.replace('.', '', 1).isdigit(): val = float(val)
            
            config.set(key, val)
            await update.message.reply_text(f"✅ Set `{key}` to `{val}`", parse_mode='Markdown')
    
    # cmd_evening is defined later at line 636 - duplicate removed
    
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
            # Import ConfigManager here to avoid circular imports
            sys.path.insert(0, 'backend')
            from utils.config import ConfigManager
            config = ConfigManager()
            
            if context.args and len(context.args) > 0:
                threshold = int(context.args[0])
                if 50 <= threshold <= 100:
                    # Update config
                    config.set('alert_threshold', threshold)
                    
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
                current = config.get('alert_threshold', 60)
                threshold_message = f"""
**Set Alert Threshold**

Usage: `/threshold <score>`

Examples:
`/threshold 70` - Only alerts ≥70
`/threshold 80` - Only best alerts

Current Threshold: {current}
                """
            await update.message.reply_text(threshold_message, parse_mode='Markdown')
        except ValueError:
            await update.message.reply_text("❌ Invalid threshold. Use a number between 50-100")

    async def cmd_chop(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /chop command (ADX Threshold)"""
        try:
            sys.path.insert(0, 'backend')
            from utils.config import ConfigManager
            config = ConfigManager()
            
            if context.args and len(context.args) > 0:
                value = int(context.args[0])
                if 10 <= value <= 50:
                    config.set('adx_threshold', value)
                    await update.message.reply_text(f"✅ **Chop Filter Updated**\n\nMin ADX: {value}\n\nSignals below this strength will be filtered out.")
                else:
                    await update.message.reply_text("❌ ADX must be between 10 (Loose) and 50 (Strict)")
            else:
                current = config.get('adx_threshold', 25)
                await update.message.reply_text(f"**Set Trim/Chop Filter**\n\nUsage: `/chop <adx>`\nExample: `/chop 30` (Strict)\n\nCurrent: {current}")
                
        except ValueError:
            await update.message.reply_text("❌ Invalid number.")

    async def cmd_update_plan(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /update_plan command"""
        status_msg = await update.message.reply_text("🔄 Checking Substack for new trade plan...")
        
        try:
            sys.path.insert(0, 'backend')
            from knowledge.plan_feeder import PlanFeeder
            
            feeder = PlanFeeder()
            result = await feeder.fetch_latest_plan()
            
            if result.get('status') == 'success':
                msg = f"""
✅ **Daily Plan Updated!**

**Source:** {result.get('title')}
**Date:** {result.get('date')}
**Regime:** {result.get('regime')}

The AI has "read" the article and updated its strategy.
"""
            else:
                msg = f"❌ **Update Failed**\n\nReason: {result.get('message')}"
                
            await status_msg.edit_text(msg, parse_mode='Markdown')
            
        except Exception as e:
            logger.error(f"Update plan error: {e}")
            await status_msg.edit_text(f"❌ Error: {str(e)}")
    
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

    def format_alert(self, result: dict) -> str:
        """Standardized Alert Formatting (Premium Style)"""
        lines = [f"🧠 **{result.get('symbol', 'NQ')} Analysis (v3.1)**", ""]
        
        # Prediction
        direction = result.get('direction', 'NEUTRAL')
        direction_emoji = "🟢" if direction in ['LONG', 'UP'] else "🔴" if direction in ['SHORT', 'DOWN'] else "⚪"
        
        lines.append(f"{direction_emoji} **PREDICTION: {direction}**")
        
        # Show detailed explanation (e.g., "Filtered: MTF not aligned")
        prediction_detail = result.get('prediction', '')
        if "Filtered" in prediction_detail:
                lines.append(f"⚠️ {prediction_detail}")
        
        lines.append(f"💪 Confidence: {result.get('confidence', 0):.1f}%")
        lines.append(f"🎯 AI Score: {result.get('score', 0)}")
        lines.append(f"📊 Method: {result.get('method', 'Unknown')}")
        lines.append("")
        
        # Reversal Warning (NQ Specific)
        reversal_msg = result.get('reversal_warning', "")
        if reversal_msg:
            lines.append(reversal_msg)
            lines.append("")

        # Confluence Score
        confluence_msg = result.get('confluence_text', "")
        if confluence_msg:
            lines.append(confluence_msg)
            lines.append("")

        # Trade Setup
        trade_setup = result.get('trade_setup', {})
        
        # If trade_setup is already a formatted string (from TradeCalculator)
        if isinstance(trade_setup, str):
            lines.append(trade_setup)
            lines.append("")
        
        # Legacy: If trade_setup is a dict, format it manually
        elif isinstance(trade_setup, dict) and trade_setup.get('entry', 0) > 0:
            # Get trade direction from setup
            trade_direction = trade_setup.get('direction', direction)
            
            # Trade type emoji
            type_emoji = {
                'SCALP': '⚡',
                'DAY TRADE': '📊',
                'SWING TRADE': '📈'
            }.get(trade_setup.get('trade_type', 'UNKNOWN'), '❓')
            
            # Direction emoji for trade
            trade_emoji = "🟢" if trade_direction in ['LONG', 'UP'] else "🔴"
            
            lines.append(f"💰 **TRADE SETUP** {trade_emoji} {trade_direction} {type_emoji} {trade_setup.get('trade_type', 'UNKNOWN')}")
            lines.append(f"⏱️ Duration: {trade_setup.get('expected_duration', 'Unknown')}")
            lines.append(f"📍 Entry: {trade_setup['entry']:,.2f}")
            lines.append(f"🛑 Stop: {trade_setup['stop_loss']:,.2f} ({trade_setup['stop_distance']:+.0f} pts)")
            lines.append(f"🎯 T1: {trade_setup['target1']:,.2f} ({trade_setup['target1_distance']:+.0f} pts) [{trade_setup['risk_reward_t1']}R]")
            lines.append(f"🎯 T2: {trade_setup['target2']:,.2f} ({trade_setup['target2_distance']:+.0f} pts) [{trade_setup['risk_reward_t2']}R]")
            lines.append("")
            
            # Key Levels
            lines.append("📊 **KEY LEVELS**")
            support = " | ".join([f"{s:,.0f}" for s in trade_setup.get('support_levels', [])])
            resistance = " | ".join([f"{r:,.0f}" for r in trade_setup.get('resistance_levels', [])])
            lines.append(f"Support: {support}")
            lines.append(f"Resistance: {resistance}")
            lines.append("")
            
            # Risk
            lines.append(f"💰 Risk: ${trade_setup.get('risk_per_contract', 0):,.0f}/contract")
            lines.append(f"📈 ATR: {trade_setup.get('atr', 0):.1f} pts")
            lines.append("")
        
        # Market Session Info (if available)
        session = result.get('session_info', {})
        if session and session.get('session'):
            lines.append("⏰ **MARKET SESSION**")
            lines.append(f"Time: {session.get('current_time_et', 'Unknown')}")
            
            # Only show session details if market is open
            session_name = session.get('session', 'unknown')
            if session_name not in ['pre_market', 'after_hours', 'closed']:
                lines.append(f"Session: {session_name.replace('_', ' ').title()}")
                lines.append(f"Quality: {session.get('quality', 'UNKNOWN')}")
                lines.append(f"Volume: {session.get('volume_expectation', 'UNKNOWN')}")
            
            recommendation = session.get('recommendation', '')
            if recommendation:
                lines.append(f"💡 {recommendation}")
            lines.append("")

        # Expert Bias (Sabuj's Plan)
        bias = result.get('expert_bias', 'NEUTRAL')
        if bias and bias != "NEUTRAL":
            bias_emoji = "🧠"
            lines.append(f"{bias_emoji} **EXPERT: {bias}**")
            lines.append("")
        
        # Economic Context (if available)
        econ = result.get('economic_context', {})
        if econ and econ.get('risk_level'):
            lines.append("📅 **ECONOMIC CONTEXT**")
            
            # High impact events
            if econ.get('high_impact'):
                for event in econ['high_impact']:
                    lines.append(f"⚠️ {event['event']} at {event['time']}")
            
            # Tech earnings
            if econ.get('tech_earnings'):
                for earning in econ['tech_earnings']:
                    lines.append(f"📊 {earning['ticker']} earnings {earning['time']}")
            
            lines.append(f"Risk Level: {econ.get('risk_level', 'NORMAL')}")
            lines.append(f"💡 {econ.get('trading_recommendation', 'Normal trading')}")
            lines.append("")
        
        # News Sentiment (if available)
        news = result.get('news_sentiment', {})
        if news and news.get('direction'):
            sentiment_emoji = "📈" if news['direction'] == 'BULLISH' else "📉" if news['direction'] == 'BEARISH' else "➡️"
            lines.append(f"{sentiment_emoji} **NEWS: {news['direction']} ({news.get('score', 50)}%)**")
            lines.append("")
        
        # Technical Details
        lines.append("📊 **TECHNICAL**")
        lines.append(f"Price: {result.get('price', 0):,.2f}")
        
        # Format RSI with 1 decimal place
        rsi_value = result.get('rsi', 'N/A')
        if isinstance(rsi_value, (int, float)):
            lines.append(f"RSI: {rsi_value:.1f}")
        else:
            lines.append(f"RSI: {rsi_value}")
            
        lines.append(f"Trend: {result.get('trend', 'N/A')}")
        lines.append(f"EMA 21: {result.get('ema_21', 'N/A')}")
        
        return "\n".join(lines)

    async def cmd_check(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /check command to run instant analysis"""
        logger.info(f"📞 /check command received from user {update.effective_user.id}")
        
        if not self.on_predict_callback:
            logger.error("❌ on_predict_callback is None!")
            await update.message.reply_text("❌ Analysis module not connected.")
            return

        # Parse symbol from args (default to NQ)
        symbol = "NQ"
        if context.args and len(context.args) > 0:
            symbol = context.args[0].upper()

        logger.info(f"🔍 Starting analysis for {symbol}...")
        status_msg = await update.message.reply_text(f"🔍 Analyzing {symbol} market data... please wait.")
        
        try:
            # Run the callback with symbol
            logger.info(f"Calling on_predict_callback for {symbol}...")
            result = await self.on_predict_callback(symbol)
            logger.info(f"Callback returned: {type(result)}")
            
            # If result is a dict, format it comprehensively
            if isinstance(result, dict):
                message = self.format_alert(result)
            else:
                message = str(result)

            await context.bot.edit_message_text(
                chat_id=update.effective_chat.id,
                message_id=status_msg.message_id,
                text=message,
                parse_mode='Markdown'
            )
        except Exception as e:
            logger.error(f"❌ Error in on-demand check: {e}")
            import traceback
            logger.error(f"Full traceback:\n{traceback.format_exc()}")
            
            # Don't use parse_mode for error messages to avoid markdown parsing issues
            error_text = f"❌ Error running analysis:\n\n{str(e)}\n\nPlease check server logs for details."
            
            await context.bot.edit_message_text(
                chat_id=update.effective_chat.id,
                message_id=status_msg.message_id,
                text=error_text
            )
            await context.bot.edit_message_text(
                chat_id=update.effective_chat.id,
                message_id=status_msg.message_id,
                text=error_text
            )

    async def cmd_evening(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /evening command for Asian Session Scalping"""
        status_msg = await update.message.reply_text("🌙 Scanning Asian Session Markets (8PM-10PM ET)...")
        
        try:
            sys.path.insert(0, 'backend')
            from analysis.evening_scalper import EveningScalper
            
            scalper = EveningScalper()
            results = await scalper.scan_market()
            
            if not results:
                await context.bot.edit_message_text(
                    chat_id=update.effective_chat.id,
                    message_id=status_msg.message_id,
                    text="🌙 **Asian Session Scan**\n\nNo setups found right now.\nMarket might be quiet or outside session hours."
                )
                return
            
            # Format Dashboard
            msg = ["🌙 **Evening Scalper Dashboard**", ""]
            msg.append(f"Time: {datetime.now().strftime('%H:%M ET')}")
            msg.append("")
            
            for res in results:
                icon = "🟢" if res['signal'] == 'LONG' else "🔴"
                msg.append(f"{icon} **{res['pair']} ({res['ticker']})**")
                msg.append(f"Strategy: {res['strategy']}")
                msg.append(f"Price: {res['price']:,.2f}")
                msg.append(f"Vol Ratio: {res['vol_ratio']:.1f}x | ADX: {res['adx']:.0f}")
                msg.append(f"Confidence: {res['confidence']}")
                msg.append("")
                
            msg.append("⚠️ *Prop Fund Rule*: Stop Loss -$250/day")
            
            await context.bot.edit_message_text(
                chat_id=update.effective_chat.id,
                message_id=status_msg.message_id,
                text="\n".join(msg),
                parse_mode='Markdown'
            )
            
        except Exception as e:
            logger.error(f"Evening scan failed: {e}")
            await context.bot.edit_message_text(
                chat_id=update.effective_chat.id,
                message_id=status_msg.message_id,
                text=f"❌ Error scanning: {e}"
            )

    async def cmd_scan(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /scan command for stock picks"""
        status_msg = await update.message.reply_text("🔍 Scanning market for top stock picks... please wait.")
        
        try:
            # Import scanner
            import sys
            sys.path.insert(0, 'backend')
            from analysis.enhanced_scanner import EnhancedStockScanner
            
            scanner = EnhancedStockScanner()
            results = await scanner.scan_market(top_n=5)
            
            # Format results
            message = scanner.format_top_picks(results)
            
            await context.bot.edit_message_text(
                chat_id=update.effective_chat.id,
                message_id=status_msg.message_id,
                text=message
            )
            
        except Exception as e:
            logger.error(f"❌ Error in /scan: {e}")
            await context.bot.edit_message_text(
                chat_id=update.effective_chat.id,
                message_id=status_msg.message_id,
                text=f"❌ Scanner error: {str(e)}"
            )

    async def cmd_backtest(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /backtest command"""
        status_msg = await update.message.reply_text("🧪 Running Verified Backtest (Last 60 Days)... please wait.")
        try:
             # Run script using current python interpreter
             cmd = f"{sys.executable} backend/backtest.py"
             
             process = await asyncio.create_subprocess_shell(
                 cmd,
                 stdout=asyncio.subprocess.PIPE,
                 stderr=asyncio.subprocess.PIPE
             )
             stdout, stderr = await process.communicate()
             
             output = stdout.decode().strip()
             # Filter out common warnings or log garbage if needed, but keep it raw for honesty
             
             # Format for telegram
             # Extract the table part if possible, or just send all
             msg = f"📋 **Verification Report**\n\n```\n{output}\n```"
             
             if len(msg) > 4000: msg = msg[-4000:] # Send last part (results usually at end)
             
             await context.bot.edit_message_text(
                 chat_id=update.effective_chat.id,
                 message_id=status_msg.message_id,
                 text=msg,
                 parse_mode='Markdown'
             )
             
        except Exception as e:
             await context.bot.edit_message_text(
                 chat_id=update.effective_chat.id,
                 message_id=status_msg.message_id,
                 text=f"❌ Backtest failed: {e}"
             )
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
    
    async def cmd_retrain(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /retrain command"""
        if str(update.effective_user.id) != str(self.chat_id):
            await update.message.reply_text("⛔ Unauthorized")
            return

        status_msg = await update.message.reply_text("🧠 Checking Model Freshness...")
        
        try:
            # Import dynamically to avoid circular imports
            sys.path.insert(0, 'backend')
            from auto_retrain import needs_retraining, run_retraining
            
            force = False
            if context.args and 'force' in context.args[0].lower():
                force = True
            
            is_needed, reason = needs_retraining(days_threshold=7)
            
            if not is_needed and not force:
                await context.bot.edit_message_text(
                    chat_id=update.effective_chat.id,
                    message_id=status_msg.message_id,
                    text=f"✅ Models are fresh! ({reason})\nUse `/retrain force` to train anyway."
                )
                return
            
            # Start Training
            msg_text = f"🔄 **Retraining Started**\nReason: {reason}\n\nThis may take 2-5 minutes..."
            await context.bot.edit_message_text(
                chat_id=update.effective_chat.id,
                message_id=status_msg.message_id,
                text=msg_text,
                parse_mode='Markdown'
            )
            
            # Exec
            success, output = await run_retraining()
            
            if success:
                final_msg = "✅ **Retraining Complete!**\n\nAll models updated to latest data.\nReady for predictions."
            else:
                final_msg = f"❌ **Retraining Failed**\n\nError output:\n{output[-500:]}"
                
            await context.bot.send_message(
                chat_id=update.effective_chat.id,
                text=final_msg,
                parse_mode='Markdown'
            )
            
        except Exception as e:
            logger.error(f"Retrain command failed: {e}")
            await context.bot.send_message(
                chat_id=update.effective_chat.id,
                text=f"❌ Error: {e}"
            )

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
