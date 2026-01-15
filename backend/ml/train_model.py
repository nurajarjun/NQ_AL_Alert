
import sys
import os
import pandas as pd
import numpy as np
import logging

# Path setup
sys.path.append(os.getcwd())
try:
    from backend.ml.xgboost_model import XGBoostPredictor
    from backend.ml.feature_engineer import FeatureEngineer
except ImportError:
    sys.path.append(os.path.join(os.getcwd(), 'backend'))
    from ml.xgboost_model import XGBoostPredictor
    from ml.feature_engineer import FeatureEngineer

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("TRAIN")

def train():
    logger.info("loading Data...")
    df = pd.read_csv("backend/data/training_data.csv", index_col=0, parse_dates=True)
    
    # Drop rows without target (lookahead gap) or features
    df = df.dropna()
    
    logger.info(f"Training on {len(df)} samples...")
    
    fe = FeatureEngineer()
    
    # Prepare X and y
    # X must match what FeatureEngineer produces
    feature_cols = [c for c in df.columns if c not in ['target', 'Open', 'High', 'Low', 'Close', 'Volume', 'Adj Close']]
    # Ideally reuse FeatureEngineer methods to ensure consistency
    # But generate_labels already calculated features and saved them in CSV
    
    X = df[feature_cols].values
    y = df['target'].values
    
    # Split
    split = int(len(X) * 0.8)
    X_train, X_test = X[:split], X[split:]
    y_train, y_test = y[:split], y[split:]
    
    logger.info(f"Train size: {len(X_train)}, Test size: {len(X_test)}")
    
    # Train
    predictor = XGBoostPredictor()
    predictor.feature_names = feature_cols
    predictor.train(X_train, y_train, X_test, y_test)
    
    logger.info("✅ Training Complete.")

if __name__ == "__main__":
    train()
