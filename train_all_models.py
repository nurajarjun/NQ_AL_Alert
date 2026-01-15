"""
Train XGBoost and Transformer models for all symbols
"""
import sys
import os
import torch
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

from ml.xgboost_model import XGBoostPredictor
from ml.transformer_model import NQTransformer
from ml.feature_engineer import FeatureEngineer
from ml.data_collector import HistoricalDataCollector
import logging
import pandas as pd
import numpy as np
import joblib
from ml.feature_engineer import FeatureEngineer
from ml.data_collector import HistoricalDataCollector
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

SYMBOLS = ["NQ", "ES", "TQQQ", "SQQQ", "SOXL", "SOXS"]

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
        # Ensure we only use the features we inteded (exclude raw OHLCV)
        X_train = train_features[robust_feature_names]
        y_train = train_features['Target']
        X_test = test_features[robust_feature_names]
        y_test = test_features['Target']
        
        # Train
        print(f"4. Training {symbol} model...")
        model.feature_names = robust_feature_names
        
        # ETFs have issues with eval_set metrics (likely NaN/Inf in evaluation),
        # so we disable evals for them to prevent crashing.
        is_etf = symbol in ["TQQQ", "SQQQ", "SOXL", "SOXS"]
        use_evals = not is_etf
        
        if not use_evals:
            print(f"   Note: Disabling eval_set for {symbol} (Stability Mode)")
            
        model.train(X_train, y_train, X_test, y_test, use_eval_set=use_evals)
        
        print(f"\n[OK] {symbol} Model Complete!")
        print(f"   Saved to: {model.model_path}\n")
        
        return True
        
    except Exception as e:
        logger.error(f"[ERROR] Failed to train {symbol}: {e}")
        import traceback
        traceback.print_exc()
        return False


def train_transformer():
    """Train Deep Learning Transformer for NQ"""
    symbol = "NQ"
    print(f"\n{'='*60}")
    print(f"Training TRANSFORMER (Deep Learning) for {symbol}")
    print(f"{'='*60}\n")
    
    try:
        from sklearn.preprocessing import StandardScaler
        from torch.utils.data import TensorDataset, DataLoader
        
        # 1. Setup
        collector = HistoricalDataCollector()
        engineer = FeatureEngineer()
        device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        print(f"   Using device: {device}")
        
        # 2. Data
        print(f"1. Downloading {symbol} training data...")
        df, _ = collector.get_data_for_training(symbol=symbol)
        
        # 3. Features
        print(f"2. Calculating features (Triple Screen: RSI/MACD/ADX)...")
        df_features = engineer.calculate_all_features(df)
        df_features = engineer.create_target_auto(df_features, symbol=symbol)
        
        feature_cols = engineer.feature_names
        target_col = 'Target'
        
        # 4. Preparation (Sequence Generation)
        print(f"3. Preparing sequences (Seq Len=60)...")
        from sklearn.preprocessing import StandardScaler
        scaler = StandardScaler()
        
        # Fit scaler on features only
        scaled_features = scaler.fit_transform(df_features[feature_cols])
        targets = df_features[target_col].values
        
        # Create sequences
        seq_len = 60
        X_seq, y_seq = [], []
        
        for i in range(len(scaled_features) - seq_len):
            X_seq.append(scaled_features[i:i+seq_len])
            y_seq.append(targets[i+seq_len])
            
        X_seq = np.array(X_seq)
        y_seq = np.array(y_seq)
        
        # Convert to Tensor
        X_tensor = torch.FloatTensor(X_seq).to(device)
        y_tensor = torch.LongTensor(y_seq).to(device)
        
        # 5. Training Loop
        print(f"4. Training Neural Network ({len(X_seq)} samples)...")
        feature_dim = X_seq.shape[2]
        model = NQTransformer(feature_dim=feature_dim).to(device)
        
        criterion = torch.nn.CrossEntropyLoss()
        optimizer = torch.optim.Adam(model.parameters(), lr=0.001)
        
        epochs = 15
        dataset = TensorDataset(X_tensor, y_tensor)
        loader = DataLoader(dataset, batch_size=32, shuffle=True)
        
        model.train()
        for epoch in range(epochs):
            total_loss = 0
            for batch_X, batch_y in loader:
                optimizer.zero_grad()
                output = model(batch_X)
                loss = criterion(output, batch_y)
                loss.backward()
                optimizer.step()
                total_loss += loss.item()
            
            if (epoch+1) % 5 == 0:
                print(f"   Epoch {epoch+1}/{epochs} - Loss: {total_loss/len(loader):.4f}")
                
        # 6. Save
        models_dir = os.path.join(os.path.dirname(__file__), 'backend', 'ml', 'models')
        os.makedirs(models_dir, exist_ok=True)
        
        model_path = os.path.join(models_dir, "transformer_model.pth")
        scaler_path = os.path.join(models_dir, "transformer_scaler.pkl")
        
        torch.save(model.state_dict(), model_path)
        joblib.dump(scaler, scaler_path)
        
        print(f"\n[OK] Transformer Logic Trained!")
        print(f"   Brain saved to: {model_path}")
        return True

    except Exception as e:
        logger.error(f"[ERROR] Transformer training failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("\nTraining Multi-Asset XGBoost Models\n")
    
    results = {}
    
    # 1. Train XGBoost
    for symbol in SYMBOLS:
        success = train_symbol(symbol)
        results[symbol] = success
        
    # 2. Train Transformer (NQ Only)
    trans_success = train_transformer()
    results['TRANSFORMER'] = trans_success
    
    print("\n" + "="*60)
    print("TRAINING SUMMARY")
    print("="*60)
    for symbol, success in results.items():
        status = "[SUCCESS]" if success else "[FAILED]"
        print(f"{symbol}: {status}")
    
    total = len(results)
    successful = sum(results.values())
    print(f"\nTotal: {successful}/{total} models trained successfully")

