
import sys
import os

# Path setup
sys.path.append(os.getcwd())
try:
    from backend.backtest import Backtester
    from backend.ml.xgboost_model import XGBoostPredictor
except ImportError:
    sys.path.append(os.path.join(os.getcwd(), 'backend'))
    from backend.backtest import Backtester
    from ml.xgboost_model import XGBoostPredictor

def verify_focused_ml():
    print("Verifying FOCUSED ML Model (Last 60 Days)...")
    print("=" * 60)
    
    # Load focused model
    predictor = XGBoostPredictor(model_path="ml/models/xgboost_model_focused.pkl")
    
    # Config with Focused ML
    config = {
        'rsi_short': 70,
        'rsi_long': 30,
        'atr_stop_mult': 1.5,
        'target1_ratio': 1.5,
        'target2_ratio': 3.0,
        'use_ml': True,
        'ml_threshold': 0.55,  # Slightly above random
        'use_adx_filter': False,
        'ml_model_path': 'ml/models/xgboost_model_focused.pkl'
    }
    
    bt = Backtester(days=60, config=config, symbol="NQ")
    bt.run(verbose=False)
    
    print(f"\nTotal Trades (Focused ML): {len(bt.trades)}")
    
    if len(bt.trades) > 0:
        wins = sum(1 for t in bt.trades if t['pnl'] > 0)
        win_rate = (wins / len(bt.trades)) * 100
        total_pnl = sum(t['pnl'] for t in bt.trades)
    else:
        win_rate = 0
        total_pnl = 0
        
    print(f"Win Rate: {win_rate:.1f}%")
    print(f"Net Profit: {total_pnl:.2f} pts")
    print("=" * 60)
    
    # Compare to baseline
    print("\nCOMPARISON:")
    print(f"  Baseline (No ML):     +765 pts, ~21% WR")
    print(f"  Old ML (40 features): -619 pts, 16.7% WR")
    print(f"  New ML (13 features): {total_pnl:+.0f} pts, {win_rate:.1f}% WR")
    print("=" * 60)
    
    if len(bt.trades) > 0:
        print("\nTRADE LOG:")
        for t in bt.trades:
            result = "WIN" if t['pnl'] > 0 else "LOSS"
            print(f"{t['timestamp']} | {t['type']:5s} | {result:4s} | PnL: {t['pnl']:+7.2f}")

if __name__ == "__main__":
    verify_focused_ml()
