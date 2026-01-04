"""
ML Ensemble Manager
Combines multiple ML models for better predictions
"""

import logging
import numpy as np

logger = logging.getLogger(__name__)


class MLEnsemble:
    """Manages multiple ML models and combines their predictions"""
    
    def __init__(self):
        self.models = {}
        self.weights = {}
        self.enabled_models = set()
    
    def add_model(self, name, model, weight=1.0, enabled=True):
        """
        Add a model to the ensemble
        
        Args:
            name: Model name (e.g., 'xgboost', 'lstm')
            model: Model instance
            weight: Weight for this model's predictions
            enabled: Whether to use this model
        """
        self.models[name] = model
        self.weights[name] = weight
        
        if enabled:
            self.enabled_models.add(name)
            logger.info(f"✅ Added {name} to ensemble (weight: {weight})")
        else:
            logger.info(f"➕ Added {name} to ensemble (disabled)")
    
    def enable_model(self, name):
        """Enable a model"""
        if name in self.models:
            self.enabled_models.add(name)
            logger.info(f"✅ Enabled {name}")
    
    def disable_model(self, name):
        """Disable a model"""
        if name in self.enabled_models:
            self.enabled_models.remove(name)
            logger.info(f"❌ Disabled {name}")
    
    def remove_model(self, name):
        """Remove a model from ensemble"""
        if name in self.models:
            del self.models[name]
            del self.weights[name]
            self.enabled_models.discard(name)
            logger.info(f"🗑️ Removed {name} from ensemble")
    
    def predict(self, X):
        """
        Get combined prediction from all enabled models
        
        Args:
            X: Feature vector or matrix
            
        Returns:
            Dictionary with combined prediction
        """
        if not self.enabled_models:
            logger.warning("No models enabled in ensemble!")
            return self._empty_prediction()
        
        predictions = {}
        scores = []
        confidences = []
        
        # Get prediction from each enabled model
        for name in self.enabled_models:
            try:
                model = self.models[name]
                pred = model.predict(X)
                predictions[name] = pred
                
                # Collect scores and confidences
                scores.append(pred.get('score', 50) * self.weights[name])
                confidences.append(pred.get('confidence', 0.5) * self.weights[name])
                
            except Exception as e:
                logger.error(f"Error getting prediction from {name}: {e}")
                continue
        
        if not predictions:
            logger.error("All models failed to predict!")
            return self._empty_prediction()
        
        # Calculate weighted average
        total_weight = sum(self.weights[name] for name in predictions.keys())
        combined_score = sum(scores) / total_weight
        combined_confidence = sum(confidences) / total_weight
        
        # Determine combined direction (majority vote weighted by confidence)
        direction_votes = {'UP': 0, 'DOWN': 0, 'SIDEWAYS': 0}
        for name, pred in predictions.items():
            direction = pred.get('direction', 'SIDEWAYS')
            confidence = pred.get('confidence', 0.5)
            weight = self.weights[name]
            direction_votes[direction] += confidence * weight
        
        combined_direction = max(direction_votes, key=direction_votes.get)
        
        return {
            'combined_score': int(combined_score),
            'combined_confidence': combined_confidence,
            'combined_direction': combined_direction,
            'individual_predictions': predictions,
            'models_used': list(predictions.keys()),
            'direction_votes': direction_votes
        }
    
    def get_model_stats(self):
        """Get statistics about ensemble models"""
        return {
            'total_models': len(self.models),
            'enabled_models': len(self.enabled_models),
            'models': {
                name: {
                    'enabled': name in self.enabled_models,
                    'weight': self.weights[name]
                }
                for name in self.models
            }
        }
    
    def _empty_prediction(self):
        """Return empty prediction when no models available"""
        return {
            'combined_score': 50,
            'combined_confidence': 0.33,
            'combined_direction': 'SIDEWAYS',
            'individual_predictions': {},
            'models_used': [],
            'direction_votes': {'UP': 0, 'DOWN': 0, 'SIDEWAYS': 1}
        }


if __name__ == "__main__":
    # Test ensemble
    logging.basicConfig(level=logging.INFO)
    
    print("="*60)
    print("ML ENSEMBLE TEST")
    print("="*60)
    
    # Create mock predictions for testing
    class MockModel:
        def __init__(self, name, score, direction):
            self.name = name
            self.score = score
            self.direction = direction
        
        def predict(self, X):
            return {
                'score': self.score,
                'confidence': self.score / 100,
                'direction': self.direction,
                'model': self.name
            }
    
    # Create ensemble
    ensemble = MLEnsemble()
    
    # Add models
    ensemble.add_model('xgboost', MockModel('XGBoost', 78, 'UP'), weight=1.0)
    ensemble.add_model('lstm', MockModel('LSTM', 72, 'UP'), weight=0.8, enabled=False)
    ensemble.add_model('transformer', MockModel('Transformer', 85, 'UP'), weight=1.2, enabled=False)
    
    print("\n1. Ensemble with XGBoost only:")
    pred = ensemble.predict(None)
    print(f"   Combined Score: {pred['combined_score']}")
    print(f"   Direction: {pred['combined_direction']}")
    print(f"   Models Used: {pred['models_used']}")
    
    print("\n2. Enable LSTM:")
    ensemble.enable_model('lstm')
    pred = ensemble.predict(None)
    print(f"   Combined Score: {pred['combined_score']}")
    print(f"   Direction: {pred['combined_direction']}")
    print(f"   Models Used: {pred['models_used']}")
    
    print("\n3. Enable Transformer:")
    ensemble.enable_model('transformer')
    pred = ensemble.predict(None)
    print(f"   Combined Score: {pred['combined_score']}")
    print(f"   Direction: {pred['combined_direction']}")
    print(f"   Models Used: {pred['models_used']}")
    
    print("\n4. Ensemble Stats:")
    stats = ensemble.get_model_stats()
    print(f"   Total Models: {stats['total_models']}")
    print(f"   Enabled Models: {stats['enabled_models']}")
    
    print("\n" + "="*60)
