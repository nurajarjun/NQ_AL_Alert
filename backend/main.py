from fastapi import FastAPI, Request, HTTPException
from telegram import Bot
import os
from dotenv import load_dotenv
import logging
from datetime import datetime
import json

# Import AI modules
from ai.context import ContextAnalyzer
from ai.analyzer import AIAnalyzer

# Import formatters
from utils.simple_formatter import SimpleAlertFormatter

# Import ML modules (optional)
try:
    from ml.ensemble import MLEnsemble
    from ml.xgboost_model import XGBoostPredictor
    from ml.feature_engineer import FeatureEngineer
    ML_AVAILABLE = True
except ImportError:
    ML_AVAILABLE = False
    logger = logging.getLogger(__name__)
    logger.warning("ML modules not available")

# Import Analysis modules
try:
    from analysis.multi_timeframe import MultiTimeframeAnalyzer
    MULTITF_AVAILABLE = True
except ImportError:
    MULTITF_AVAILABLE = False
    logger = logging.getLogger(__name__)
    logger.warning("Multi-timeframe analysis not available")

try:
    from analysis.economic_news import EconomicCalendar, NewsAnalyzer
    ECONOMIC_AVAILABLE = True
except ImportError:
    ECONOMIC_AVAILABLE = False
    logger = logging.getLogger(__name__)
    logger.warning("Economic calendar not available")

try:
    from analysis.market_correlations import MarketCorrelations
    CORRELATIONS_AVAILABLE = True
except ImportError:
    CORRELATIONS_AVAILABLE = False
    logger = logging.getLogger(__name__)
    logger.warning("Market correlations not available")

# Import Signal Generator (Autonomous Trading)
try:
    from analysis.signal_generator import SignalGenerator, AutonomousTrader
    AUTONOMOUS_AVAILABLE = True
except ImportError:
    AUTONOMOUS_AVAILABLE = False
    logger = logging.getLogger(__name__)
    logger.warning("Autonomous signal generator not available")

# Import Telegram Bot (Two-way communication)
try:
    from utils.telegram_bot import TelegramBotHandler
    TELEGRAM_BOT_AVAILABLE = True
except ImportError:
    TELEGRAM_BOT_AVAILABLE = False
    logger = logging.getLogger(__name__)
    logger.warning("Telegram bot handler not available")

# Import Database modules
try:
    from database.pattern_db import PatternDatabase
    PATTERN_DB_AVAILABLE = True
except ImportError:
    PATTERN_DB_AVAILABLE = False
    logger = logging.getLogger(__name__)
    logger.warning("Pattern database not available")

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
    version="3.0.0"  # Simplified version
)

# Initialize Telegram Bot
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

if not TELEGRAM_BOT_TOKEN or not TELEGRAM_CHAT_ID:
    logger.error("Telegram credentials not found!")
else:
    bot = Bot(token=TELEGRAM_BOT_TOKEN)
    logger.info("✅ Telegram bot initialized")

# Initialize AI components
context_analyzer = ContextAnalyzer()
ai_analyzer = AIAnalyzer()
alert_formatter = SimpleAlertFormatter()
logger.info("✅ AI components initialized")

# Initialize ML components (optional)
ml_ensemble = None
if ML_AVAILABLE:
    try:
        ml_ensemble = MLEnsemble()
        xgboost_model = XGBoostPredictor()
        feature_engineer = FeatureEngineer()
        
        if xgboost_model.is_trained:
            ml_ensemble.add_model('xgboost', xgboost_model, weight=1.0)
            logger.info("✅ XGBoost model loaded")
        else:
            logger.info("⚠️ XGBoost not trained - AI only mode")
            ml_ensemble = None
    except Exception as e:
        logger.warning(f"ML initialization failed: {e}")
        ml_ensemble = None
else:
    logger.info("ℹ️ Running in AI-only mode (ML not available)")

# Initialize Multi-Timeframe Analyzer
mtf_analyzer = None
if MULTITF_AVAILABLE:
    try:
        mtf_analyzer = MultiTimeframeAnalyzer()
        logger.info("✅ Multi-timeframe analyzer initialized")
    except Exception as e:
        logger.warning(f"Multi-timeframe init failed: {e}")
        mtf_analyzer = None

# Initialize Pattern Database
pattern_db = None
if PATTERN_DB_AVAILABLE:
    try:
        pattern_db = PatternDatabase()
        logger.info("✅ Pattern database initialized")
    except Exception as e:
        logger.warning(f"Pattern database init failed: {e}")
        pattern_db = None

# Initialize Economic Calendar
economic_calendar = None
if ECONOMIC_AVAILABLE:
    try:
        economic_calendar = EconomicCalendar()
        logger.info("✅ Economic calendar initialized")
    except Exception as e:
        logger.warning(f"Economic calendar init failed: {e}")
        economic_calendar = None

# Initialize Market Correlations
market_correlations = None
if CORRELATIONS_AVAILABLE:
    try:
        market_correlations = MarketCorrelations()
        logger.info("✅ Market correlations initialized")
    except Exception as e:
        logger.warning(f"Market correlations init failed: {e}")
        market_correlations = None

# Initialize Autonomous Signal Generator
autonomous_trader = None
if AUTONOMOUS_AVAILABLE:
    try:
        signal_generator = SignalGenerator()
        autonomous_trader = AutonomousTrader(signal_generator, check_interval=300)
        logger.info("✅ Autonomous signal generator initialized")
    except Exception as e:
        logger.warning(f"Autonomous trader init failed: {e}")
        autonomous_trader = None

# Initialize Telegram Bot (Two-way communication)
telegram_bot = None
if TELEGRAM_BOT_AVAILABLE and TELEGRAM_BOT_TOKEN and TELEGRAM_CHAT_ID:
    try:
        telegram_bot = TelegramBotHandler(TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID)
        logger.info("✅ Telegram bot handler initialized")
    except Exception as e:
        logger.warning(f"Telegram bot init failed: {e}")
        telegram_bot = None

# Store alerts
alerts_history = []

# Background task flag
autonomous_enabled = os.getenv("AUTONOMOUS_MODE", "false").lower() == "true"

# Startup event
@app.on_event("startup")
async def startup_event():
    """Start background tasks on startup"""
    logger.info("🚀 Starting NQ AI Alert System...")
    
    # Start Telegram bot
    if telegram_bot:
        try:
            await telegram_bot.start_bot()
            logger.info("✅ Telegram bot started - Two-way communication active")
        except Exception as e:
            logger.error(f"Failed to start Telegram bot: {e}")
    
    # Start autonomous trading if enabled
    if autonomous_enabled and autonomous_trader:
        logger.info("✅ Autonomous mode ENABLED - Will generate signals automatically")
    else:
        logger.info("ℹ️ Autonomous mode disabled - Waiting for TradingView signals")
    
    logger.info("🎯 System ready!")

# Shutdown event
@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown"""
    logger.info("Shutting down...")
    
    if telegram_bot:
        try:
            await telegram_bot.stop_bot()
        except Exception as e:
            logger.error(f"Error stopping Telegram bot: {e}")

@app.get("/")
async def root():
    """Health check endpoint"""
    return {
        "status": "running",
        "service": "NQ AI Tracker",
        "version": "3.0.0",
        "autonomous_mode": autonomous_enabled,
        "telegram_bot": telegram_bot is not None,
        "timestamp": datetime.now().isoformat()
    }

@app.get("/test")
async def test_telegram():
    """Test Telegram bot connection"""
    try:
        message = f"""
✅ TEST ALERT - System Check

🤖 NQ AI Tracker
Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
Status: All systems operational
Connection: Telegram ✓

Your NQ AI Tracker is ready! 🚀
        """
        
        await bot.send_message(
            chat_id=TELEGRAM_CHAT_ID,
            text=message
        )
        
        logger.info("Test alert sent successfully")
        return {
            "status": "success",
            "message": "Test alert sent to Telegram"
        }
    
    except Exception as e:
        logger.error(f"Error sending test alert: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/webhook/tradingview")
async def receive_tradingview_alert(request: Request):
    """
    Receive alerts from TradingView with AI-powered analysis
    
    Expected JSON format:
    {
        "direction": "LONG" or "SHORT",
        "entry": 16850.5,
        "stop": 16820.0,
        "target1": 16920.0,
        "target2": 16980.0,
        "rsi": 58.5,
        "atr": 45.2,
        "volume_ratio": 1.4
    }
    """
    try:
        # Parse incoming data
        data = await request.json()
        logger.info(f"Received TradingView alert: {json.dumps(data)}")
        
        # Extract data
        symbol = data.get('symbol', 'NQ').upper()  # Get symbol, default to NQ
        direction = data.get('direction', 'N/A')
        entry = data.get('entry', 0)
        stop = data.get('stop', 0)
        target1 = data.get('target1', 0)
        target2 = data.get('target2', 0)
        rsi = data.get('rsi', 0)
        atr = data.get('atr', 0)
        volume_ratio = data.get('volume_ratio', 1.0)
        
        logger.info(f"Processing {symbol} {direction} signal at {entry}")
        
        # Calculate risk/reward
        if direction == "LONG":
            risk = entry - stop
            reward1 = target1 - entry
            reward2 = target2 - entry
        else:
            risk = stop - entry
            reward1 = entry - target1
            reward2 = entry - target2
        
        rr1 = round(reward1 / risk, 2) if risk > 0 else 0
        rr2 = round(reward2 / risk, 2) if risk > 0 else 0
        
        # ===== AI ANALYSIS STARTS HERE =====
        logger.info("Starting AI analysis...")
        
        # Step 1: Get market context
        context = await context_analyzer.get_market_context(symbol)  # Use symbol
        logger.info(f"Market context retrieved: {context.get('sentiment', {}).get('fear_greed_text', 'Unknown')}")
        
        # Step 2: AI analysis of the trade
        signal_data = {
            'symbol': symbol,  # Add symbol to signal data
            'direction': direction,
            'entry': entry,
            'stop': stop,
            'target1': target1,
            'target2': target2,
            'rsi': rsi,
            'atr': atr,
            'volume_ratio': volume_ratio
        }
        
        ai_analysis = await ai_analyzer.analyze_trade(signal_data, context)
        logger.info(f"AI Analysis: {ai_analysis['recommendation']} (Score: {ai_analysis['score']})")
        
        # ===== ML PREDICTION =====
        ml_prediction = None
        combined_score = ai_analysis['score']  # Default to AI score
        
        if ml_ensemble and ml_ensemble.enabled_models:
            try:
                logger.info("Getting ML prediction...")
                from ml.ml_helpers import signal_to_ml_features
                
                ml_features = signal_to_ml_features(signal_data, feature_engineer)
                ml_prediction = ml_ensemble.predict(ml_features)
                logger.info(f"ML: {ml_prediction['combined_direction']} ({ml_prediction['combined_score']})")
                
                # Combine AI and ML (50/50)
                combined_score = int(
                    (ai_analysis['score'] * 0.5) +
                    (ml_prediction['combined_score'] * 0.5)
                )
                
            except Exception as e:
                logger.error(f"ML failed: {e}")
                ml_prediction = None
        
        # ===== MULTI-TIMEFRAME ANALYSIS =====
        mtf_result = None
        mtf_boost = 0
        
        if mtf_analyzer:
            try:
                logger.info("Analyzing multiple timeframes...")
                mtf_result = mtf_analyzer.analyze()
                mtf_boost = mtf_result['score_boost']
                
                # Add boost to combined score
                combined_score += mtf_boost
                logger.info(f"Multi-TF: {mtf_result['alignment']['direction']} "
                           f"({mtf_result['alignment']['percentage']:.0f}% aligned, +{mtf_boost} boost)")
                
            except Exception as e:
                logger.error(f"Multi-timeframe failed: {e}")
                mtf_result = None
        
        # ===== PATTERN MATCHING =====
        similar_patterns = None
        pattern_stats = None
        
        if pattern_db:
            try:
                logger.info("Finding similar patterns...")
                similar_patterns = pattern_db.find_similar_patterns(signal_data, top_k=15)
                
                if similar_patterns:
                    pattern_stats = pattern_db.calculate_win_rate(similar_patterns)
                    logger.info(f"Patterns: {pattern_stats['total_trades']} found, "
                               f"{pattern_stats['win_rate']*100:.0f}% win rate")
                
            except Exception as e:
                logger.error(f"Pattern matching failed: {e}")
                similar_patterns = None
        
        # ===== ECONOMIC CALENDAR =====
        economic_events = None
        economic_risk = 'NORMAL'
        
        if economic_calendar:
            try:
                logger.info("Checking economic events...")
                economic_events = economic_calendar.get_todays_events()
                economic_risk = economic_events['risk_level']
                
                if economic_events['high_impact'] or economic_events['tech_earnings']:
                    logger.info(f"Economic risk: {economic_risk} - {economic_events['trading_recommendation']}")
                
            except Exception as e:
                logger.error(f"Economic calendar failed: {e}")
                economic_events = None
        
        # ===== MARKET CORRELATIONS =====
        correlations = None
        correlation_boost = 0
        
        if market_correlations:
            try:
                logger.info("Analyzing market correlations...")
                correlations = market_correlations.analyze_correlations()
                correlation_boost = correlations['signals']['score_adjustment']
                
                # Add correlation boost to score
                combined_score += correlation_boost
                
                logger.info(f"Correlations: {correlations['overall']['direction']} "
                           f"({correlations['overall']['bullish_pct']:.0f}%, {correlation_boost:+d} boost)")
                
            except Exception as e:
                logger.error(f"Correlations failed: {e}")
                correlations = None
        
        # Update AI analysis with final combined score
        ai_analysis_with_ml = ai_analysis.copy()
        ai_analysis_with_ml['score'] = combined_score
        
        should_send = ai_analyzer.should_send_alert(ai_analysis_with_ml)
        
        if not should_send:
            logger.info(f"Alert filtered out (Score: {combined_score})")
            return {
                "status": "filtered",
                "message": "Low quality setup",
                "score": combined_score
            }
        
        # ===== FORMAT SIMPLE ALERT =====
        message = alert_formatter.format_trade_alert(
            signal_data=signal_data,
            ai_analysis=ai_analysis,
            ml_prediction=ml_prediction
        )
        
        # Send to Telegram
        await bot.send_message(
            chat_id=TELEGRAM_CHAT_ID,
            text=message
        )
        
        # Store in pattern database
        if pattern_db:
            try:
                trade_data = signal_data.copy()
                trade_data['ai_score'] = combined_score
                trade_id = pattern_db.store_trade(trade_data)
                logger.info(f"Trade stored in pattern DB: ID {trade_id}")
            except Exception as e:
                logger.warning(f"Failed to store in pattern DB: {e}")
        
        # Store simple history
        alert_record = {
            "timestamp": datetime.now().isoformat(),
            "direction": direction,
            "entry": entry,
            "stop": stop,
            "target1": target1,
            "score": combined_score,
            "ai_score": ai_analysis['score'],
            "ml_score": ml_prediction['combined_score'] if ml_prediction else None,
            "mtf_boost": mtf_boost,
            "pattern_win_rate": pattern_stats['win_rate'] if pattern_stats else None
        }
        alerts_history.append(alert_record)
        
        # Enhanced logging
        log_msg = f"✅ Alert sent: {direction} at {entry}, Score: {combined_score}"
        if mtf_boost > 0:
            log_msg += f" (+{mtf_boost} MTF)"
        if pattern_stats:
            log_msg += f", Pattern: {pattern_stats['win_rate']*100:.0f}% WR"
        logger.info(log_msg)
        
        return {
            "status": "success",
            "message": "Enhanced alert sent",
            "score": combined_score,
            "mtf_boost": mtf_boost,
            "pattern_win_rate": pattern_stats['win_rate'] if pattern_stats else None
        }
    
    except Exception as e:
        logger.error(f"Error processing alert: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/alerts/history")
async def get_alerts_history(limit: int = 10):
    """Get recent alerts history"""
    return {
        "total_alerts": len(alerts_history),
        "recent_alerts": alerts_history[-limit:]
    }

@app.get("/alerts/stats")
async def get_alerts_stats():
    """Get alert statistics"""
    if not alerts_history:
        return {"message": "No alerts yet"}
    
    total = len(alerts_history)
    long_count = sum(1 for a in alerts_history if a['direction'] == 'LONG')
    short_count = sum(1 for a in alerts_history if a['direction'] == 'SHORT')
    high_quality = sum(1 for a in alerts_history if a.get('ai_score', 0) >= 80)
    
    avg_score = sum(a.get('ai_score', 0) for a in alerts_history) / total if total > 0 else 0
    
    return {
        "total_alerts": total,
        "long_alerts": long_count,
        "short_alerts": short_count,
        "high_quality_alerts": high_quality,
        "high_quality_percentage": round((high_quality / total) * 100, 1) if total > 0 else 0,
        "average_ai_score": round(avg_score, 1)
    }

if __name__ == "__main__":
    import uvicorn
    
    logger.info("Starting NQ AI Alert System...")
    logger.info(f"Telegram Bot Token: {'✓ Configured' if TELEGRAM_BOT_TOKEN else '✗ Missing'}")
    logger.info(f"Telegram Chat ID: {'✓ Configured' if TELEGRAM_CHAT_ID else '✗ Missing'}")
    
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        log_level="info"
    )
