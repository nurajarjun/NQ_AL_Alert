"""
Auto-Retrainer - Continuous Learning
Automatically retrains models with new trade data
"""

import logging
from datetime import datetime, timedelta
from trade_tracker import TradeTracker
from xgboost_model import XGBoostPredictor
from feature_engineer import FeatureEngineer
from data_collector import HistoricalDataCollector

logger = logging.getLogger(__name__)

class AutoRetrainer:
    """Automatically retrains models based on performance"""
    
    def __init__(self):
        self.tracker = TradeTracker()
        self.min_trades_for_retrain = 50  # Minimum trades before retraining
        self.retrain_threshold_win_rate = 55  # Only retrain if win rate < 55%
    
    def should_retrain(self, symbol):
        """Determine if model should be retrained"""
        stats = self.tracker.get_performance_stats(symbol=symbol, days=7)
        
        if stats['total_trades'] < self.min_trades_for_retrain:
            logger.info(f"{symbol}: Not enough trades ({stats['total_trades']}/50)")
            return False
        
        if stats['win_rate'] < self.retrain_threshold_win_rate:
            logger.info(f"{symbol}: Win rate low ({stats['win_rate']:.1f}%) - RETRAIN")
            return True
        
        logger.info(f"{symbol}: Performance good ({stats['win_rate']:.1f}%) - Skip retrain")
        return False
    
    def retrain_model(self, symbol):
        """Retrain model with latest data"""
        logger.info(f"Retraining {symbol} model...")
        
        try:
            # Collect fresh data
            collector = HistoricalDataCollector()
            train_data, test_data = collector.get_data_for_training(symbol=symbol)
            
            # Engineer features
            engineer = FeatureEngineer()
            train_features = engineer.calculate_all_features(train_data)
            test_features = engineer.calculate_all_features(test_data)
            
            # Create targets
            train_features = engineer.create_target(train_features)
            test_features = engineer.create_target(test_features)
            
            # Prepare data
            X_train = train_features.drop(['Target'], axis=1)
            y_train = train_features['Target']
            X_test = test_features.drop(['Target'], axis=1)
            y_test = test_features['Target']
            
            # Train
            model = XGBoostPredictor(symbol=symbol)
            model.train(X_train, y_train, X_test, y_test)
            
            logger.info(f"✅ {symbol} model retrained successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to retrain {symbol}: {e}")
            return False
    
    def run_auto_retrain(self, symbols=['NQ', 'ES']):
        """Run auto-retrain check for all symbols"""
        logger.info("=== AUTO-RETRAIN CHECK ===")
        
        results = {}
        for symbol in symbols:
            if self.should_retrain(symbol):
                results[symbol] = self.retrain_model(symbol)
            else:
                results[symbol] = "Skipped"
        
        return results

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    
    retrainer = AutoRetrainer()
    results = retrainer.run_auto_retrain()
    
    print(f"\nRetrain Results: {results}")
