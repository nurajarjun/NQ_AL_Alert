"""
Final Verification - No Fake Things
"""
import sys
sys.path.insert(0, 'backend')

print("="*60)
print("FINAL SYSTEM VERIFICATION")
print("="*60)

# Test 1: ML Models
print("\n1. ML MODELS")
try:
    from ml.xgboost_model import XGBoostPredictor
    
    nq_model = XGBoostPredictor(symbol='NQ')
    es_model = XGBoostPredictor(symbol='ES')
    
    print(f"   NQ: {'✅ TRAINED' if nq_model.is_trained else '❌ NOT TRAINED'}")
    if nq_model.is_trained:
        print(f"       Features: {len(nq_model.feature_names)}")
    
    print(f"   ES: {'✅ TRAINED' if es_model.is_trained else '❌ NOT TRAINED'}")
    if es_model.is_trained:
        print(f"       Features: {len(es_model.feature_names)}")
except Exception as e:
    print(f"   ❌ ERROR: {e}")

# Test 2: Institutional Features
print("\n2. INSTITUTIONAL FEATURES")
try:
    from ml.feature_engineer import FeatureEngineer
    
    eng = FeatureEngineer()
    methods = ['_add_60m_ema', '_detect_fvg', '_detect_opening_drive', '_analyze_gaps']
    
    for method in methods:
        exists = hasattr(eng, method)
        print(f"   {method}: {'✅ EXISTS' if exists else '❌ MISSING'}")
except Exception as e:
    print(f"   ❌ ERROR: {e}")

# Test 3: Scanner
print("\n3. ENHANCED SCANNER")
try:
    from analysis.enhanced_scanner import EnhancedStockScanner
    
    scanner = EnhancedStockScanner()
    print(f"   Scanner: ✅ CREATED")
    print(f"   Watchlist: {len(scanner.watchlist)} stocks")
except Exception as e:
    print(f"   ❌ ERROR: {e}")

# Test 4: Trade Tracker
print("\n4. TRADE TRACKER")
try:
    from ml.trade_tracker import TradeTracker
    
    tracker = TradeTracker()
    print(f"   Database: ✅ INITIALIZED")
    print(f"   Path: {tracker.db_path}")
except Exception as e:
    print(f"   ❌ ERROR: {e}")

# Test 5: Auto-Retrainer
print("\n5. AUTO-RETRAINER")
try:
    from ml.auto_retrainer import AutoRetrainer
    
    retrainer = AutoRetrainer()
    print(f"   Retrainer: ✅ READY")
    print(f"   Min trades: {retrainer.min_trades_for_retrain}")
except Exception as e:
    print(f"   ❌ ERROR: {e}")

print("\n" + "="*60)
print("VERIFICATION COMPLETE")
print("="*60)
