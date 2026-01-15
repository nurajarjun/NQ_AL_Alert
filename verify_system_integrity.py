import sys
import os
import asyncio
import pandas as pd

# Setup path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

# Mock env vars
os.environ["TELEGRAM_BOT_TOKEN"] = "mock"
os.environ["TELEGRAM_CHAT_ID"] = "mock"

# Import components
from ml.global_trading import GlobalMarketManager
from ml.data_collector import HistoricalDataCollector
from ml.feature_engineer import FeatureEngineer
from ml.xgboost_model import XGBoostPredictor

async def verify_system():
    print("="*60)
    print("🔍 FINAL SYSTEM INTEGRITY CHECK")
    print("="*60)
    
    # 1. Verify Global Trading Logic
    print("\n[1] Checking Global Market Manager...")
    try:
        manager = GlobalMarketManager()
        session = manager.get_current_session()
        print(f"   ✅ Manager Initialized")
        print(f"   🕒 Current Session: {session}")
    except Exception as e:
        print(f"   ❌ Global Manager Failed: {e}")

    # 2. Verify Data & Models for ALL Symbols
    print("\n[2] Verifying Data Pipeline & Model Inference...")
    
    symbols = ["NQ", "ES", "TQQQ", "SQQQ", "SOXL", "SOXS"]
    collector = HistoricalDataCollector()
    engineer = FeatureEngineer()
    
    results = {}
    
    for symbol in symbols:
        print(f"\n   👉 Checking {symbol}...")
        try:
            # A. Data
            df = collector.download_nq_data(symbol=symbol)
            if df.empty:
                print(f"      ❌ Data Download Failed (Empty)")
                results[symbol] = "Data Fail"
                continue
            print(f"      ✅ Data Downloaded ({len(df)} candles)")
            
            # B. Features
            df_features = engineer.calculate_all_features(df)
            if df_features.empty:
                print(f"      ❌ Feature Calculation Failed")
                results[symbol] = "Feature Fail"
                continue
            # Check for critical features
            if 'RSI' not in df_features.columns:
                 print(f"      ❌ Missing Critical Feature (RSI)")
                 
            print(f"      ✅ Features Calculated ({df_features.shape[1]} features)")
            
            # C. Model Prediction
            model = XGBoostPredictor(symbol=symbol)
            if not model.is_trained:
                print(f"      ⚠️ Model Not Trained")
                results[symbol] = "Model Missing"
                continue
                
            # Predict on last row
            last_row_features = engineer.get_feature_matrix(df_features.tail(1))
            prediction = model.predict(last_row_features)
            
            direction = prediction['direction']
            conf = prediction['confidence']
            print(f"      ✅ Prediction: {direction} ({conf:.1%})")
            results[symbol] = "PASS"
            
        except Exception as e:
            print(f"      ❌ FAILED: {e}")
            results[symbol] = f"Error: {e}"
            import traceback
            traceback.print_exc()

    # Summary
    print("\n" + "="*60)
    print("📋 VERIFICATION SUMMARY")
    print("="*60)
    all_pass = True
    for sym, status in results.items():
        icon = "✅" if status == "PASS" else "❌"
        print(f"{icon} {sym}: {status}")
        if status != "PASS": all_pass = False
        
    if all_pass:
        print("\n🚀 ALL SYSTEMS NOMINAL. READY FOR LIVE TRADING.")
    else:
        print("\n⚠️ SOME SYSTEMS FAILED. REVIEW LOGS.")

if __name__ == "__main__":
    asyncio.run(verify_system())
