
import sys
import os
import asyncio
import logging
import pandas as pd
from datetime import datetime

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("TEST_PIPELINE")

# Add root to path
sys.path.append(os.getcwd())

# Mock Telegram Bot to avoid initialization errors if needed, 
# but main.py imports it conditionally. 
# We need to import main's callback.

try:
    from backend.main import mobile_app_prediction_callback, data_collector
except ImportError:
    sys.path.append(os.path.join(os.getcwd(), 'backend'))
    from main import mobile_app_prediction_callback, data_collector

async def run_test():
    print("\n--- STARTING PIPELINE TEST ---")
    print(f"Time: {datetime.now()}")
    
    # Check if data collector is working and what data it has
    if os.path.exists("backend/ml/data/nq_historical.pkl"):
        print("⚠️ CACHE FILE EXISTS (Potential for stale data)")
        try:
            cache_time = datetime.fromtimestamp(os.path.getmtime("backend/ml/data/nq_historical.pkl"))
            print(f"Cache Timestamp: {cache_time}")
        except:
            pass
    
    print("\nRunning mobile_app_prediction_callback('NQ')...")
    result = await mobile_app_prediction_callback("NQ")
    
    if isinstance(result, str):
        print(f"❌ FAILED: Callback returned string error: {result}")
        return

    print("\n--- RESULT ANALYSIS ---")
    
    # 1. Check Trend
    trend = result.get('trend')
    print(f"Trend Key: {trend}")
    if trend == 'N/A' or trend is None:
        print("❌ FAIL: Trend is N/A")
    else:
        print("✅ PASS: Trend is populated")

    # 2. Check EMA 21
    ema21 = result.get('ema_21')
    print(f"EMA 21 Key: {ema21}")
    if ema21 == 'N/A' or ema21 is None:
        print("❌ FAIL: EMA 21 is N/A")
    else:
        print("✅ PASS: EMA 21 is populated")

    # 3. Check Data Freshness (Proxy via Price)
    price = result.get('price')
    print(f"Price: {price}")
    
    # 4. Check Trade Setup
    trade_setup = result.get('trade_setup')
    print(f"Trade Setup Type: {type(trade_setup)}")
    print(f"Trade Setup Content: {trade_setup}")
    
    # 5. Check Confluence
    print(f"Confluence: {result.get('confluence_text')}")
    
    print("\n--- TEST COMPLETE ---")

if __name__ == "__main__":
    loop = asyncio.new_event_loop()
    loop.run_until_complete(run_test())
