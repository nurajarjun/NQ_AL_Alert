"""
Test XGBoost Model Loading
"""
import sys
import os
sys.path.insert(0, 'backend')

print("="*60)
print("TESTING XGBOOST MODEL LOADING")
print("="*60)

# Test 1: Import
print("\n1. Testing imports...")
try:
    from ml.xgboost_model import XGBoostPredictor
    print("   ✅ XGBoostPredictor imported")
except Exception as e:
    print(f"   ❌ Import failed: {e}")
    sys.exit(1)

# Test 2: Load NQ model
print("\n2. Loading NQ model...")
try:
    nq_model = XGBoostPredictor('NQ')
    print(f"   Model path: {nq_model.model_path}")
    print(f"   File exists: {os.path.exists(nq_model.model_path)}")
    print(f"   Is trained: {nq_model.is_trained}")
    print(f"   Model loaded: {nq_model.model is not None}")
    
    if nq_model.is_trained and nq_model.model:
        print("   ✅ NQ model loaded successfully")
    else:
        print("   ❌ NQ model failed to load")
except Exception as e:
    print(f"   ❌ Error: {e}")
    import traceback
    traceback.print_exc()

# Test 3: Check ml_models dict (as server does)
print("\n3. Testing ml_models dict initialization...")
try:
    ml_models = {}
    SYMBOLS = ["NQ", "ES"]
    
    for symbol in SYMBOLS:
        try:
            xgboost_model = XGBoostPredictor(symbol=symbol)
            if xgboost_model.is_trained:
                ml_models[symbol] = xgboost_model
                print(f"   ✅ {symbol} added to ml_models")
            else:
                print(f"   ⚠️ {symbol} not trained - skipping")
        except Exception as e:
            print(f"   ❌ {symbol} failed: {e}")
    
    print(f"\n   ml_models dict: {list(ml_models.keys())}")
    print(f"   'NQ' in ml_models: {'NQ' in ml_models}")
    
except Exception as e:
    print(f"   ❌ Error: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "="*60)
print("TEST COMPLETE")
print("="*60)
