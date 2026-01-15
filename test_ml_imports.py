"""
Test ML Imports (as server does)
"""
import sys
sys.path.insert(0, 'backend')

print("Testing ML imports...")
print("="*60)

try:
    from ml.ensemble import MLEnsemble
    print("✅ MLEnsemble imported")
except ImportError as e:
    print(f"❌ MLEnsemble failed: {e}")

try:
    from ml.xgboost_model import XGBoostPredictor
    print("✅ XGBoostPredictor imported")
except ImportError as e:
    print(f"❌ XGBoostPredictor failed: {e}")

try:
    from ml.feature_engineer import FeatureEngineer
    print("✅ FeatureEngineer imported")
except ImportError as e:
    print(f"❌ FeatureEngineer failed: {e}")

try:
    from ml.transformer_predictor import TransformerPredictor
    print("✅ TransformerPredictor imported")
except ImportError as e:
    print(f"❌ TransformerPredictor failed: {e}")

try:
    from ml.data_collector import HistoricalDataCollector
    print("✅ HistoricalDataCollector imported")
except ImportError as e:
    print(f"❌ HistoricalDataCollector failed: {e}")

print("="*60)
print("If ANY import failed, ML_AVAILABLE = False")
