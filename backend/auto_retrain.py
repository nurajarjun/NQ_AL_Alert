
import os
import sys
import logging
import time
from datetime import datetime, timedelta
import asyncio

# Setup paths
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from ml.xgboost_model import XGBoostPredictor

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

MODELS_DIR = os.path.join(os.path.dirname(__file__), 'ml', 'models')
SYMBOLS = ["NQ", "ES", "TQQQ", "SQQQ", "SOXL", "SOXS"]

def needs_retraining(days_threshold=7):
    """Check if any model is older than threshold days"""
    try:
        # If directory doesn't exist, we definitely need training
        if not os.path.exists(MODELS_DIR):
            return True, "No models found"
            
        # Check specific model files
        for symbol in SYMBOLS:
            model_path = os.path.join(MODELS_DIR, f"xgboost_model_{symbol}.pkl")
            if not os.path.exists(model_path):
                return True, f"Missing model for {symbol}"
                
            # Check age
            mod_time = datetime.fromtimestamp(os.path.getmtime(model_path))
            age = datetime.now() - mod_time
            
            if age.days >= days_threshold:
                return True, f"Model {symbol} is {age.days} days old"
                
        return False, "All models are fresh"
        
    except Exception as e:
        logger.error(f"Error checking model age: {e}")
        return True, "Error checking status"

async def run_retraining():
    """Run the training script via subprocess to ensure clean state"""
    logger.info("🚀 Starting Auto-Retraining Sequence...")
    
    # We invoke the existing train_all_models.py in the root directory
    root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    script_path = os.path.join(root_dir, "train_all_models.py")
    
    cmd = f"{sys.executable} {script_path}"
    
    proc = await asyncio.create_subprocess_shell(
        cmd,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE
    )
    
    stdout, stderr = await proc.communicate()
    
    if proc.returncode == 0:
        logger.info("✅ Retraining Complete Success")
        return True, stdout.decode()
    else:
        logger.error(f"❌ Retraining Failed: {stderr.decode()}")
        return False, stderr.decode()

if __name__ == "__main__":
    is_needed, reason = needs_retraining()
    print(f"Status: {reason}")
    if is_needed:
        print("Triggering training...")
        asyncio.run(run_retraining())
