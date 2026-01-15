
import sys
import os

# Path setup
sys.path.append(os.getcwd())
try:
    from backend.backtest import Backtester
except ImportError:
    sys.path.append(os.path.join(os.getcwd(), 'backend'))
    from backend.backtest import Backtester

def verify_30_days():
    print("Verifying Deployed Strategy (Last 30 Days)...")
    
    # +765 PnL Config WITH RSI 70/30 Tweak (DEPLOYED)
    config = {
        'rsi_short': 70,
        'rsi_long': 30,
        'atr_stop_mult': 1.5,
        'target1_ratio': 1.5,
        'target2_ratio': 3.0,
        'use_ml': False,
        'use_adx_filter': False
    }
    
    # Days = 30
    bt = Backtester(days=30, config=config, symbol="NQ")
    bt.run(verbose=False)
    
    print("\nTRADE LOG (Last 30 Days):")
    for t in bt.trades:
        print(f"{t['timestamp']} | {t['type']} | PnL: {t['pnl']:.2f}")

if __name__ == "__main__":
    verify_30_days()
