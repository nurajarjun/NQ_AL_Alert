"""
Simple test to verify ML models work with institutional features
"""
import sys
sys.path.insert(0, 'backend')

from ml.xgboost_model import XGBoostPredictor
from ml.feature_engineer import FeatureEngineer, PANDAS_TA_AVAILABLE
from ml.data_collector import HistoricalDataCollector

print("="*60)
print("NQ AI Alert System - ML Verification Test")
print("="*60)

# Check pandas-ta
print(f"\n1. pandas-ta available: {PANDAS_TA_AVAILABLE}")

# Load models
print("\n2. Loading ML Models...")
symbols = ['NQ', 'ES']
for sym in symbols:
    try:
        model = XGBoostPredictor(sym)
        print(f"   {sym}: trained={model.is_trained}, features={len(model.feature_names) if model.feature_names else 0}")
    except Exception as e:
        print(f"   {sym}: ERROR - {e}")

# Test feature engineering (if pandas-ta available)
if PANDAS_TA_AVAILABLE:
    print("\n3. Testing Feature Engineering...")
    try:
        collector = HistoricalDataCollector()
        df = collector.download_nq_data(symbol='NQ')
        print(f"   Data fetched: {len(df)} rows")
        
        engineer = FeatureEngineer()
        df_features = engineer.calculate_all_features(df)
        print(f"   Features calculated: {len(engineer.feature_names)} features")
        print(f"   Sample features: {engineer.feature_names[:5]}")
        
        # Check for institutional features
        institutional = ['EMA_20_60m', 'FVG_Bullish', 'Distance_from_EMA60m']
        found = [f for f in institutional if f in engineer.feature_names]
        print(f"   Institutional features found: {found}")
        
    except Exception as e:
        print(f"   ERROR: {e}")
        import traceback
        traceback.print_exc()
else:
    print("\n3. Skipping feature engineering test (pandas-ta not available)")

print("\n" + "="*60)
print("Test Complete!")
print("="*60)
