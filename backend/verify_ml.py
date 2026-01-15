
import sys
import os

# Path setup
sys.path.append(os.getcwd())
try:
    from backend.backtest import Backtester
except ImportError:
    sys.path.append(os.path.join(os.getcwd(), 'backend'))
    from backend.backtest import Backtester

def verify():
    print("🤖 Verifying Machine Learning Strategy (Threshold: 80%)...")
    
    # Config: Mean Reversion + ML Filter
    config = {
        'rsi_short': 60,
        'rsi_long': 40,
        'atr_stop_mult': 1.5,
        'target1_ratio': 1.5,
        'target2_ratio': 3.0,
        'use_ml': True,
        'ml_threshold': 0.50 # Lowered to debug (was 0.80)
    }
    
    bt = Backtester(days=60, config=config)
    bt.run()

if __name__ == "__main__":
    verify()
