
import sys
import os
import pandas as pd
import numpy as np
import logging

# Setup backend path
sys.path.insert(0, '/app/backend')

from ml.data_collector import HistoricalDataCollector
from ml.feature_engineer import FeatureEngineer, PANDAS_TA_AVAILABLE
from ml.xgboost_model import XGBoostPredictor

# Configure logging
logging.basicConfig(level=logging.ERROR)
logger = logging.getLogger(__name__)

def backtest_today():
    print("="*60)
    print("NQ AI Alert System - Backtest Today")
    print("="*60)
    
    if not PANDAS_TA_AVAILABLE:
        print("❌ pandas-ta not available - cannot calculate features")
        return

    # 1. Load Data
    print("\n1. Fetching NQ data...")
    collector = HistoricalDataCollector()
    # download_nq_data automatically handles interval (usually 1h for NQ)
    # forcing refresh to get latest
    df = collector.download_nq_data(force_refresh=True, symbol="NQ")
    
    # Filter for "today" (last 24h or current trading session)
    print(f"   Fetched {len(df)} candles")
    print(f"   Last candle: {df.index[-1]}")
    
    # Check frequency
    if len(df) > 1:
        time_diff = (df.index[1] - df.index[0]).total_seconds() / 60
        print(f"   Interval: {time_diff:.0f} minutes")
    
    # Load Model
    print("\n2. Loading NQ Model...")
    model = XGBoostPredictor('NQ')
    if not model.is_trained:
        print("❌ Model not trained!")
        return

    # Select samples for backtesting
    # To verify 5-hour lookahead, we need to go back at least 6-7 hours.
    # Let's pick 5 points from the last 24 hours that have resolved outcomes.
    
    # Indices: We need `idx + 5` to be valid. 
    # Max valid training idx = len(df) - 1 - 5 = len(df) - 6.
    
    if len(df) < 20:
        print("❌ Not enough data for backtest (need >20 candles)")
        return
        
    # Pick 5 indices ending at len(df)-6
    # e.g. [-10, -9, -8, -7, -6]
    test_indices = list(range(-10, -5))
    
    engineer = FeatureEngineer()
    
    print("\n3. Running Backtest (Model Horizon: 5 Hours)...")
    print(f"{'Time (UTC)':<22} {'Price':<10} {'Pred':<10} {'Conf':<8} {'Active(5h)':<12} {'Result'}")
    print("-" * 80)
    
    correct_count = 0
    valid_comparisons = 0
    
    for relative_idx in test_indices:
        # absolute index
        abs_idx = len(df) + relative_idx
        target_time = df.index[abs_idx]
        
        # Slice for feature calc (must perform strict cutoff)
        df_slice = df.iloc[:abs_idx+1].copy()
        
        try:
            df_features = engineer.calculate_all_features(df_slice)
        except Exception as e:
            continue
            
        latest_features = df_features.iloc[-1:]
        if latest_features['EMA_200'].isna().any():
             continue

        X = latest_features.drop(['Target'], axis=1, errors='ignore')
        
        # Align features
        if model.feature_names:
             X_model = pd.DataFrame(0, index=X.index, columns=model.feature_names)
             for col in X.columns:
                 if col in model.feature_names:
                     X_model[col] = X[col]
             X = X_model.values
        else:
             X = X.values

        pred_idx = model.model.predict(X)[0]
        probs = model.model.predict_proba(X)[0]
        confidence = probs[pred_idx] * 100
        
        dir_map = {0: "SIDEWAYS", 1: "DOWN", 2: "UP"}
        prediction = dir_map.get(pred_idx, "SIDEWAYS")
        
        # Truth Check (5 hours later)
        lookahead = 5
        if abs_idx + lookahead < len(df):
            current_close = df.iloc[abs_idx]['Close']
            future_close = df.iloc[abs_idx + lookahead]['Close']
            
            pct_change = (future_close - current_close) / current_close
            # Threshold from training defaults
            threshold = 0.001 
            
            if pct_change > threshold:
                truth = "UP"
            elif pct_change < -threshold:
                truth = "DOWN"
            else:
                truth = "SIDEWAYS"
                
            if prediction == truth:
                result = "✅"
                correct_count += 1
            else:
                result = f"❌ ({truth})"
            valid_comparisons += 1
        else:
            truth = "?"
            result = "Pending"

        price_str = f"{df.iloc[abs_idx]['Close']:.2f}"
        result_line = f"{str(target_time):<22} {price_str:<10} {prediction:<10} {confidence:<8.1f} {truth:<12} {result}"
        print(result_line)
        with open("results.txt", "a") as f:
            f.write(result_line + "\n")

    print("-" * 80)
    summary = ""
    if valid_comparisons > 0:
        summary = f"Accuracy: {correct_count}/{valid_comparisons} ({correct_count/valid_comparisons*100:.0f}%)"
    else:
        summary = "No resolved predictions to verify (all pending)"
    print(summary)
    with open("results.txt", "a") as f:
        f.write("-" * 80 + "\n")
        f.write(summary + "\n")

if __name__ == "__main__":
    backtest_today()
