import sys
import os
sys.path.append(os.getcwd())

from backend.backtest import Backtester

config = {
    'rsi_short': 70,
    'rsi_long': 30,
    'atr_stop_mult': 1.5,
    'target1_ratio': 1.5,
    'target2_ratio': 3.0,
    'use_ml': True,
    'ml_threshold': 0.55,
    'use_adx_filter': False,
    'ml_model_path': 'ml/models/xgboost_model_focused.pkl'
}

bt = Backtester(days=60, config=config, symbol="NQ")
bt.run(verbose=False)

wins = sum(1 for t in bt.trades if t['pnl'] > 0)
total_pnl = sum(t['pnl'] for t in bt.trades)
wr = (wins/len(bt.trades)*100) if bt.trades else 0

print(f"TRADES:{len(bt.trades)} WR:{wr:.1f}% PNL:{total_pnl:.0f}")
