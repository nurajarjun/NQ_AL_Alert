"""
XGBoost Model for NQ Trading Predictions
"""

import xgboost as xgb
import numpy as np
import pandas as pd
import logging
import pickle
import os
import joblib
import json
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix

logger = logging.getLogger(__name__)


class XGBoostPredictor:
    """XGBoost model for predicting price direction (Multi-Asset)"""
    
    def __init__(self, symbol: str):
        self.symbol = symbol
        # Models are in ml/models/ (not backend/ml/models/)
        import os
        project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        self.model_path = os.path.join(project_root, "ml", "models", f"xgboost_model_{symbol}.pkl")
        self.is_trained = os.path.exists(self.model_path)
        self.feature_names = None
        
        if self.is_trained:
            try:
                loaded_data = joblib.load(self.model_path)
                
                # Handle both old format (dict) and new format (direct model)
                if isinstance(loaded_data, dict):
                    self.model = loaded_data.get('model')
                    self.feature_names = loaded_data.get('feature_names')
                    self.is_trained = loaded_data.get('is_trained', True)
                else:
                    # Old format - direct model object
                    self.model = loaded_data
                    # Try to load feature names separately
                    feature_path = self.model_path.replace('.pkl', '_features.json')
                    if os.path.exists(feature_path):
                        with open(feature_path, 'r') as f:
                            self.feature_names = json.load(f)
                
                logger.info(f"✅ Loaded XGBoost model for {symbol} from {self.model_path}")
            except Exception as e:
                logger.error(f"Failed to load model for {symbol}: {e}")
                self.model = None
                self.is_trained = False
        else:
            self.model = None
            logger.warning(f"No trained model found for {symbol} at {self.model_path}")
    
    def train(self, X_train, y_train, X_val=None, y_val=None, use_eval_set=True):
        """
        Train XGBoost model (MULTI-CLASS: 0=SIDEWAYS, 1=DOWN, 2=UP)
        """
        logger.info("Training XGBoost model (Multi-class)...")
        
        # Create XGBoost classifier
        self.model = xgb.XGBClassifier(
            max_depth=6,
            learning_rate=0.05,
            n_estimators=300,
            objective='multi:softprob',
            num_class=3,
            subsample=0.8,
            colsample_bytree=0.8,
            random_state=42,
            eval_metric='mlogloss'
        )
        
        # Prepare evaluation set
        eval_set = []
        if use_eval_set and X_val is not None and y_val is not None:
             eval_set = [(X_train, y_train), (X_val, y_val)]
        
        # Train model
        fit_params = {
            "X": X_train,
            "y": y_train,
            "verbose": True
        }
        
        if eval_set:
             fit_params["eval_set"] = eval_set
             fit_params["early_stopping_rounds"] = 20
             
        self.model.fit(**fit_params)
        
        self.is_trained = True
        
        # Calculate training accuracy
        train_pred = self.model.predict(X_train)
        train_acc = accuracy_score(y_train, train_pred)
        logger.info(f"Training accuracy: {train_acc:.4f}")
        
        if X_val is not None and y_val is not None:
            try:
                val_pred = self.model.predict(X_val)
                val_acc = accuracy_score(y_val, val_pred)
                logger.info(f"Validation accuracy: {val_acc:.4f}")
                logger.info("\nClassification Report:")
                logger.info(classification_report(y_val, val_pred, target_names=['SIDEWAYS', 'DOWN', 'UP']))
            except Exception as e:
                logger.warning(f"Could not calculate validation metrics: {e}")
        
        self.save_model()
        return self.model
    
    def predict(self, X):
        """
        Predict Direction (0=SIDEWAYS, 1=DOWN, 2=UP)
        """
        if not self.is_trained:
            logger.warning("Model not trained! Using fallback prediction")
            return self._fallback_prediction()
        
        # Ensure X is 2D
        if len(X.shape) == 1:
            X = X.reshape(1, -1)
        
        # Get prediction and probabilities
        prediction_idx = self.model.predict(X)[0]
        probabilities = self.model.predict_proba(X)[0]
        
        # Map classes
        classes = {0: "SIDEWAYS", 1: "DOWN", 2: "UP"}
        direction = classes.get(prediction_idx, "SIDEWAYS")
        
        confidence = float(probabilities[prediction_idx])
        
        return {
            "direction": direction,
            "confidence": confidence,
            "score": int(confidence * 100),
            "probabilities": {
                "sideways": float(probabilities[0]),
                "down": float(probabilities[1]),
                "up": float(probabilities[2])
            },
            "model": "XGBoost Multi-class"
        }
    
    def predict_with_features(self, features_dict):
        """
        Predict using a dictionary of features
        
        Args:
            features_dict: Dictionary with feature names and values
            
        Returns:
            Prediction dictionary
        """
        if self.feature_names is None:
            logger.error("Feature names not set!")
            return self._fallback_prediction()
        
        # Create feature array in correct order
        X = np.array([features_dict.get(name, 0) for name in self.feature_names])
        
        return self.predict(X)
    
    def get_feature_importance(self, top_n=20):
        """
        Get feature importance scores
        
        Args:
            top_n: Number of top features to return
            
        Returns:
            List of (feature_name, importance) tuples
        """
        if not self.is_trained or self.feature_names is None:
            return []
        
        importance = self.model.feature_importances_
        
        # Sort by importance
        feature_importance = sorted(
            zip(self.feature_names, importance),
            key=lambda x: x[1],
            reverse=True
        )
        
        return feature_importance[:top_n]
    
    def save_model(self):
        """Save model to disk"""
        try:
            with open(self.model_path, 'wb') as f:
                pickle.dump({
                    'model': self.model,
                    'feature_names': self.feature_names,
                    'is_trained': self.is_trained
                }, f)
            logger.info(f"Model saved to {self.model_path}")
        except Exception as e:
            logger.error(f"Error saving model: {e}")
    
    def load_model(self):
        """Load model from disk"""
        if not os.path.exists(self.model_path):
            logger.info("No saved model found")
            return False
        
        try:
            with open(self.model_path, 'rb') as f:
                data = pickle.load(f)
                self.model = data['model']
                self.feature_names = data.get('feature_names')
                self.is_trained = data.get('is_trained', False)
            logger.info(f"Model loaded from {self.model_path}")
            return True
        except Exception as e:
            logger.error(f"Error loading model: {e}")
            return False
    
    def _fallback_prediction(self):
        """Fallback prediction when model not available"""
        return {
            "direction": "SIDEWAYS",
            "confidence": 0.33,
            "score": 33,
            "probabilities": {
                "down": 0.33,
                "sideways": 0.34,
                "up": 0.33
            },
            "model": "XGBoost (fallback)"
        }


if __name__ == "__main__":
    # Test XGBoost model
    logging.basicConfig(level=logging.INFO)
    
    from ml.data_collector import HistoricalDataCollector
    from ml.feature_engineer import FeatureEngineer
    
    print("="*60)
    print("XGBOOST MODEL TRAINING")
    print("="*60)
    
    # Load data
    print("\n1. Loading historical data...")
    collector = HistoricalDataCollector()
    data = collector.download_nq_data()
    print(f"   Loaded {len(data)} candles")
    
    # Calculate features
    print("\n2. Calculating features...")
    engineer = FeatureEngineer()
    data_with_features = engineer.calculate_all_features(data)
    data_with_target = engineer.create_target(data_with_features)
    print(f"   Created {len(engineer.feature_names)} features")
    
    # Prepare train/test split
    print("\n3. Splitting data...")
    split_idx = int(len(data_with_target) * 0.8)
    train_data = data_with_target.iloc[:split_idx]
    test_data = data_with_target.iloc[split_idx:]
    
    X_train = engineer.get_feature_matrix(train_data)
    y_train = engineer.get_target_vector(train_data)
    X_test = engineer.get_feature_matrix(test_data)
    y_test = engineer.get_target_vector(test_data)
    
    print(f"   Training samples: {len(X_train)}")
    print(f"   Testing samples: {len(X_test)}")
    
    # Train model
    print("\n4. Training XGBoost model...")
    model = XGBoostPredictor(symbol="NQ")
    model.feature_names = engineer.feature_names
    model.train(X_train, y_train, X_test, y_test)
    
    # Test prediction
    print("\n5. Testing prediction...")
    test_sample = X_test[0]
    prediction = model.predict(test_sample)
    
    print(f"\nPrediction: {prediction['direction']}")
    print(f"Confidence: {prediction['confidence']:.2%}")
    print(f"Score: {prediction['score']}/100")
    print(f"\nProbabilities:")
    for direction, prob in prediction['probabilities'].items():
        print(f"  {direction.upper()}: {prob:.2%}")
    
    # Show feature importance
    print("\n6. Top 10 Most Important Features:")
    for i, (feature, importance) in enumerate(model.get_feature_importance(10), 1):
        print(f"   {i}. {feature}: {importance:.4f}")
    
    print("\n" + "="*60)
    print("✅ XGBoost model trained and ready!")
    print("="*60)
