"""
Transformer Predictor
Wrapper class for live inference using the NQ Transformer
Phase 4: The Integration
"""

import torch
import numpy as np
import pandas as pd
import joblib
import os
import logging
from .transformer_model import NQTransformer
from .feature_engineer import FeatureEngineer

logger = logging.getLogger(__name__)

class TransformerPredictor:
    """Wrapper for Transformer inference"""
    
    def __init__(self, 
                 model_path="ml/models/transformer_model.pth",
                 scaler_path="ml/models/transformer_scaler.pkl"):
        
        self.output_dir = os.path.dirname(os.path.abspath(__file__))
        # Adjust paths to be relative to this file if needed, or absolute
        # Assuming run from backend/ or root, let's make them robust
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        self.model_path = os.path.join(base_dir, model_path)
        self.scaler_path = os.path.join(base_dir, scaler_path)
        
        self.model = None
        self.scaler = None
        self.feature_engineer = FeatureEngineer()
        self.device = torch.device("cpu") # Inference on CPU is fine
        self.seq_len = 60
        self.feature_dim = 34 # Default, will update from scaler/model
        
        self.load_artifacts()
        
    def load_artifacts(self):
        """Load model and scaler"""
        try:
            if not os.path.exists(self.model_path) or not os.path.exists(self.scaler_path):
                logger.warning(f"Artifacts not found: {self.model_path} or {self.scaler_path}")
                return False
            
            # Load Scaler
            self.scaler = joblib.load(self.scaler_path)
            self.feature_dim = self.scaler.n_features_in_
            logger.info(f"Scaler loaded. Feature dim: {self.feature_dim}")
            
            # Load Model
            self.model = NQTransformer(feature_dim=self.feature_dim)
            self.model.load_state_dict(torch.load(self.model_path, map_location=self.device))
            self.model.to(self.device)
            self.model.eval()
            logger.info(f"Transformer model loaded from {self.model_path}")
            
            return True
            
        except Exception as e:
            logger.error(f"Error loading Transformer artifacts: {e}")
            return False

    def predict(self, df):
        """
        Make prediction on latest data
        
        Args:
            df: DataFrame with OHLCV data (must have at least seq_len rows)
        """
        if self.model is None or self.scaler is None:
            return self._fallback()
        
        try:
            # 1. Calculate Features
            df_features = self.feature_engineer.calculate_all_features(df)
            
            # Ensure columns match scaler (FeatureEngineer now ensures string cols)
            feature_names = self.feature_engineer.feature_names
            
            # Check if we have enough data
            if len(df_features) < self.seq_len:
                logger.warning(f"Not enough data for Transformer. Need {self.seq_len}, got {len(df_features)}")
                return self._fallback()
            
            # 2. Get last sequence
            latest_features = df_features[feature_names].tail(self.seq_len).values
            
            logger.info(f"DEBUG: Input shape: {latest_features.shape}, Scaler expects: {self.scaler.n_features_in_}")
            print(f"DEBUG: Input shape: {latest_features.shape}, Scaler expects: {self.scaler.n_features_in_}")

            # 3. Normalize
            try:
                latest_features_scaled = self.scaler.transform(latest_features)
            except Exception as e:
                logger.warning(f"Scaler transform failed ({e}). Re-fitting scaler on current data...")
                # Refit on all available history in df_features
                all_features = df_features[feature_names].values
                self.scaler.fit(all_features)
                latest_features_scaled = self.scaler.transform(latest_features)
                logger.info("Scaler re-fitted successfully.")

            # 4. To Tensor [Batch, Seq, Feat]
            input_tensor = torch.tensor(latest_features_scaled, dtype=torch.float32).unsqueeze(0).to(self.device)
            
            # 5. Inference
            with torch.no_grad():
                output = self.model(input_tensor)
                probabilities = torch.softmax(output, dim=1).cpu().numpy()[0]
                prediction_idx = torch.argmax(output, dim=1).item()
            
            # Map result
            direction_map = {0: "DOWN", 1: "SIDEWAYS", 2: "UP"}
            direction = direction_map[prediction_idx]
            confidence = float(probabilities[prediction_idx])
            
            return {
                "direction": direction,
                "confidence": confidence,
                "score": int(confidence * 100),
                "probabilities": {
                    "down": float(probabilities[0]),
                    "sideways": float(probabilities[1]),
                    "up": float(probabilities[2])
                },
                "model": "Transformer (Deep Learning)"
            }
            
        except Exception as e:
            logger.error(f"Prediction failed: {e}")
            import traceback
            traceback.print_exc()
            return self._fallback()
            
    def _fallback(self):
        return {
            "direction": "SIDEWAYS",
            "confidence": 0.0,
            "score": 0,
            "probabilities": {"down": 0.33, "sideways": 0.34, "up": 0.33},
            "model": "None"
        } 
