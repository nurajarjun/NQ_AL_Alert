"""
Send Test Alert with XGBoost Prediction
"""
import sys
import os
import asyncio
sys.path.insert(0, 'backend')

from utils.telegram_bot import TelegramBotHandler
from ml.xgboost_model import XGBoostPredictor
from ml.feature_engineer import FeatureEngineer
from ml.data_collector import HistoricalDataCollector

async def send_test_alert():
    # Initialize components
    print("Initializing components...")
    bot = TelegramBotHandler(
        os.getenv('TELEGRAM_BOT_TOKEN'),
        os.getenv('TELEGRAM_CHAT_ID')
    )
    
    # Load NQ model
    print("Loading NQ model...")
    nq_model = XGBoostPredictor('NQ')
    print(f"Model loaded: {nq_model.is_trained}")
    print(f"Model path: {nq_model.model_path}")
    
    if not nq_model.is_trained:
        await bot.send_alert("❌ NQ model not loaded!")
        return
    
    # Get latest data
    print("Fetching data...")
    collector = HistoricalDataCollector()
    df = collector.download_nq_data(symbol='NQ')
    
    # Engineer features
    print("Engineering features...")
    engineer = FeatureEngineer()
    df_features = engineer.calculate_all_features(df)
    
    # Make prediction
    print("Making prediction...")
    X = df_features.tail(1).drop(['Target'], axis=1, errors='ignore')
    
    prediction = nq_model.model.predict(X)[0]
    probabilities = nq_model.model.predict_proba(X)[0]
    
    direction_map = {0: "SIDEWAYS", 1: "DOWN", 2: "UP"}
    direction = direction_map.get(prediction, "NEUTRAL")
    confidence = probabilities[prediction] * 100
    
    # Send alert
    message = f"""🧠 **NQ Test Alert - XGBoost**

✅ **Model Loaded Successfully!**

📊 **Prediction:**
Direction: {direction}
Confidence: {confidence:.1f}%
Method: XGBoost ML (49 features + Institutional)

🎯 **Institutional Features Active:**
• 60m EMA (Trend Anchor)
• Fair Value Gaps (FVG)
• Opening Drive Patterns
• Gap Analysis

💪 **Model Info:**
Features: {len(nq_model.feature_names) if nq_model.feature_names else 'N/A'}
Trained: {nq_model.is_trained}

System is LIVE with Discord strategies!"""
    
    print("Sending alert...")
    await bot.send_alert(message)
    print("✅ Alert sent!")

asyncio.run(send_test_alert())
