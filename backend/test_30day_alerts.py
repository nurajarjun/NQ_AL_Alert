"""
Test Last 30 Days - Daily 10 PM Alert Simulation
Simulates sending a daily alert at 10 PM and tracks next-day performance
"""
import sys
import os
sys.path.append(os.getcwd())

from backend.ml.data_collector import HistoricalDataCollector
from backend.ml.feature_engineer import FeatureEngineer
from datetime import datetime, timedelta
import pandas as pd
import numpy as np

print("=" * 80)
print("LAST 30 DAYS - DAILY 10 PM ALERT SIMULATION")
print("=" * 80)

# Load data
collector = HistoricalDataCollector()
fe = FeatureEngineer()

print("\nLoading 60 days of data (to have context)...")
end_date = datetime.now()
start_date = end_date - timedelta(days=60)
df = collector.download_nq_data(start_date=start_date, end_date=end_date)

print(f"Calculating features...")
df = fe.calculate_all_features(df)

# Calculate 4H RSI for Phase 14
print("Calculating 4H RSI for multi-timeframe analysis...")
df['RSI_4H'] = fe.calculate_4h_rsi(df)

print(f"\nLoaded {len(df)} candles")
print(f"Date range: {df.index[0]} to {df.index[-1]}")

# Simulate daily 10 PM alerts for last 30 days
print("\n" + "=" * 80)
print("SIMULATING DAILY 10 PM ALERTS (Last 30 Days)")
print("=" * 80)

alerts = []
last_30_days = end_date - timedelta(days=30)

# Find all 10 PM timestamps in last 30 days
for day_offset in range(30):
    check_date = last_30_days + timedelta(days=day_offset)
    # Set to 10 PM (22:00)
    alert_time = check_date.replace(hour=22, minute=0, second=0, microsecond=0)
    
    # Find closest candle to 10 PM
    try:
        # Get the candle at or before 10 PM
        mask = df.index <= alert_time
        if not mask.any():
            continue
            
        idx = df.index[mask][-1]
        row = df.loc[idx]
        
        # Calculate signal (RSI-based score)
        rsi = row.get('RSI', 50)
        sma_10 = row.get('SMA_10', row['Close'])
        sma_20 = row.get('SMA_20', row['Close'])
        sma_50 = row.get('SMA_50', row['Close'])
        close = row['Close']
        open_price = row['Open']
        
        # Score calculation (same as main.py)
        score = 50
        if rsi < 30: score -= 30
        elif rsi > 70: score += 30
        if close > sma_50: score += 4
        else: score -= 4
        if sma_10 > sma_20: score += 8
        else: score -= 8
        if close > open_price: score += 5
        else: score -= 5
        score = max(0, min(100, score))
        
        # Determine direction
        direction = "NEUTRAL"
        if score >= 70: direction = "SHORT"
        elif score <= 30: direction = "LONG"
        
        # Phase 14: Multi-timeframe check
        rsi_4h = row.get('RSI_4H')
        mtf_aligned = False
        if direction == "LONG" and rsi < 30 and rsi_4h < 35:
            mtf_aligned = True
        elif direction == "SHORT" and rsi > 70 and rsi_4h > 65:
            mtf_aligned = True
        
        # Apply Phase 14 filter
        if direction != "NEUTRAL" and not mtf_aligned:
            direction = "NEUTRAL"
            filtered = True
        else:
            filtered = False
        
        # Calculate next-day outcome (if signal was given)
        outcome = None
        outcome_pnl = 0
        
        if direction in ["LONG", "SHORT"]:
            # Find next 24 hours of data
            next_24h_mask = (df.index > idx) & (df.index <= idx + timedelta(hours=24))
            next_24h = df[next_24h_mask]
            
            if len(next_24h) > 0:
                entry = close
                atr = row.get('ATR', close * 0.01)
                stop_dist = atr * 1.5
                target_dist = atr * 1.5
                
                if direction == "LONG":
                    stop = entry - stop_dist
                    target = entry + target_dist
                    
                    # Check if hit target or stop
                    hit_target = (next_24h['High'] >= target).any()
                    hit_stop = (next_24h['Low'] <= stop).any()
                    
                    if hit_target and not hit_stop:
                        outcome = "WIN"
                        outcome_pnl = target_dist
                    elif hit_stop:
                        outcome = "LOSS"
                        outcome_pnl = -stop_dist
                    else:
                        outcome = "OPEN"
                        outcome_pnl = next_24h.iloc[-1]['Close'] - entry
                        
                else:  # SHORT
                    stop = entry + stop_dist
                    target = entry - target_dist
                    
                    hit_target = (next_24h['Low'] <= target).any()
                    hit_stop = (next_24h['High'] >= stop).any()
                    
                    if hit_target and not hit_stop:
                        outcome = "WIN"
                        outcome_pnl = target_dist
                    elif hit_stop:
                        outcome = "LOSS"
                        outcome_pnl = -stop_dist
                    else:
                        outcome = "OPEN"
                        outcome_pnl = entry - next_24h.iloc[-1]['Close']
        
        alerts.append({
            'date': alert_time.date(),
            'time': '10:00 PM',
            'rsi_1h': rsi,
            'rsi_4h': rsi_4h,
            'direction': direction,
            'mtf_aligned': mtf_aligned,
            'filtered': filtered,
            'outcome': outcome,
            'pnl': outcome_pnl
        })
        
    except Exception as e:
        print(f"Error processing {alert_time}: {e}")
        continue

# Display results
print(f"\nTotal Days Checked: {len(alerts)}")
print("\n" + "-" * 80)
print(f"{'Date':<12} {'RSI 1H':<8} {'RSI 4H':<8} {'Signal':<10} {'MTF':<6} {'Outcome':<8} {'PnL':<10}")
print("-" * 80)

total_signals = 0
total_wins = 0
total_losses = 0
total_pnl = 0
filtered_count = 0

for alert in alerts:
    rsi_1h_str = f"{alert['rsi_1h']:.1f}" if not pd.isna(alert['rsi_1h']) else "N/A"
    rsi_4h_str = f"{alert['rsi_4h']:.1f}" if not pd.isna(alert['rsi_4h']) else "N/A"
    mtf_str = "✓" if alert['mtf_aligned'] else "✗"
    outcome_str = alert['outcome'] if alert['outcome'] else "-"
    pnl_str = f"{alert['pnl']:+.2f}" if alert['outcome'] else "-"
    
    if alert['filtered']:
        signal_str = f"{alert['direction']} [F]"
        filtered_count += 1
    else:
        signal_str = alert['direction']
    
    print(f"{str(alert['date']):<12} {rsi_1h_str:<8} {rsi_4h_str:<8} {signal_str:<10} {mtf_str:<6} {outcome_str:<8} {pnl_str:<10}")
    
    if alert['direction'] != "NEUTRAL" and not alert['filtered']:
        total_signals += 1
        if alert['outcome'] == "WIN":
            total_wins += 1
            total_pnl += alert['pnl']
        elif alert['outcome'] == "LOSS":
            total_losses += 1
            total_pnl += alert['pnl']

# Summary
print("\n" + "=" * 80)
print("SUMMARY")
print("=" * 80)
print(f"Total Days: {len(alerts)}")
print(f"Signals Generated: {total_signals}")
print(f"Signals Filtered (Phase 14): {filtered_count}")
print(f"Neutral Days: {len(alerts) - total_signals - filtered_count}")
print()
print(f"Wins: {total_wins}")
print(f"Losses: {total_losses}")
print(f"Win Rate: {(total_wins/total_signals*100) if total_signals > 0 else 0:.1f}%")
print(f"Total PnL: {total_pnl:+.2f} pts")
print(f"Avg PnL per Signal: {(total_pnl/total_signals) if total_signals > 0 else 0:+.2f} pts")
print()
print("=" * 80)
print("INTERPRETATION:")
print("=" * 80)
if total_signals == 0:
    print("No signals in last 30 days - RSI stayed in neutral zone (30-70)")
elif total_wins / total_signals > 0.5:
    print(f"✅ Good performance: {total_wins/total_signals*100:.1f}% win rate")
    print(f"   Daily 10 PM alerts would have been profitable")
else:
    print(f"⚠️  Low win rate: {total_wins/total_signals*100:.1f}%")
    print(f"   But remember: Mean reversion needs big wins to cover small losses")
    print(f"   Total PnL: {total_pnl:+.2f} pts")
