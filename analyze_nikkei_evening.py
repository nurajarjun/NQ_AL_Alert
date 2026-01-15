"""
Analyze Nikkei volume specifically during evening hours (8-10 PM ET)
when Tokyo market is actually open
"""
import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta
import pytz

print("\n" + "="*80)
print("NIKKEI VOLUME ANALYSIS - EVENING HOURS (8-10 PM ET)")
print("="*80 + "\n")

# Get Nikkei data
nkd = yf.Ticker('NKD=F')
df = nkd.history(period="5d", interval="5m")

if len(df) == 0:
    print("❌ No Nikkei data available")
    exit()

print(f"Total candles: {len(df)}")
print(f"Date range: {df.index[0]} to {df.index[-1]}\n")

# Convert to ET timezone
et_tz = pytz.timezone('US/Eastern')
df.index = df.index.tz_convert(et_tz)

# Filter for evening hours (8 PM - 10 PM ET)
df['hour'] = df.index.hour
evening_df = df[(df['hour'] >= 20) & (df['hour'] < 22)]

print(f"Evening candles (8-10 PM ET): {len(evening_df)}")

if len(evening_df) > 0:
    print(f"\nEVENING HOURS STATS:")
    print(f"  Avg Volume: {evening_df['Volume'].mean():.0f}")
    print(f"  Max Volume: {evening_df['Volume'].max():.0f}")
    print(f"  Min Volume: {evening_df['Volume'].min():.0f}")
    print(f"  Avg Spread: {((evening_df['High'] - evening_df['Low']) / evening_df['Close'] * 100).mean():.3f}%")
    
    # Compare to all-day average
    all_day_avg = df['Volume'].mean()
    print(f"\nCOMPARISON:")
    print(f"  All-day avg volume: {all_day_avg:.0f}")
    print(f"  Evening avg volume: {evening_df['Volume'].mean():.0f}")
    print(f"  Evening vs All-day: {(evening_df['Volume'].mean() / all_day_avg * 100):.1f}%")
    
    # Check if tradeable
    evening_avg = evening_df['Volume'].mean()
    if evening_avg > 500:
        print(f"\n✅ VERDICT: TRADEABLE (Evening volume: {evening_avg:.0f})")
    elif evening_avg > 100:
        print(f"\n⚠️ VERDICT: MARGINAL (Evening volume: {evening_avg:.0f})")
    else:
        print(f"\n❌ VERDICT: NOT TRADEABLE (Evening volume: {evening_avg:.0f})")
else:
    print("\n❌ No evening data available")

# Show hourly breakdown
print("\n" + "="*80)
print("HOURLY VOLUME BREAKDOWN (ET)")
print("="*80 + "\n")

hourly = df.groupby('hour')['Volume'].agg(['mean', 'count'])
hourly = hourly.sort_index()
print(hourly.to_string())

print("\n" + "="*80)
