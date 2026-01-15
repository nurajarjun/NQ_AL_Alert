import sys
import os
import traceback
import numpy as np

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

from ml.xgboost_model import XGBoostPredictor
from ml.feature_engineer import FeatureEngineer
from ml.data_collector import HistoricalDataCollector

def train_tqqq():
    print("Starting TQQQ debug training...")
    try:
        collector = HistoricalDataCollector()
        engineer = FeatureEngineer()
        
        print("1. Downloading Data...")
        # Force fresh download to be sure
        train_data, test_data = collector.get_data_for_training(symbol="TQQQ")
        print(f"Data Loaded: {len(train_data)} train, {len(test_data)} test")
        print(f"Index Type: {type(train_data.index)}")
        print(f"Index Sample: {train_data.index[:3]}")

        print("2. Calculating Features...")
        train_features = engineer.calculate_all_features(train_data)
        test_features = engineer.calculate_all_features(test_data) # Need test too
        
        print("3. Creating Targets...")
        train_features = engineer.create_target_auto(train_features, symbol="TQQQ")
        test_features = engineer.create_target_auto(test_features, symbol="TQQQ")
        
        robust_feature_names = engineer.feature_names
        
        X_train = train_features[robust_feature_names]
        y_train = train_features['Target']
        X_test = test_features[robust_feature_names]
        y_test = test_features['Target']
        
        # DEBUG: Check for NaNs
        print("\nDEBUG: Checking for NaNs in X_train...", flush=True)
        print(f"X_train shape: {X_train.shape}", flush=True)
        print(f"y_train shape: {y_train.shape}", flush=True)
        
        if X_train.empty:
            print("❌ X_train is EMPTY! Feature engineering dropped all rows.", flush=True)
            return

        # Force Float
        X_train = X_train.astype(float)
        X_test = X_test.astype(float)
        
        nan_cols = X_train.columns[X_train.isna().any()].tolist()
        if nan_cols:
            print(f"❌ FOUND NaNs in columns: {nan_cols}", flush=True)
            print(X_train[nan_cols].isna().sum(), flush=True)
            X_train = X_train.fillna(0)
            X_test = X_test.fillna(0)
            print("⚠️ Filled NaNs with 0 for debugging.", flush=True)
        else:
            print("✅ No NaNs found in X_train.", flush=True)
            
        # DEBUG: Check for Infinite values
        print("\nDEBUG: Checking for Inf values...", flush=True)
        inf_cols = X_train.columns[np.isinf(X_train).any()].tolist()
        if inf_cols:
            print(f"❌ FOUND Inf values in columns: {inf_cols}", flush=True)
            X_train = X_train.replace([np.inf, -np.inf], 0)
            X_test = X_test.replace([np.inf, -np.inf], 0)
            print("⚠️ Replaced Inf with 0.", flush=True)
        else:
            print("✅ No Inf values found in X_train.", flush=True)

        # DEBUG: Check Targets
        print("\nDEBUG: Checking Targets...", flush=True)
        if y_train.isna().any():
            print("❌ FOUND NaNs in y_train!", flush=True)
        if y_test.isna().any():
            print("❌ FOUND NaNs in y_test!", flush=True)
        print(f"y_train unique: {y_train.unique()}", flush=True)

        # Dump Data for Inspection
        try:
            print("\nDEBUG: Dumping training data to debug_etf_data.csv...", flush=True)
            debug_df = X_train.copy()
            debug_df['Target'] = y_train
            debug_df.to_csv("debug_etf_data.csv")
            print("✅ Data dumped successfully.", flush=True)
        except Exception as e:
            print(f"❌ Failed to dump data: {e}", flush=True)

        print("4. Training Model (Evals DISABLED)...", flush=True)
        model = XGBoostPredictor(symbol="TQQQ")
        model.feature_names = robust_feature_names
        # Turn off evals to isolate crash
        model.train(X_train, y_train, X_test, y_test, use_eval_set=False)
        
        print("Basic Training Complete.")
        
    except Exception:
        with open("debug_traceback.txt", "w") as f:
            traceback.print_exc(file=f)
        print("Error occurred. traceback saved to debug_traceback.txt")
        traceback.print_exc()

if __name__ == "__main__":
    train_tqqq()
