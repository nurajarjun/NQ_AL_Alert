
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
    print("🚀 Verifying SCALP Strategy (Target > 70% WR)...")
    
    # Config: Scalping (Low Reward to Risk)
    config = {
        'rsi_short': 70,
        'rsi_long': 30,
        'atr_stop_mult': 4.0, # WIDE STOP to force high Win Rate
        'target1_ratio': 0.5, # Small Target
        'target2_ratio': 1.0,
        'use_ml': False
    }
    
    bt = Backtester(days=60, config=config)
    bt.run(verbose=True)

if __name__ == "__main__":
    verify()
