#!/usr/bin/env python3
"""
Train XGBoost models for all symbols (No Transformer - torch not available)
"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

from ml.xgboost_model import XGBoostPredictor
from ml.feature_engineer import FeatureEngineer
from ml.data_collector import HistoricalDataCollector
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

SYMBOLS = ["NQ", "ES", "SPY", "TQQQ", "SQQQ", "SOXL", "SOXS"]

def train_symbol(symbol):
    """Train XGBoost model for a single symbol"""
    print(f"\n{'='*60}")
    print(f"Training {symbol} Model")
    print(f"{'='*60}\n")
    
    try:
        # Initialize components
        collector = HistoricalDataCollector()
        engineer = FeatureEngineer()
        model = XGBoostPredictor(symbol=symbol)
        
        # Download data
        print(f"1. Downloading {symbol} historical data...")
        train_data, test_data = collector.get_data_for_training(symbol=symbol)
        
        # Engineer features
        print(f"2. Engineering features for {symbol}...")
        train_features = engineer.calculate_all_features(train_data)
        # Capture robust feature names from training set
        robust_feature_names = engineer.feature_names
        
        test_features = engineer.calculate_all_features(test_data)
        
        # Create targets (auto-detects daily vs hourly)
        print(f"3. Creating targets for {symbol}...")
        train_features = engineer.create_target_auto(train_features, symbol=symbol)
        test_features = engineer.create_target_auto(test_features, symbol=symbol)
        
        # Prepare data
        X_train = train_features[robust_feature_names]
        y_train = train_features['Target']
        X_test = test_features[robust_feature_names]
        y_test = test_features['Target']
        
        # Train
        print(f"4. Training {symbol} model...")
        model.feature_names = robust_feature_names
        
        # ETFs have issues with eval_set metrics, so we disable evals for them
        is_etf = symbol in ["TQQQ", "SQQQ", "SOXL", "SOXS"]
        use_evals = not is_etf
        
        if not use_evals:
            print(f"   Note: Disabling eval_set for {symbol} (Stability Mode)")
            
        model.train(X_train, y_train, X_test, y_test, use_eval_set=use_evals)
        
        print(f"\n✅ {symbol} Model Complete!")
        print(f"   Saved to: {model.model_path}\n")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Failed to train {symbol}: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    print("\n" + "="*60)
    print("Training XGBoost Models for All Symbols")
    print("="*60 + "\n")
    
    results = {}
    
    # Train XGBoost for all symbols
    for symbol in SYMBOLS:
        success = train_symbol(symbol)
        results[symbol] = success
    
    # Summary
    print("\n" + "="*60)
    print("TRAINING SUMMARY")
    print("="*60)
    for symbol, success in results.items():
        status = "✅ SUCCESS" if success else "❌ FAILED"
        print(f"{symbol:6} {status}")
    
    total = len(results)
    successful = sum(results.values())
    print(f"\nTotal: {successful}/{total} models trained successfully")
    print("="*60 + "\n")
