"""
ML Model Verification Script
Verifies that all trained models load correctly and contain institutional features
"""

import os
import sys
import pickle
import logging
from pathlib import Path

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent / 'backend'))

def verify_model(model_path, symbol):
    """Verify a single model file"""
    logger.info(f"\n{'='*60}")
    logger.info(f"Verifying {symbol} Model")
    logger.info(f"{'='*60}")
    
    if not os.path.exists(model_path):
        logger.error(f"❌ Model file not found: {model_path}")
        return False
    
    file_size = os.path.getsize(model_path) / 1024  # KB
    logger.info(f"📁 File: {os.path.basename(model_path)}")
    logger.info(f"📊 Size: {file_size:.2f} KB")
    
    try:
        # Load the model
        with open(model_path, 'rb') as f:
            model = pickle.load(f)
        
        logger.info(f"✅ Model loaded successfully")
        
        # Check model type
        model_type = type(model).__name__
        logger.info(f"🔧 Type: {model_type}")
        
        # Try to get feature names
        feature_names = None
        if hasattr(model, 'feature_names_in_'):
            feature_names = model.feature_names_in_
        elif hasattr(model, 'get_booster'):
            # XGBoost model
            try:
                feature_names = model.get_booster().feature_names
            except:
                pass
        
        if feature_names is not None:
            logger.info(f"📈 Features: {len(feature_names)} total")
            
            # Check for institutional features
            institutional_features = [
                'EMA_20_60m',
                'Distance_from_EMA60m',
                'FVG_Bullish',
                'FVG_Bearish',
                'FVG_Strength',
                'Is_First_Hour',
                'Time_Since_Open',
                'Gap_Type',
                'Gap_Size_Pct'
            ]
            
            found_institutional = [f for f in institutional_features if f in feature_names]
            
            if found_institutional:
                logger.info(f"✅ Institutional Features Found: {len(found_institutional)}/{len(institutional_features)}")
                for feat in found_institutional:
                    logger.info(f"   • {feat}")
            else:
                logger.warning(f"⚠️  No institutional features found!")
                logger.info(f"   First 10 features: {list(feature_names[:10])}")
        else:
            logger.warning(f"⚠️  Could not extract feature names")
        
        # Check model attributes
        if hasattr(model, 'n_estimators'):
            logger.info(f"🌲 Trees: {model.n_estimators}")
        if hasattr(model, 'max_depth'):
            logger.info(f"📏 Max Depth: {model.max_depth}")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Error loading model: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Main verification function"""
    logger.info("="*60)
    logger.info("NQ AI Alert System - ML Model Verification")
    logger.info("="*60)
    
    models_dir = Path(__file__).parent / 'ml' / 'models'
    
    if not models_dir.exists():
        logger.error(f"❌ Models directory not found: {models_dir}")
        return
    
    logger.info(f"📂 Models Directory: {models_dir}")
    
    # Define models to check
    models_to_check = {
        'NQ': 'xgboost_model_NQ.pkl',
        'ES': 'xgboost_model_ES.pkl',
        'TQQQ': 'xgboost_model_TQQQ.pkl',
        'SQQQ': 'xgboost_model_SQQQ.pkl',
        'SOXL': 'xgboost_model_SOXL.pkl',
        'SOXS': 'xgboost_model_SOXS.pkl',
    }
    
    results = {}
    for symbol, filename in models_to_check.items():
        model_path = models_dir / filename
        results[symbol] = verify_model(model_path, symbol)
    
    # Summary
    logger.info(f"\n{'='*60}")
    logger.info("VERIFICATION SUMMARY")
    logger.info(f"{'='*60}")
    
    successful = sum(1 for v in results.values() if v)
    total = len(results)
    
    for symbol, success in results.items():
        status = "✅ PASS" if success else "❌ FAIL"
        logger.info(f"{symbol:6s}: {status}")
    
    logger.info(f"\nTotal: {successful}/{total} models verified successfully")
    
    if successful == total:
        logger.info("\n🎉 All models verified! System ready for deployment.")
    else:
        logger.warning(f"\n⚠️  {total - successful} model(s) failed verification")

if __name__ == "__main__":
    main()
