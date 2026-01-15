
import sys
import os
import pandas as pd
import numpy as np
import xgboost as xgb

# Ensure we can import from backend
sys.path.append(os.path.abspath("backend"))

from ml.data_collector import HistoricalDataCollector
from ml.feature_engineer import FeatureEngineer

print("Loading data...")
try:
    data_dir = r"d:\Google\.gemini\antigravity\scratch\NQ-AI-Alerts\backend\ml\data"
    collector = HistoricalDataCollector(data_dir=data_dir)
    data = collector.download_nq_data()
    
    engineer = FeatureEngineer()
    df = engineer.calculate_all_features(data)
    df = engineer.create_target(df)
    
    # Flatten columns again to be sure
    df.columns = [str(c) for c in df.columns]
    
    feature_names = engineer.feature_names
    X = df[feature_names].values
    y = df['Target'].values
    
    print(f"Full Data: X={X.shape}, y={y.shape}")
    print(f"X types: {X.dtype}")
    print(f"y types: {y.dtype}")
    
    # Check for NaNs or Infs
    print(f"X NaNs: {np.isnan(X).sum()}")
    print(f"X Infs: {np.isinf(X).sum()}")
    
    # Test 1: Random Data
    print("\n--- TEST 1: Random Data ---")
    X_rand = np.random.rand(100, X.shape[1])
    y_rand = np.random.randint(0, 3, 100)
    model = xgb.XGBClassifier(n_estimators=10)
    model.fit(X_rand, y_rand)
    print("Random data fit SUCCESS")
    
    # Test 2: Real Data Small
    print("\n--- TEST 2: Real Data (100 rows) ---")
    model2 = xgb.XGBClassifier(n_estimators=10)
    model2.fit(X[:100], y[:100])
    print("Real data (100) fit SUCCESS")
    
    # Test 3: Real Data Full
    print("\n--- TEST 3: Real Data (Full) ---")
    model3 = xgb.XGBClassifier(n_estimators=10)
    model3.fit(X, y)
    print("Real data (Full) fit SUCCESS")

except Exception as e:
    print(f"CRASHED: {e}")
    import traceback
    traceback.print_exc()
