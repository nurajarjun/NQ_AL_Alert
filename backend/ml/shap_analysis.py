"""
SHAP Analysis Script
Scientifically determines feature importance using SHAP values.
Phase 2: The Scientist
"""

import sys
import os
import pandas as pd
import numpy as np
import xgboost as xgb
# import shap
import logging
from sklearn.model_selection import TimeSeriesSplit

# Ensure we can import from backend
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from data_collector import HistoricalDataCollector
from feature_engineer import FeatureEngineer

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def run_shap_analysis():
    print("🔬 STARTING SHAP ANALYSIS 🔬")
    print("--------------------------------")
    
    # 1. Load Data (Use Training CSV from Generate Labels)
    print("1. Loading Training Data...")
    training_file = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data", "training_data.csv")
    
    if not os.path.exists(training_file):
        print("Error: training_data.csv not found!")
        return

    df = pd.read_csv(training_file, index_col=0, parse_dates=True)
    df = df.dropna()
    
    # 2. Prepare X and y
    # Filter columns
    feature_names = [c for c in df.columns if c not in ['target', 'Open', 'High', 'Low', 'Close', 'Volume', 'Adj Close']]
    X = df[feature_names]
    y = df['target'] # Binary Target 0 or 1
    
    print(f"   Dataset Shape: {X.shape}")
    print(f"   Features: {len(feature_names)}")

    print("\n--- DEBUG DATA ---")
    print(X.info())
    print(y.info())
    print("\nCheck for object columns:")
    print(X.select_dtypes(include=['object']).columns)
    print("------------------\n")

    # 4. Train XGBoost (Chronological Split)
    # Use last 20% for validation/explanation
    split_idx = int(len(X) * 0.8)
    
    # Cast to numpy to avoid pandas dimensional issues
    X_np = X.values
    y_np = y.values
    
    X_train_np, X_test_np = X_np[:split_idx], X_np[split_idx:]
    y_train_np, y_test_np = y_np[:split_idx], y_np[split_idx:]
    
    print(f"Train shapes: X={X_train_np.shape}, y={y_train_np.shape}")
    
    print("3. Training XGBoost Model...")
    # Use minimal params like debug_xgb.py
    model = xgb.XGBClassifier(
        n_estimators=100,
        max_depth=5,
        random_state=42
    )
    model.fit(X_train_np, y_train_np.ravel())
    print("✅ Model trained successfully!")
    
    # 5. Extract Native Feature Importance
    print("4. Extracting Native Feature Importance...")
    # Get importance (gain)
    importance = model.feature_importances_
    
    # Create Importance DataFrame
    importance_df = pd.DataFrame({
        'Feature': feature_names,
        'Importance': importance
    }).sort_values(by='Importance', ascending=False)
    
    # Normalize importance to 0-100 score
    if importance_df['Importance'].max() > 0:
        importance_df['Score'] = (importance_df['Importance'] / importance_df['Importance'].max()) * 100
    else:
        importance_df['Score'] = 0
    
    # 6. Report
    print("\n📊 FEATURE IMPORTANCE RANKING (Top 20) 📊")
    print("------------------------------------------")
    print(format_dataframe(importance_df.head(20)))
    
    print("\n🗑️ WEAK FEATURES (Score < 5) 🗑️")
    print("---------------------------------")
    weak_features = importance_df[importance_df['Score'] < 5]
    if not weak_features.empty:
        print(format_dataframe(weak_features))
        print(f"\nRecommendation: Drop these {len(weak_features)} features.")
    else:
        print("No extremely weak features found.")

    return importance_df

def format_dataframe(df):
    # Helper to print nice tables
    return df.to_string(index=False, float_format=lambda x: "{:.2f}".format(x))

if __name__ == "__main__":
    run_shap_analysis()
