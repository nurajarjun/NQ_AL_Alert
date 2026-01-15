
import sys
import os

# Path setup
sys.path.append(os.getcwd())
try:
    from backend.backtest import Backtester
except ImportError:
    sys.path.append(os.path.join(os.getcwd(), 'backend'))
    from backend.backtest import Backtester

def verify_ml_precision():
    print("Verifying ML Precision (Last 60 Days)...")
    
    # Config with ML Enabled
    config = {
        'rsi_short': 70,
        'rsi_long': 30,
        'atr_stop_mult': 1.5,
        'target1_ratio': 1.5,
        'target2_ratio': 3.0,
        'use_ml': True,
        'ml_threshold': 0.51, # Just above random
        'use_adx_filter': False 
    }
    
    bt = Backtester(days=60, config=config, symbol="NQ")
    bt.run(verbose=False)
    
    print(f"\nTotal Trades (ML Filtered): {len(bt.trades)}")
    
    if len(bt.trades) > 0:
        wins = sum(1 for t in bt.trades if t['pnl'] > 0)
        win_rate = (wins / len(bt.trades)) * 100
        total_pnl = sum(t['pnl'] for t in bt.trades)
    else:
        win_rate = 0
        total_pnl = 0
        
    print(f"Win Rate: {win_rate:.1f}%")
    print(f"Net Profit: {total_pnl:.2f} pts")
    
    print("\nTRADE LOG:")
    for t in bt.trades:
        print(f"{t['timestamp']} | {t['type']} | PnL: {t['pnl']:.2f} | Conf: {t.get('ml_score', 'N/A')}")

if __name__ == "__main__":
    verify_ml_precision()
