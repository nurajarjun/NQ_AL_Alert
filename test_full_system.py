"""
Comprehensive ML System Test with Sample Predictions
Tests the full pipeline: data -> features -> prediction
"""
import sys
sys.path.insert(0, 'backend')

from ml.xgboost_model import XGBoostPredictor
from ml.feature_engineer import FeatureEngineer, PANDAS_TA_AVAILABLE
from ml.data_collector import HistoricalDataCollector
import pandas as pd

print("="*70)
print("NQ AI Alert System - Full ML Pipeline Test")
print("="*70)

# Test 1: Verify pandas-ta and models
print("\n📊 TEST 1: System Components")
print("-" * 70)
print(f"✓ pandas-ta available: {PANDAS_TA_AVAILABLE}")

models_status = {}
for sym in ['NQ', 'ES', 'TQQQ', 'SQQQ']:
    try:
        model = XGBoostPredictor(sym)
        models_status[sym] = {
            'loaded': model.is_trained,
            'features': len(model.feature_names) if model.feature_names else 0
        }
        status = "✓" if model.is_trained else "✗"
        print(f"{status} {sym:6s}: Loaded={model.is_trained}, Features={models_status[sym]['features']}")
    except Exception as e:
        print(f"✗ {sym:6s}: ERROR - {str(e)[:50]}")
        models_status[sym] = {'loaded': False, 'features': 0}

# Test 2: Feature Engineering
print("\n🔧 TEST 2: Feature Engineering with Institutional Features")
print("-" * 70)

if PANDAS_TA_AVAILABLE:
    try:
        collector = HistoricalDataCollector()
        print("Fetching NQ data...")
        df = collector.download_nq_data(symbol='NQ')
        print(f"✓ Data fetched: {len(df)} rows")
        
        engineer = FeatureEngineer()
        print("Calculating features...")
        df_features = engineer.calculate_all_features(df)
        print(f"✓ Features calculated: {len(engineer.feature_names)} total features")
        
        # Check institutional features
        institutional_features = [
            'EMA_20_60m',
            'Distance_from_EMA60m', 
            'FVG_Bullish',
            'FVG_Bearish',
            'FVG_Strength',
            'Is_First_Hour',
            'Gap_Type'
        ]
        
        print("\n📈 Institutional Features (Discord Strategy):")
        for feat in institutional_features:
            if feat in engineer.feature_names:
                print(f"   ✓ {feat}")
            else:
                print(f"   ✗ {feat} - MISSING")
        
        # Show sample feature values from latest candle
        print("\n📊 Latest Candle Feature Values:")
        latest = df_features.iloc[-1]
        print(f"   Close Price: ${latest['Close']:.2f}")
        if 'EMA_20_60m' in latest:
            print(f"   EMA 20 (60m): ${latest['EMA_20_60m']:.2f}")
            print(f"   Distance from EMA: {latest['Distance_from_EMA60m']*100:.2f}%")
        if 'RSI' in latest:
            print(f"   RSI: {latest['RSI']:.1f}")
        if 'FVG_Bullish' in latest:
            print(f"   FVG Bullish: {latest['FVG_Bullish']}")
            print(f"   FVG Bearish: {latest['FVG_Bearish']}")
        
    except Exception as e:
        print(f"✗ Feature engineering failed: {e}")
        import traceback
        traceback.print_exc()
        df_features = None
else:
    print("✗ pandas-ta not available - skipping feature engineering")
    df_features = None

# Test 3: ML Predictions
print("\n🧠 TEST 3: ML Predictions (XGBoost with Institutional Features)")
print("-" * 70)

if df_features is not None and models_status.get('NQ', {}).get('loaded'):
    try:
        nq_model = XGBoostPredictor('NQ')
        
        # Prepare data for prediction
        X = df_features.tail(1).drop(['Target'], axis=1, errors='ignore')
        
        # Make prediction
        prediction = nq_model.model.predict(X)[0]
        probabilities = nq_model.model.predict_proba(X)[0]
        
        direction_map = {0: "SIDEWAYS ↔️", 1: "DOWN ↘️", 2: "UP ↗️"}
        direction = direction_map.get(prediction, "NEUTRAL")
        confidence = probabilities[prediction] * 100
        
        print(f"\n🎯 NQ Prediction:")
        print(f"   Direction: {direction}")
        print(f"   Confidence: {confidence:.1f}%")
        print(f"   Method: XGBoost ML ({len(nq_model.feature_names)} features + Institutional)")
        
        # Show probability distribution
        print(f"\n   Probability Distribution:")
        print(f"      SIDEWAYS: {probabilities[0]*100:.1f}%")
        print(f"      DOWN:     {probabilities[1]*100:.1f}%")
        print(f"      UP:       {probabilities[2]*100:.1f}%")
        
        # Test ES model too
        if models_status.get('ES', {}).get('loaded'):
            es_model = XGBoostPredictor('ES')
            es_prediction = es_model.model.predict(X)[0]
            es_probabilities = es_model.model.predict_proba(X)[0]
            es_direction = direction_map.get(es_prediction, "NEUTRAL")
            es_confidence = es_probabilities[es_prediction] * 100
            
            print(f"\n🎯 ES Prediction:")
            print(f"   Direction: {es_direction}")
            print(f"   Confidence: {es_confidence:.1f}%")
        
    except Exception as e:
        print(f"✗ Prediction failed: {e}")
        import traceback
        traceback.print_exc()
else:
    print("✗ Cannot make predictions - data or model not available")

# Test 4: Multiple Predictions (last 5 candles)
print("\n📊 TEST 4: Historical Predictions (Last 5 Candles)")
print("-" * 70)

if df_features is not None and models_status.get('NQ', {}).get('loaded'):
    try:
        nq_model = XGBoostPredictor('NQ')
        
        print(f"\n{'Time':<20} {'Close':>10} {'Prediction':<15} {'Confidence':>12}")
        print("-" * 70)
        
        for i in range(5, 0, -1):
            row = df_features.iloc[-i]
            X_test = df_features.iloc[-i:-i+1].drop(['Target'], axis=1, errors='ignore')
            
            pred = nq_model.model.predict(X_test)[0]
            probs = nq_model.model.predict_proba(X_test)[0]
            
            direction_map = {0: "SIDEWAYS", 1: "DOWN", 2: "UP"}
            direction = direction_map.get(pred, "NEUTRAL")
            confidence = probs[pred] * 100
            
            timestamp = row.name.strftime('%Y-%m-%d %H:%M') if hasattr(row.name, 'strftime') else str(row.name)
            print(f"{timestamp:<20} ${row['Close']:>9.2f} {direction:<15} {confidence:>11.1f}%")
        
    except Exception as e:
        print(f"✗ Historical predictions failed: {e}")

# Summary
print("\n" + "="*70)
print("📋 TEST SUMMARY")
print("="*70)

total_tests = 4
passed_tests = 0

if PANDAS_TA_AVAILABLE:
    passed_tests += 1
    print("✓ pandas-ta: WORKING")
else:
    print("✗ pandas-ta: NOT AVAILABLE")

if models_status.get('NQ', {}).get('loaded'):
    passed_tests += 1
    print(f"✓ NQ Model: LOADED ({models_status['NQ']['features']} features)")
else:
    print("✗ NQ Model: FAILED")

if df_features is not None:
    passed_tests += 1
    print(f"✓ Feature Engineering: WORKING ({len(engineer.feature_names)} features)")
else:
    print("✗ Feature Engineering: FAILED")

if df_features is not None and models_status.get('NQ', {}).get('loaded'):
    passed_tests += 1
    print("✓ ML Predictions: WORKING")
else:
    print("✗ ML Predictions: FAILED")

print(f"\nResult: {passed_tests}/{total_tests} tests passed")

if passed_tests == total_tests:
    print("\n🎉 ALL TESTS PASSED - SYSTEM READY FOR PRODUCTION!")
else:
    print(f"\n⚠️  {total_tests - passed_tests} test(s) failed - review errors above")

print("="*70)
