"""
Training Pipeline for NQ Transformer
Phase 3: The Architect
"""

import sys
import os
import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import DataLoader, TensorDataset
import numpy as np
import pandas as pd
import logging
from sklearn.model_selection import TimeSeriesSplit
from sklearn.preprocessing import StandardScaler

# Add backend to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from ml.data_collector import HistoricalDataCollector
from ml.feature_engineer import FeatureEngineer
from ml.transformer_model import NQTransformer

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def create_sequences(data, seq_len, feature_cols, target_col='Target'):
    """
    Create sequences for Time Series training
    X: [batch, seq_len, features]
    y: [batch] (class label of the *next* candle after sequence)
    """
    xs = []
    ys = []
    
    data_values = data[feature_cols].values
    target_values = data[target_col].values
    
    for i in range(len(data) - seq_len):
        x = data_values[i : i + seq_len]
        y = target_values[i + seq_len] # Predict the target of the step *after* the sequence
        xs.append(x)
        ys.append(y)
        
    return np.array(xs), np.array(ys)

def train_transformer():
    print("🚀 STARTING TRANSFORMER TRAINING 🚀")
    
    # Configuration
    SEQ_LEN = 60 # Lookback 60 hours
    BATCH_SIZE = 32
    EPOCHS = 5 # Start small for verification
    LR = 0.001
    
    # 1. Load Data
    print("1. Loading Data...")
    # Use absolute path
    data_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "ml", "data")
    collector = HistoricalDataCollector(data_dir=data_dir)
    data = collector.download_nq_data()
    
    # 2. Engineer Features
    print("2. Engineering Features...")
    engineer = FeatureEngineer()
    df = engineer.calculate_all_features(data)
    df = engineer.create_target(df) 
    
    # Flatten columns if needed (FeatureEngineer handles this now but be safe)
    df.columns = [str(col) for col in df.columns]
    
    # Select features (remove non-feature cols)
    feature_names = engineer.feature_names
    logger.info(f"Features: {len(feature_names)}")
    
    # Normalize Features (Important for Deep Learning!)
    print("   Normalizing features...")
    scaler = StandardScaler()
    df[feature_names] = scaler.fit_transform(df[feature_names])
    
    # 3. Create Sequences
    print("3. Creating Sequences...")
    X, y = create_sequences(df, SEQ_LEN, feature_names)
    print(f"   X shape: {X.shape}, y shape: {y.shape}")
    
    # 4. Train/Test Split (Chronological)
    split_idx = int(len(X) * 0.8)
    X_train, X_test = X[:split_idx], X[split_idx:]
    y_train, y_test = y[:split_idx], y[split_idx:]
    
    # Convert to Tensors
    train_data = TensorDataset(torch.from_numpy(X_train).float(), torch.from_numpy(y_train).long())
    test_data = TensorDataset(torch.from_numpy(X_test).float(), torch.from_numpy(y_test).long())
    
    train_loader = DataLoader(train_data, shuffle=True, batch_size=BATCH_SIZE) # Shuffle train
    test_loader = DataLoader(test_data, shuffle=False, batch_size=BATCH_SIZE)
    
    # 5. Initialize Model
    print("4. Initializing Model...")
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    print(f"   Device: {device}")
    
    model = NQTransformer(feature_dim=len(feature_names)).to(device)
    criterion = nn.CrossEntropyLoss()
    optimizer = optim.Adam(model.parameters(), lr=LR)
    
    # 6. Training Loop
    print(f"5. Training for {EPOCHS} epochs...")
    
    for epoch in range(EPOCHS):
        model.train()
        train_loss = 0
        correct = 0
        total = 0
        
        for batch_X, batch_y in train_loader:
            batch_X, batch_y = batch_X.to(device), batch_y.to(device)
            
            optimizer.zero_grad()
            outputs = model(batch_X)
            loss = criterion(outputs, batch_y)
            loss.backward()
            optimizer.step()
            
            train_loss += loss.item()
            _, predicted = torch.max(outputs.data, 1)
            total += batch_y.size(0)
            correct += (predicted == batch_y).sum().item()
            
        print(f"   Epoch {epoch+1}/{EPOCHS} | Loss: {train_loss/len(train_loader):.4f} | Acc: {100 * correct / total:.2f}%")
        
    # 7. Evaluation
    print("6. Evaluating...")
    model.eval()
    correct = 0
    total = 0
    with torch.no_grad():
        for batch_X, batch_y in test_loader:
            batch_X, batch_y = batch_X.to(device), batch_y.to(device)
            outputs = model(batch_X)
            _, predicted = torch.max(outputs.data, 1)
            total += batch_y.size(0)
            correct += (predicted == batch_y).sum().item()
            
    print(f"   Test Accuracy: {100 * correct / total:.2f}%")
    
    # Save Model
    save_path = "ml/models/transformer_model.pth"
    os.makedirs(os.path.dirname(save_path), exist_ok=True)
    torch.save(model.state_dict(), save_path)
    print(f"✅ Model saved to {save_path}")
    
    # Save Scaler
    import joblib
    scaler_path = "ml/models/transformer_scaler.pkl"
    joblib.dump(scaler, scaler_path)
    print(f"✅ Scaler saved to {scaler_path}")

if __name__ == "__main__":
    train_transformer()
