"""
ML Helper Functions
Converts TradingView signals to ML features
"""

import numpy as np
import logging

logger = logging.getLogger(__name__)


def signal_to_ml_features(signal_data, feature_engineer):
    """
    Convert TradingView signal to ML feature vector
    
    Args:
        signal_data: Dict with signal data (entry, stop, rsi, atr, etc.)
        feature_engineer: FeatureEngineer instance
        
    Returns:
        Feature vector for ML prediction
    """
    try:
        # Extract signal features
        entry = signal_data.get('entry', 0)
        stop = signal_data.get('stop', 0)
        target1 = signal_data.get('target1', 0)
        target2 = signal_data.get('target2', 0)
        rsi = signal_data.get('rsi', 50)
        atr = signal_data.get('atr', 40)
        volume_ratio = signal_data.get('volume_ratio', 1.0)
        
        # Calculate derived features
        risk = abs(entry - stop)
        reward1 = abs(target1 - entry)
        reward2 = abs(target2 - entry)
        rr1 = reward1 / risk if risk > 0 else 0
        rr2 = reward2 / risk if risk > 0 else 0
        
        # Create feature dictionary matching training features
        # Note: We only have limited features from TradingView
        # The model will use what's available and default the rest
        features = {
            'RSI': rsi,
            'ATR': atr,
            'ATR_Pct': atr / entry if entry > 0 else 0,
            'Volume_Ratio': volume_ratio,
            'Price_Change': 0,  # Not available from signal
            'Price_Range': risk / entry if entry > 0 else 0,
            
            # Trend indicators (not available, use defaults)
            'SMA_10': entry,
            'SMA_20': entry,
            'SMA_50': entry,
            'EMA_12': entry,
            'EMA_26': entry,
            'Price_vs_SMA20': 0,
            'Price_vs_SMA50': 0,
            'SMA_10_20_Cross': 1 if signal_data.get('direction') == 'LONG' else 0,
            'EMA_12_26_Cross': 1 if signal_data.get('direction') == 'LONG' else 0,
            
            # Momentum (partial)
            'MACD': 0,
            'MACD_Signal': 0,
            'MACD_Hist': 0,
            'ROC_10': 0,
            'ROC_20': 0,
            'Momentum_10': 0,
            
            # Volatility
            'BB_Middle': entry,
            'BB_Upper': entry + (atr * 2),
            'BB_Lower': entry - (atr * 2),
            'BB_Width': (atr * 4) / entry if entry > 0 else 0,
            'BB_Position': 0.5,
            'Volatility_10': 0.01,
            'Volatility_20': 0.01,
            
            # Volume
            'Volume_SMA_20': 100000,
            'OBV': 0,
            'OBV_SMA': 0,
            'VPT': 0,
            
            # Patterns
            'Higher_High': 1 if signal_data.get('direction') == 'LONG' else 0,
            'Lower_Low': 1 if signal_data.get('direction') == 'SHORT' else 0,
            'Uptrend_Strength': 5 if signal_data.get('direction') == 'LONG' else 2,
            'Downtrend_Strength': 5 if signal_data.get('direction') == 'SHORT' else 2,
            'Gap_Up': 0,
            'Gap_Down': 0,
            
            # Time features (use current time)
            'Hour': 10,  # Default to morning session
            'DayOfWeek': 2,  # Wednesday
            'DayOfMonth': 15,
            'Month': 12,
            'Is_Morning': 1,
            'Is_Afternoon': 0,
            'Is_Lunch': 0,
            
            # Additional
            'Body_Size': 0.005,
            'Upper_Shadow': 0.002,
            'Lower_Shadow': 0.002,
        }
        
        # If feature engineer has feature names, use them
        if hasattr(feature_engineer, 'feature_names') and feature_engineer.feature_names:
            # Create feature vector in correct order
            feature_vector = np.array([
                features.get(name, 0) for name in feature_engineer.feature_names
            ])
        else:
            # Use all features as array
            feature_vector = np.array(list(features.values()))
        
        return feature_vector
        
    except Exception as e:
        logger.error(f"Error converting signal to ML features: {e}")
        # Return default feature vector
        return np.zeros(50)  # Default size


def format_ml_prediction(ml_prediction):
    """
    Format ML prediction for display in alerts
    
    Args:
        ml_prediction: Dict from ML ensemble
        
    Returns:
        Formatted string for alert
    """
    if not ml_prediction or 'combined_score' not in ml_prediction:
        return "ML prediction not available"
    
    score = ml_prediction['combined_score']
    direction = ml_prediction.get('combined_direction', 'SIDEWAYS')
    confidence = ml_prediction.get('combined_confidence', 0.5)
    
    # Get individual model predictions
    individual = ml_prediction.get('individual_predictions', {})
    
    text = f"""🤖 ML PREDICTION
Direction: {direction} ({confidence*100:.0f}% confidence)
Score: {score}/100

"""
    
    # Add individual model predictions
    if individual:
        text += "Model Predictions:\n"
        for model_name, pred in individual.items():
            model_dir = pred.get('direction', 'N/A')
            model_conf = pred.get('confidence', 0) * 100
            text += f"  • {model_name.upper()}: {model_dir} ({model_conf:.0f}%)\n"
    
    return text.strip()
