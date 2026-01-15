
import sys
import os
import pandas as pd
import numpy as np

# Ensure we can import from backend
sys.path.append(os.path.abspath("backend"))

from ml.data_collector import HistoricalDataCollector
from ml.feature_engineer import FeatureEngineer

print("Loading data...")
# Use absolute path
data_dir = r"d:\Google\.gemini\antigravity\scratch\NQ-AI-Alerts\backend\ml\data"
collector = HistoricalDataCollector(data_dir=data_dir)
data = collector.download_nq_data()

print(f"Data Shape: {data.shape}")

print("\n--- TEST FEATURE ENGINEER ---")
try:
    engineer = FeatureEngineer()
    print("Calculating features...")
    df = engineer.calculate_all_features(data)
    print(f"Features Shape: {df.shape}")
    print("Columns:", df.columns.tolist()[:5])
    
    print("DF Info:")
    df.info()
    
    print("\nCreating target...")
    df = engineer.create_target(df)
    print(f"Target Shape: {df.shape}")
    print("Target Info:")
    df[['Target']].info()
    
    print("\nSelect Features...")
    X = df[engineer.feature_names]
    print("X Info:")
    X.info()
    
except Exception as e:
    print(f"ERROR: {e}")
    import traceback
    traceback.print_exc()
