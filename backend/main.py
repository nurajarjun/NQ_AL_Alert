from fastapi import FastAPI, Request, HTTPException
from telegram import Bot
import os
from dotenv import load_dotenv
import logging
from datetime import datetime
import json
import sys
import asyncio

# Import AI modules
from ai.context import ContextAnalyzer
from ai.analyzer import AIAnalyzer

# Import formatters
from utils.simple_formatter import SimpleAlertFormatter

# Import ML modules
try:
    from ml.ensemble import MLEnsemble
    from ml.xgboost_model import XGBoostPredictor
    from ml.feature_engineer import FeatureEngineer
    from ml.data_collector import HistoricalDataCollector
    ML_AVAILABLE = True
    
    # Try to import transformer (optional - requires torch)
    try:
        from ml.transformer_predictor import TransformerPredictor
        TRANSFORMER_AVAILABLE = True
    except ImportError as e:
        print(f"Transformer not available (torch missing): {e}")
        TRANSFORMER_AVAILABLE = False
        TransformerPredictor = None
        
except ImportError as e:
    # logger has not been defined yet, so print
    print(f"ML Import Warning: {e}") 
    ML_AVAILABLE = False
    TRANSFORMER_AVAILABLE = False
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
    from analysis.economic_news import EconomicCalendar as OldEconomicCalendar, NewsAnalyzer
    ECONOMIC_AVAILABLE = True
except ImportError:
    ECONOMIC_AVAILABLE = False
    logger = logging.getLogger(__name__)
    logger.warning("Economic calendar not available")

# Phase 14: Enhanced Calendars
try:
    from utils.economic_calendar import EconomicCalendar
    from utils.earnings_calendar import EarningsCalendar
    PHASE14_AVAILABLE = True
except ImportError as e:
    PHASE14_AVAILABLE = False
    logger = logging.getLogger(__name__)
    logger.warning(f"Phase 14 calendars not available: {e}")

try:
    from analysis.trade_calculator import TradeCalculator
    TRADE_CALC_AVAILABLE = True
except ImportError:
    TRADE_CALC_AVAILABLE = False
    logger = logging.getLogger(__name__)
    logger.warning("Trade calculator not available")

try:
    from analysis.market_session import MarketSessionAnalyzer
    MARKET_SESSION_AVAILABLE = True
except ImportError:
    MARKET_SESSION_AVAILABLE = False
    logger = logging.getLogger(__name__)
    logger.warning("Market session analyzer not available")

try:
    from analysis.market_correlations import MarketCorrelations
    CORRELATIONS_AVAILABLE = True
except ImportError:
    CORRELATIONS_AVAILABLE = False
    logger = logging.getLogger(__name__)
    logger.warning("Market correlations not available")

# Import Geopolitics Analyzer
try:
    from analysis.geopolitics import GeopoliticsAnalyzer
    GEOPOLITICS_AVAILABLE = True
except ImportError:
    GEOPOLITICS_AVAILABLE = False
    logger = logging.getLogger(__name__)
    logger.warning("Geopolitics analyzer not available")

# Import Global Market Manager (Phase 2)
try:
    from ml.global_trading import GlobalMarketManager
    GLOBAL_TRADING_AVAILABLE = True
except ImportError:
    GLOBAL_TRADING_AVAILABLE = False
    logger.warning("Global Market Manager not available")

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

try:
    from analysis.trade_manager import TradeManager
    TRADE_MANAGER_AVAILABLE = True
except ImportError:
    TRADE_MANAGER_AVAILABLE = False
    logger = logging.getLogger(__name__)
    logger.warning("Trade Manager not available")

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
trade_manager = TradeManager() if TRADE_MANAGER_AVAILABLE else None
logger.info("✅ AI components initialized")

# Initialize ML components (optional)
# ===== MULTI-ASSET CONFIGURATION =====
SYMBOLS = ["NQ", "ES", "TQQQ", "SQQQ", "SOXL", "SOXS"]  # Supported symbols
DEFAULT_SYMBOL = "NQ"  # Primary symbol for /check command

# ===== ML INITIALIZATION (Multi-Asset) =====
ml_ensemble = None
ml_models = {}  # Dict to store models per symbol: {"NQ": xgb_model, "ES": xgb_model, ...}

if ML_AVAILABLE:
    try:
        # LAZY LOADING: Don't load models at startup, load on first use
        # This saves ~1.5GB of memory during container initialization
        logger.info("✅ ML System initialized (lazy loading enabled)")
        logger.info(f"   Available symbols: {', '.join(SYMBOLS)}")
        logger.info("   Models will load on first prediction request")
        
        # Initialize feature engineer and data collector (lightweight)
        feature_engineer = FeatureEngineer()
        data_collector = HistoricalDataCollector()
        
        # Transformer setup (also lazy)
        if TRANSFORMER_AVAILABLE:
            logger.info("ℹ️ Transformer available (will load on first NQ prediction)")
        else:
            logger.info("ℹ️ Transformer not available (torch not installed)")
            
    except Exception as e:
        logger.warning(f"ML initialization failed: {e}")
        ml_models = {}
else:
    logger.info("ℹ️ Running in AI-only mode (ML not available)")

# Lazy Loading Helper Function
def get_ml_model(symbol):
    """Load ML model on-demand (lazy loading to save startup memory)"""
    if not ML_AVAILABLE:
        return None
    
    # Check if already loaded
    if symbol in ml_models:
        return ml_models[symbol]
    
    # Load on first use
    try:
        logger.info(f"📦 Loading XGBoost model for {symbol} (first use)...")
        xgboost_model = XGBoostPredictor(symbol=symbol)
        if xgboost_model.is_trained:
            ml_models[symbol] = xgboost_model
            logger.info(f"✅ {symbol} model loaded successfully")
            return xgboost_model
        else:
            logger.warning(f"⚠️ {symbol} model not trained")
            return None
    except Exception as e:
        logger.error(f"❌ Failed to load {symbol} model: {e}")
        return None


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

# Initialize Geopolitics Analyzer
geopolitics_analyzer = None
if GEOPOLITICS_AVAILABLE:
    try:
        geopolitics_analyzer = GeopoliticsAnalyzer()
        logger.info("✅ Geopolitics analyzer initialized")
    except Exception as e:
        logger.warning(f"Geopolitics analyzer init failed: {e}")
        geopolitics_analyzer = None

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

# Initialize Evening Scalper (Asian Session)
evening_scalper = None
try:
    from analysis.evening_scalper import EveningScalper
    evening_scalper = EveningScalper()
    logger.info("✅ Evening Scalper initialized (8PM-10PM ET)")
except ImportError:
    logger.warning("Evening Scalper not available")
    evening_scalper = None

# Initialize Telegram Bot (Two-way communication)
telegram_bot = None
if TELEGRAM_BOT_AVAILABLE and TELEGRAM_BOT_TOKEN and TELEGRAM_CHAT_ID:
    try:
        telegram_bot = TelegramBotHandler(TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID)
        logger.info("✅ Telegram bot handler initialized")
    except Exception as e:
        logger.warning(f"Telegram bot init failed: {e}")
        telegram_bot = None

# Initialize Analysis Modules
trade_calculator = TradeCalculator() if TRADE_CALC_AVAILABLE else None
economic_calendar_old = OldEconomicCalendar() if ECONOMIC_AVAILABLE else None
news_analyzer = NewsAnalyzer(api_key=os.getenv("NEWS_API_KEY")) if ECONOMIC_AVAILABLE else None
session_analyzer = MarketSessionAnalyzer() if MARKET_SESSION_AVAILABLE else None

# Phase 14: Initialize Enhanced Calendars
economic_calendar = EconomicCalendar() if PHASE14_AVAILABLE else None
earnings_calendar = EarningsCalendar() if PHASE14_AVAILABLE else None

# Phase 2: Global Trading
global_manager = GlobalMarketManager() if GLOBAL_TRADING_AVAILABLE else None
if global_manager:
    logger.info("✅ Global Market Manager initialized")

# Initialize Plan Feeder (Substack Integration)
plan_feeder = None
try:
    from knowledge.plan_feeder import PlanFeeder
    plan_feeder = PlanFeeder()
    logger.info("✅ Plan feeder initialized (Substack)")
except ImportError:
    logger.warning("Plan feeder not available")

# Start Daily Scheduler (Background Thread)
try:
    import threading
    from scheduler.daily_tasks import run_scheduler
    
    scheduler_thread = threading.Thread(target=run_scheduler, daemon=True, name="DailyScheduler")
    scheduler_thread.start()
    logger.info("✅ Daily scheduler started (6 AM plan fetch, Sunday retrain)")
except Exception as e:
    logger.warning(f"Daily scheduler not started: {e}")

# Start Auto Alert Generator (Background Thread)
try:
    from alerts.auto_alert_generator import AutoAlertGenerator
    import asyncio
    
    def run_auto_alerts():
        """Run auto alerts in background thread"""
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        if telegram_bot:
            generator = AutoAlertGenerator(telegram_bot)
            loop.run_until_complete(generator.run_continuous_scan())
    
    alert_thread = threading.Thread(target=run_auto_alerts, daemon=True, name="AutoAlerts")
    alert_thread.start()
    logger.info("✅ Auto alert generator started (scans every 15 min)")
except Exception as e:
    logger.warning(f"Auto alert generator not started: {e}")

# Callback for on-demand analysis
async def mobile_app_prediction_callback(symbol="NQ"):
    """Run instant prediction for Telegram /check command"""
    try:
        # Check if ML components are available
        if not ML_AVAILABLE:
            return """❌ ML Components Not Available

The /check command requires ML modules which are not currently loaded.

Possible reasons:
• Missing dependencies (install requirements.txt)
• ML models not trained yet

What you can do:
• Wait for TradingView alerts (those work without ML)
• Check server logs for initialization errors

System is still monitoring for TradingView signals!"""
        
        # Check if required components are initialized
        if 'data_collector' not in globals() or 'feature_engineer' not in globals():
            return """❌ Data components not initialized

Required ML components are not available.

TradingView alerts will still work normally!"""
        
        # SPECIAL: Check Global Session Status
        if symbol == "GLOBAL":
            if global_manager:
                import pytz
                from datetime import datetime
                et_now = datetime.now(pytz.timezone('US/Eastern'))
                
                # Get rich details
                details = global_manager.get_session_details()
                
                # Format message
                details['current_time_et'] = et_now.strftime('%H:%M ET')
                details['message'] = "Global Trading System Online 🌍"
                
                return {
                    'symbol': 'GLOBAL',
                    'session_info': details,
                    'direction': 'NEUTRAL', # Placeholder
                    'prediction': f"Current Session: {details['session']}",
                    'confidence': 100
                }
            else:
                 return "Global Manager not initialized."

        # 1. Fetch latest data (Smart Cache: Delta update)
        logger.info(f"Fetching data for {symbol}...")
        df = data_collector.download_nq_data(symbol=symbol)
        
        if df.empty:
            return f"❌ No data found for {symbol}"

        # 2. Feature Engineering
        logger.info("Calculating features...")
        df_features = feature_engineer.calculate_all_features(df)
        last_row = df_features.iloc[-1]
        
        # 3. Prediction Logic (Transformer or Technical Analysis)
        # Check for 10 AM Reversal Window (using Global Manager if available)
        reversal_warning = ""
        is_reversal_window = False
        
        if global_manager:
            session_name = global_manager.get_current_session()
            if session_name == "NY_AM":
                # Check for 10-10:30 AM specific window
                import datetime
                import pytz
                ny_time = datetime.datetime.now(pytz.timezone('US/Eastern'))
                if ny_time.hour == 10 and ny_time.minute <= 30:
                     is_reversal_window = True
                     reversal_warning = "⚠️ **10 AM REVERSAL WATCH** ⚠️\n(Volatility High - Expect Fakeouts)"
        else:
            # Fallback Legacy Logic
            import datetime
            import pytz
            ny_time = datetime.datetime.now(pytz.timezone('US/Eastern'))
            if ny_time.hour == 10 and ny_time.minute >= 0 and ny_time.minute <= 30:
                is_reversal_window = True
                reversal_warning = "⚠️ **10 AM REVERSAL WATCH** ⚠️\n(Volatility High - Expect Fakeouts)"

        # --- Confluence Scoring (NQ Logic) ---
        confluence_score = 0
        confluence_factors = []
        
        # 1. Trend (21 EMA) - Institutional NQ Level
        if 'EMA_21' in last_row:
             if last_row['Close'] > last_row['EMA_21']:
                 confluence_score += 1
                 confluence_factors.append("Trend (Above 21 EMA)")
             else:
                 confluence_factors.append("Trend (Below 21 EMA)") # For Short
        
        # 2. Momentum (RSI)
        rsi_val = last_row.get('RSI', 50)
        if rsi_val > 55:
            confluence_score += 1
            confluence_factors.append("Momentum (Bullish)")
        elif rsi_val < 45:
             confluence_factors.append("Momentum (Bearish)")

        # 3. Volume / Price Action (Simple Body Size)
        # NQ likes strong candles
        if last_row.get('Body_Size', 0) > 0.0005: 
             confluence_score += 1
             confluence_factors.append("Strong Candle")

        confluence_text = f"✅ Confluence: {' + '.join(confluence_factors)}"

        # USE XGBOOST MODEL (with institutional features) - LAZY LOADED
        xgb_model = get_ml_model(symbol)
        if xgb_model is not None:
            logger.info(f"Using XGBoost model for {symbol}...")
            try:
                # Prepare features for prediction
                X = df_features.tail(1).drop(['Target'], axis=1, errors='ignore')
                
                # Get prediction
                prediction = xgb_model.model.predict(X)[0]
                probabilities = xgb_model.model.predict_proba(X)[0]
                
                # Map prediction to direction
                direction_map = {0: "SIDEWAYS", 1: "DOWN", 2: "UP"}
                direction = direction_map.get(prediction, "NEUTRAL")
                
                # Confidence is the probability of the predicted class
                confidence = probabilities[prediction] * 100
                
                # Score for compatibility
                if direction == "UP":
                    score = 50 + (confidence / 2)
                elif direction == "DOWN":
                    score = 50 - (confidence / 2)
                else:
                    score = 50
                
                
                # Check for Transformer (Deep Learning)
                transformer_result = None
                if 'transformer_model' in globals() and transformer_model is not None and symbol == "NQ":
                     try:
                         # Transformer expects seq_len sequence
                         transformer_result = transformer_model.predict(df_features) # predict handles scaling
                         logger.info(f"Transformer Prediction: {transformer_result}")
                     except Exception as e:
                         logger.error(f"Transformer prediction error: {e}")

                # === ENSEMBLE LOGIC (The "Brain") ===
                # Weighted Average: XGBoost (Stable) + Transformer (Deep Patterns)
                
                if transformer_result and transformer_result['model'] != "None":
                    # Parse XGBoost confidence
                    xgb_conf = confidence
                    xgb_dir = direction
                    
                    # Parse Transformer confidence
                    trans_conf = transformer_result.get('confidence', 0) * 100
                    trans_dir = transformer_result.get('direction', 'NEUTRAL')
                    
                    # Convert directions to numeric signal (Long=1, Short=-1, Neutral=0)
                    dir_map_num = {"UP": 1, "LONG": 1, "DOWN": -1, "SHORT": -1, "NEUTRAL": 0, "SIDEWAYS": 0}
                    xgb_sig = dir_map_num.get(xgb_dir, 0)
                    trans_sig = dir_map_num.get(trans_dir, 0)
                    
                    # Weighted Score
                    # XGBoost: 60% (Proven Stability)
                    # Transformer: 40% (New "RightChoice" Deep Learning)
                    final_score = (xgb_sig * xgb_conf * 0.6) + (trans_sig * trans_conf * 0.4)
                    
                    # Determine Final Direction
                    if final_score > 15: # Threshold
                        final_dir = "LONG"
                    elif final_score < -15:
                        final_dir = "SHORT"
                    else:
                        final_dir = "NEUTRAL"
                        
                    # Final Confidence is absolute avg magnitude
                    final_conf = abs(final_score)
                    
                    direction = final_dir
                    confidence = final_conf
                    method = f"ENSEMBLE: XGBoost(60%) + Transformer(40%)"
                    prediction_text = f"🤖 AI Fusion: {direction} ({confidence:.1f}% Conf)\n[XGB: {xgb_dir} | Trans: {trans_dir}]"
                    
                else:
                    # XGBoost Only
                    method = f"XGBoost ML (49 features + Institutional)"
                    prediction_text = f"ML Prediction: {direction} with {confidence:.2f}% confidence."
                
            except Exception as e:
                logger.error(f"XGBoost prediction failed: {e}")
                import traceback
                traceback.print_exc()
                # Fallback to technical analysis
                symbol = "FALLBACK"
        
        if 'ml_models' not in globals() or symbol not in ml_models:
            # USE TECHNICAL ANALYSIS (Improved Logic for other symbols or fallback)
            logger.info("Using Technical Analysis...")
            rsi = last_row.get('RSI', 50)
            sma_10 = last_row.get('SMA_10', 0)
            sma_20 = last_row.get('SMA_20', 0)
            sma_50 = last_row.get('SMA_50', 0)
            close = last_row['Close']
            open_price = last_row['Open']
            
            # Improved Scoring Logic
            score = 50
            
            # RSI Analysis (more sensitive)
            if rsi > 60: score += 15  # Bullish momentum
            elif rsi > 50: score += 8  # Slight bullish
            elif rsi < 40: score -= 15  # Bearish momentum
            elif rsi < 50: score -= 8  # Slight bearish
            
            if rsi > 70: score -= 10  # Overbought (reduce bullish)
            if rsi < 30: score += 10  # Oversold (reduce bearish)
            
            # Price vs Moving Averages
            if close > sma_10: score += 8
            else: score -= 8
            
            if close > sma_20: score += 6
            else: score -= 6
            
            if sma_50 > 0:
                if close > sma_50: score += 4
                else: score -= 4
            
            # Trend Strength (MA alignment)
            if sma_10 > sma_20: score += 8
            else: score -= 8
            
            # Current candle direction
            if close > open_price: score += 5  # Bullish candle
            else: score -= 5  # Bearish candle
            
            score = max(0, min(100, score)) # Clamp 0-100
            method = "Technical Analysis"
            
            # Derive direction/confidence (narrower NEUTRAL range)
            # OPTIMIZED V2: Mean Reversion (Backtest Proven +765 pts PnL)
            # We fade the high scores (Overbought) and buy the low scores (Oversold)
            
            from utils.config import ConfigManager
            config = ConfigManager()
            threshold = config.get('alert_threshold', 70)
            
            if score >= threshold: direction = "SHORT"
            elif score <= (100 - threshold): direction = "LONG"
            else: direction = "NEUTRAL"
            
            # Confidence calculation
            confidence = abs(score - 50) * 2
            prediction_text = f"TA Prediction: {direction} with {confidence:.2f}% confidence."
            
            # === PHASE 14: ENHANCED FILTERS ===
            if direction in ["LONG", "SHORT"]:
                # Filter 1: Multi-Timeframe RSI Confirmation
                if ML_AVAILABLE and feature_engineer:
                    try:
                        rsi_4h_series = feature_engineer.calculate_4h_rsi(df_features)
                        rsi_4h = rsi_4h_series.iloc[-1] if len(rsi_4h_series) > 0 else None
                        rsi_1h = last_row.get('RSI')
                        
                        if rsi_4h is not None and rsi_1h is not None:
                            mtf_aligned = feature_engineer.check_mtf_rsi_alignment(rsi_1h, rsi_4h, direction)
                            if not mtf_aligned:
                                logger.info(f"MTF Filter: 1H RSI={rsi_1h:.1f}, 4H RSI={rsi_4h:.1f} - Not aligned")
                                direction = "NEUTRAL"
                                prediction_text += " [Filtered: Multi-timeframe not aligned]"
                    except Exception as e:
                        logger.warning(f"MTF RSI check failed: {e}")
                
                # Filter 2: Economic Calendar (FOMC, CPI, NFP)
                if PHASE14_AVAILABLE and economic_calendar and direction != "NEUTRAL":
                    try:
                        is_safe, event_name = await economic_calendar.is_safe_to_trade(datetime.now())
                        if not is_safe:
                            logger.info(f"Economic Filter: Skipping trade - {event_name} in 30 min")
                            direction = "NEUTRAL"
                            prediction_text += f" [Filtered: {event_name} event]"
                    except Exception as e:
                        logger.warning(f"Economic calendar check failed: {e}")
                
                # Filter 3: Earnings Week (Top NQ Holdings)
                if PHASE14_AVAILABLE and earnings_calendar and direction != "NEUTRAL":
                    try:
                        is_earnings, symbol_reporting = await earnings_calendar.is_earnings_week(datetime.now())
                        if is_earnings:
                            logger.info(f"Earnings Filter: Skipping trade - {symbol_reporting} reports this week")
                            direction = "NEUTRAL"
                            prediction_text += f" [Filtered: {symbol_reporting} earnings]"
                    except Exception as e:
                        logger.warning(f"Earnings calendar check failed: {e}")
                
                # Filter 4: Geopolitical Risk (War, Conflict, Crisis)
                if GEOPOLITICS_AVAILABLE and geopolitics_analyzer and direction != "NEUTRAL":
                    try:
                        # Get news headlines from context
                        if context_analyzer:
                            context_data = await context_analyzer.get_context()
                            if context_data and 'news' in context_data:
                                headlines = [item.get('title', '') for item in context_data['news']]
                                geo_risk = geopolitics_analyzer.analyze_risk(headlines)
                                
                                # Block trades on CRITICAL or ELEVATED risk
                                if geo_risk['level'] in ['CRITICAL', 'ELEVATED']:
                                    logger.info(f"Geopolitical Filter: {geo_risk['level']} risk detected - {geo_risk['triggers']}")
                                    direction = "NEUTRAL"
                                    prediction_text += f" [Filtered: {geo_risk['level']} geopolitical risk]"
                    except Exception as e:
                        logger.warning(f"Geopolitical risk check failed: {e}")

        # 4. Calculate Trade Setup (Entry, Stops, Targets, Levels)
        target_levels = {} # Renamed from trade_setup to target_levels
        if trade_calculator:
            try:
                target_levels_dict = trade_calculator.calculate_trade_setup(
                    df_features, 
                    direction, 
                    confidence / 100
                )
                
                # Add to Trade Manager for monitoring
                if trade_manager and target_levels_dict.get('entry', 0) > 0:
                     target_levels_dict['confluence'] = confluence_text # Add confluence to track
                     trade_manager.add_trade(target_levels_dict)
                
                # Format for display as a string
                # Actually, let's keep target_levels as dict and use a new variable for string
                formatted_setup = trade_calculator.format_trade_setup(target_levels_dict)
                # But telegram_bot expects 'trade_setup' key to be either dict or string...
                # and I modified main.py earlier to overwrite it.
                # Let's pass the string as 'trade_setup' for now as planned in Phase 2 fix.
                target_levels = formatted_setup
                
            except Exception as e:
                logger.warning(f"Trade calculator failed: {e}")
        
        # 5. Get Economic Context
        economic_context = {}
        news_sentiment = {}
        session_info = {}
        
        if economic_calendar:
            try:
                economic_context = await economic_calendar.get_events_for_date(datetime.now().date())
            except Exception as e:
                logger.warning(f"Economic calendar failed: {e}")
        
        if news_analyzer:
            try:
                news_data = news_analyzer.get_market_news()
                news_sentiment = news_data.get('sentiment', {})
            except Exception as e:
                logger.warning(f"News analyzer failed: {e}")
        
        if global_manager:
            try:
                import pytz
                from datetime import datetime
                # returns: {'session': '...', 'quality': '...', 'volume_expectation': '...', 'recommendation': '...'}
                session_details = global_manager.get_session_details()
                
                et_now = datetime.now(pytz.timezone('US/Eastern'))
                
                # Merge into final structure
                session_info = session_details
                session_info['current_time_et'] = et_now.strftime('%H:%M ET')
                session_info['status'] = "OPEN"
                session_info['message'] = session_details.get('recommendation', "Global Trading Active")
                
            except Exception as e:
                 logger.warning(f"Global manager session check failed: {e}")
                 session_info = {}
        elif session_analyzer:
            try:
                session_info = session_analyzer.get_current_session()
            except Exception as e:
                logger.warning(f"Session analyzer failed: {e}")

        # 6. EXPERT CONTEXT (Added to fix missing bias)
        expert_bias = "NEUTRAL"
        try:
             sys.path.insert(0, 'backend')
             from analysis.expert_input import ExpertContext
             expert = ExpertContext()
             expert.refresh() # Force refresh
             expert_bias = expert.data.get('bias', 'NEUTRAL').upper()
        except Exception as e:
             logger.warning(f"Failed to load Expert Context: {e}")

        # Construct comprehensive response
        return {
            'symbol': symbol if symbol != "FALLBACK" else "NQ",
            'direction': direction,
            'confidence': confidence,
            'score': score,
            'method': method,
            'price': last_row['Close'],
            'rsi': last_row.get('RSI', 'N/A'),
            'sma_10': last_row.get('SMA_10', 'N/A'),
            'sma_20': last_row.get('SMA_20', 'N/A'),
            'ema_21': last_row.get('EMA_21', 'N/A'), # Added EMA 21
            'prediction': prediction_text,
            'trade_setup': target_levels,
            'confluence_text': confluence_text, # Pass confluence
            'reversal_warning': reversal_warning, # Pass reversal warning
            'session_info': session_info,
            'expert_bias': expert_bias, # Added Expert Bias
            'trend': 'UP ↗️' if 'EMA_21' in last_row and last_row['Close'] > last_row['EMA_21'] else 'DOWN ↘️' if 'EMA_21' in last_row else 'N/A'
        }
    except Exception as e:
        logger.error(f"Callback prediction failed: {e}")
        import traceback
        traceback.print_exc()
        return f"Error analyzing {symbol}: {str(e)}"

# Setup Telegram with callback
if TELEGRAM_BOT_AVAILABLE and os.getenv("TELEGRAM_BOT_TOKEN"):
    try:
        telegram_bot = TelegramBotHandler(
            os.getenv("TELEGRAM_BOT_TOKEN"), 
            os.getenv("TELEGRAM_CHAT_ID"),
            on_predict_callback=mobile_app_prediction_callback
        )
    except Exception as e:
        logger.warning(f"Telegram bot init failed: {e}")
        telegram_bot = None

# Store alerts
alerts_history = []

# Background task flag
from utils.config import ConfigManager
config_mgr = ConfigManager()
autonomous_enabled = config_mgr.get('autonomous_enabled', False) or (os.getenv("AUTONOMOUS_MODE", "false").lower() == "true")

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
            
            # Send startup note
            await telegram_bot.send_alert("""
📝 **System Updated! Here are your new commands:**

**🔎 /check** -> Check NQ (AI Model 🧠)
**🔎 /check ES** -> Check S&P 500 (Techs 📊)

**❓ /help** -> See full command list anytime.
            """)
        except Exception as e:
            logger.error(f"Failed to start Telegram bot: {e}")
    
    # Start autonomous trading if enabled
    if autonomous_enabled and autonomous_trader:
        logger.info("✅ Autonomous mode ENABLED - Will generate signals automatically")
        asyncio.create_task(run_autonomous_loop())
    else:
        logger.info("ℹ️ Autonomous mode disabled - Waiting for TradingView signals")
    
    logger.info("🎯 System ready!")

async def run_autonomous_loop():
    """Background loop for autonomous trading"""
    logger.info("🔄 Starting Autonomous Trading Loop...")
    
    while True:
        try:
            if autonomous_trader:
                signal = autonomous_trader.get_signal_if_ready()
                
                if signal:
                    symbol = signal.get('symbol', 'NQ')
                    direction = signal.get('direction', 'NEUTRAL')
                    logger.info(f"🚨 AUTONOMOUS SIGNAL: {symbol} {direction}")
                    
                    # Send to Telegram
                    if telegram_bot:
                        # Use Premium Formatting (Standardized)
                        try:
                             # Enrich signal relative to what main.py has
                             if 'score' not in signal: signal['score'] = 50 
                             if 'confidence' not in signal:
                                  # Estimate confidence if missing
                                  if 'probability' in signal:
                                      signal['confidence'] = signal['probability'] * 100
                                  else:
                                      signal['confidence'] = 0
                                      
                             msg = telegram_bot.format_alert(signal)
                             await telegram_bot.send_alert(msg)
                             
                        except Exception as fmt_err:
                             logger.error(f"Formatting error: {fmt_err}")
                             # Fallback
                             await telegram_bot.send_alert(f"🚨 SIGNAL: {symbol} {direction} @ {signal.get('entry', 0)}")
                        
                        # Add to alerts history (simplified)
                        alerts_history.append({
                            "timestamp": datetime.now().isoformat(),
                            "symbol": symbol,
                            "direction": direction,
                            "price": signal.get('entry'),
                            "source": "autonomous"
                        })

            
            # --- EVENING SCALPER CHECK (8 PM - 10 PM ET) ---
            if evening_scalper:
                # Check scanning
                try:
                    evening_signals = await evening_scalper.scan_market()
                    
                    if evening_signals:
                        logger.info(f"🌙 Evening Scalper found {len(evening_signals)} signals")
                        for sig in evening_signals:
                            # Only send if confident and in session
                            if sig.get('in_session', False):
                                msg = f"🌙 **EVENING SCALP** | {sig['pair']}\n\n"
                                msg += f"📊 **{sig['strategy']}**\n"
                                msg += f"Signal: **{sig['signal']}** | Conf: {sig['confidence']}\n\n"
                                
                                # Entry and Levels
                                msg += f"💰 **Trade Setup:**\n"
                                msg += f"Entry: {sig['entry']:.2f}\n"
                                msg += f"Stop: {sig['stop']:.2f}\n"
                                msg += f"Target 1: {sig['target1']:.2f} (R/R: {sig['rr_ratio1']}:1)\n"
                                msg += f"Target 2: {sig['target2']:.2f} (R/R: {sig['rr_ratio2']}:1)\n\n"
                                
                                # Risk/Reward in Dollars
                                msg += f"💵 **Risk/Reward:**\n"
                                msg += f"Risk: ${sig['risk_dollars']:.0f}\n"
                                msg += f"Reward 1: ${sig['reward1_dollars']:.0f}\n"
                                msg += f"Reward 2: ${sig['reward2_dollars']:.0f}\n\n"
                                
                                # Technical Stats
                                msg += f"📈 **Stats:** ADX={sig['adx']:.1f} | RSI={sig['rsi']:.1f}"
                                
                                if telegram_bot:
                                    await telegram_bot.send_alert(msg)
                except Exception as es_err:
                     logger.error(f"Evening scalper error: {es_err}")

            # Sleep for a bit to prevent tight loop
            await asyncio.sleep(60) # Check every minute (AutonomourTrader handles its own interval logic too)
            
        except Exception as e:
            logger.error(f"Error in autonomous loop: {e}")
            await asyncio.sleep(60) # Sleep on error

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
        "version": "3.1.0",
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
        
        # ===== ML PREDICTION (Transformer + XGBoost) =====
        ml_prediction = None
        combined_score = ai_analysis['score']  # Default to AI score
        
        if ML_AVAILABLE:
            try:
                logger.info("Fetching latest market data for Deep Learning...")
                # Get latest data for Transformer (needs history)
                recent_data = data_collector.download_nq_data()
                
                # 1. Transformer Prediction (The Architect)
                dl_prediction = transformer_model.predict(recent_data)
                logger.info(f"🧠 Deep Learning: {dl_prediction['direction']} ({dl_prediction['score']})")
                
                # 2. XGBoost Prediction (The Scientist feature check)
                xgb_score = 50 # Default neutral
                try:
                    from ml.ml_helpers import signal_to_ml_features
                    ml_features = signal_to_ml_features(signal_data, feature_engineer)
                    
                    if ml_ensemble and ml_ensemble.enabled_models:
                        xgb_prediction = ml_ensemble.predict(ml_features)
                        xgb_score = xgb_prediction['combined_score']
                        logger.info(f"🌲 XGBoost: {xgb_prediction['combined_direction']} ({xgb_score})")
                    else:
                        logger.info("🌲 XGBoost: Skipped (Not enabled)")
                        
                except Exception as e:
                    logger.warning(f"XGBoost step failed: {e}")
                
                # Combine Scores
                # Weighted: 60% Deep Learning, 20% XGBoost, 20% AI Context
                deep_learning_score = dl_prediction['score']
                ai_score = ai_analysis['score']
                
                combined_score = int(
                    (deep_learning_score * 0.6) +
                    (xgb_score * 0.2) +
                    (ai_score * 0.2)
                )
                
                # Update ml_prediction object for the alert
                ml_prediction = dl_prediction
                ml_prediction['model'] = f"Transformer + XGBoost"
                
            except Exception as e:
                logger.error(f"ML Processing failed completely: {e}")
                # Fallback to AI score if ML dies entirely
                combined_score = ai_analysis['score']
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

# Background Task for Trade Monitoring
import asyncio

async def trade_monitor_loop():
    """Background loop to monitor active trades"""
    logger.info("🚀 Trade Monitor Loop Started")
    while True:
        try:
            if trade_manager and trade_manager.active_trades:
                # Get latest price (lightweight)
                # We reuse data collector if available, or yfinance directly
                import yfinance as yf
                ticker = yf.Ticker("NQ=F")
                current_price = ticker.fast_info['last_price']
                
                if current_price:
                    updates = trade_manager.check_updates(current_price)
                    
                    for msg in updates:
                        await bot.send_message(
                            chat_id=TELEGRAM_CHAT_ID,
                            text=msg
                        )
                        logger.info(f"Sent trade update: {msg}")
            
            await asyncio.sleep(60) # Check every minute
            
        except Exception as e:
            logger.error(f"Error in trade monitor: {e}")
            await asyncio.sleep(60)

@app.on_event("startup")
async def startup_event():
    asyncio.create_task(trade_monitor_loop())

if __name__ == "__main__":
    import uvicorn
    
    logger.info("Starting NQ AI Alert System...")
    logger.info(f"Telegram Bot Token: {'✓ Configured' if TELEGRAM_BOT_TOKEN else '✗ Missing'}")
    logger.info(f"Telegram Chat ID: {'✓ Configured' if TELEGRAM_CHAT_ID else '✗ Missing'}")
    
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8001,
        log_level="info"
    )
