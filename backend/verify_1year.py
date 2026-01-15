import sys
import os
sys.path.append(os.getcwd())

from backend.backtest import Backtester

print("Testing Simple RSI 70/30 Logic - 1 YEAR Backtest")
print("=" * 60)

config = {
    'rsi_short': 70,
    'rsi_long': 30,
    'atr_stop_mult': 1.5,
    'target1_ratio': 1.5,
    'target2_ratio': 3.0,
    'use_ml': False,
    'use_adx_filter': False
}

bt = Backtester(days=365, config=config, symbol="NQ")
bt.run(verbose=False)

wins = sum(1 for t in bt.trades if t['pnl'] > 0)
losses = len(bt.trades) - wins
total_pnl = sum(t['pnl'] for t in bt.trades)
wr = (wins/len(bt.trades)*100) if bt.trades else 0
avg_win = sum(t['pnl'] for t in bt.trades if t['pnl'] > 0) / wins if wins else 0
avg_loss = sum(t['pnl'] for t in bt.trades if t['pnl'] < 0) / losses if losses else 0

print(f"\nRESULTS (365 Days):")
print(f"  Total Trades: {len(bt.trades)}")
print(f"  Wins: {wins} | Losses: {losses}")
print(f"  Win Rate: {wr:.1f}%")
print(f"  Net PnL: {total_pnl:+.2f} points")
print(f"  Avg Win: {avg_win:+.2f} pts")
print(f"  Avg Loss: {avg_loss:+.2f} pts")
print(f"  Profit Factor: {abs(avg_win/avg_loss):.2f}x" if avg_loss != 0 else "N/A")
print("=" * 60)

# Monthly breakdown
print("\nMONTHLY BREAKDOWN:")
import pandas as pd
trades_df = pd.DataFrame(bt.trades)
if not trades_df.empty:
    trades_df['month'] = pd.to_datetime(trades_df['timestamp']).dt.to_period('M')
    monthly = trades_df.groupby('month').agg({
        'pnl': ['count', 'sum', lambda x: (x > 0).sum()]
    }).round(2)
    monthly.columns = ['Trades', 'PnL', 'Wins']
    monthly['WR%'] = (monthly['Wins'] / monthly['Trades'] * 100).round(1)
    print(monthly.to_string())
