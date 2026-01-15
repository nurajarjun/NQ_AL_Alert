"""
Phase 14 Backtest Verification
Compare performance with and without Phase 14 filters over 1 year
"""
import sys
import os
sys.path.append(os.getcwd())

from backend.backtest import Backtester
import pandas as pd

print("=" * 80)
print("PHASE 14 VERIFICATION - 1 YEAR BACKTEST COMPARISON")
print("=" * 80)

# Test 1: Baseline (No Phase 14 filters)
print("\n📊 TEST 1: BASELINE (Original System)")
print("-" * 80)
config_baseline = {
    'rsi_short': 70,
    'rsi_long': 30,
    'atr_stop_mult': 1.5,
    'target1_ratio': 1.5,
    'target2_ratio': 3.0,
    'use_ml': False,
    'use_adx_filter': False,
    'use_phase14_filters': False  # Disable Phase 14
}

bt_baseline = Backtester(days=365, config=config_baseline, symbol="NQ")
bt_baseline.run(verbose=False)

baseline_trades = len(bt_baseline.trades)
baseline_wins = sum(1 for t in bt_baseline.trades if t['pnl'] > 0)
baseline_pnl = sum(t['pnl'] for t in bt_baseline.trades)
baseline_wr = (baseline_wins / baseline_trades * 100) if baseline_trades > 0 else 0

print(f"Total Trades: {baseline_trades}")
print(f"Wins: {baseline_wins} | Losses: {baseline_trades - baseline_wins}")
print(f"Win Rate: {baseline_wr:.1f}%")
print(f"Net PnL: {baseline_pnl:+.2f} pts")

# Monthly breakdown for baseline
trades_df_baseline = pd.DataFrame(bt_baseline.trades)
if not trades_df_baseline.empty:
    trades_df_baseline['month'] = pd.to_datetime(trades_df_baseline['timestamp']).dt.to_period('M')
    monthly_baseline = trades_df_baseline.groupby('month').agg({
        'pnl': ['count', 'sum', lambda x: (x > 0).sum()]
    }).round(2)
    monthly_baseline.columns = ['Trades', 'PnL', 'Wins']
    monthly_baseline['WR%'] = (monthly_baseline['Wins'] / monthly_baseline['Trades'] * 100).round(1)
    
    worst_month_baseline = monthly_baseline['PnL'].min()
    best_month_baseline = monthly_baseline['PnL'].max()
    print(f"Best Month: {best_month_baseline:+.2f} pts")
    print(f"Worst Month: {worst_month_baseline:+.2f} pts")

# Test 2: Phase 14 Enhanced (With all filters)
print("\n\n🚀 TEST 2: PHASE 14 ENHANCED (Multi-TF + Economic + Earnings)")
print("-" * 80)
config_phase14 = {
    'rsi_short': 70,
    'rsi_long': 30,
    'atr_stop_mult': 1.5,
    'target1_ratio': 1.5,
    'target2_ratio': 3.0,
    'use_ml': False,
    'use_adx_filter': False,
    'use_phase14_filters': True  # Enable Phase 14
}

bt_phase14 = Backtester(days=365, config=config_phase14, symbol="NQ")
bt_phase14.run(verbose=False)

phase14_trades = len(bt_phase14.trades)
phase14_wins = sum(1 for t in bt_phase14.trades if t['pnl'] > 0)
phase14_pnl = sum(t['pnl'] for t in bt_phase14.trades)
phase14_wr = (phase14_wins / phase14_trades * 100) if phase14_trades > 0 else 0

print(f"Total Trades: {phase14_trades}")
print(f"Wins: {phase14_wins} | Losses: {phase14_trades - phase14_wins}")
print(f"Win Rate: {phase14_wr:.1f}%")
print(f"Net PnL: {phase14_pnl:+.2f} pts")

# Monthly breakdown for Phase 14
trades_df_phase14 = pd.DataFrame(bt_phase14.trades)
if not trades_df_phase14.empty:
    trades_df_phase14['month'] = pd.to_datetime(trades_df_phase14['timestamp']).dt.to_period('M')
    monthly_phase14 = trades_df_phase14.groupby('month').agg({
        'pnl': ['count', 'sum', lambda x: (x > 0).sum()]
    }).round(2)
    monthly_phase14.columns = ['Trades', 'PnL', 'Wins']
    monthly_phase14['WR%'] = (monthly_phase14['Wins'] / monthly_phase14['Trades'] * 100).round(1)
    
    worst_month_phase14 = monthly_phase14['PnL'].min()
    best_month_phase14 = monthly_phase14['PnL'].max()
    print(f"Best Month: {best_month_phase14:+.2f} pts")
    print(f"Worst Month: {worst_month_phase14:+.2f} pts")

# Comparison Summary
print("\n\n📈 COMPARISON SUMMARY")
print("=" * 80)
print(f"{'Metric':<25} {'Baseline':<20} {'Phase 14':<20} {'Change':<15}")
print("-" * 80)

trade_reduction = ((baseline_trades - phase14_trades) / baseline_trades * 100) if baseline_trades > 0 else 0
wr_improvement = phase14_wr - baseline_wr
pnl_improvement = phase14_pnl - baseline_pnl
worst_month_improvement = worst_month_phase14 - worst_month_baseline

print(f"{'Total Trades':<25} {baseline_trades:<20} {phase14_trades:<20} {trade_reduction:+.1f}%")
print(f"{'Win Rate':<25} {baseline_wr:.1f}%{'':<15} {phase14_wr:.1f}%{'':<15} {wr_improvement:+.1f}%")
print(f"{'Net PnL':<25} {baseline_pnl:+.2f} pts{'':<10} {phase14_pnl:+.2f} pts{'':<10} {pnl_improvement:+.2f} pts")
print(f"{'Worst Month':<25} {worst_month_baseline:+.2f} pts{'':<10} {worst_month_phase14:+.2f} pts{'':<10} {worst_month_improvement:+.2f} pts")

print("\n" + "=" * 80)
print("VERDICT:")
print("=" * 80)

if phase14_wr > baseline_wr and worst_month_phase14 > worst_month_baseline:
    print("✅ PHASE 14 IMPROVED BOTH WIN RATE AND WORST MONTH")
    print(f"   - Win rate increased by {wr_improvement:.1f}%")
    print(f"   - Worst month improved by {worst_month_improvement:+.2f} pts")
    print(f"   - Trade frequency reduced by {trade_reduction:.1f}% (quality over quantity)")
elif phase14_wr > baseline_wr:
    print("⚠️  PHASE 14 IMPROVED WIN RATE BUT NOT WORST MONTH")
    print(f"   - Win rate increased by {wr_improvement:.1f}%")
    print(f"   - But worst month changed by {worst_month_improvement:+.2f} pts")
elif worst_month_phase14 > worst_month_baseline:
    print("⚠️  PHASE 14 IMPROVED WORST MONTH BUT NOT WIN RATE")
    print(f"   - Worst month improved by {worst_month_improvement:+.2f} pts")
    print(f"   - But win rate changed by {wr_improvement:+.1f}%")
else:
    print("❌ PHASE 14 DID NOT IMPROVE KEY METRICS")
    print("   - Filters may be too aggressive or need tuning")

print("\n" + "=" * 80)
