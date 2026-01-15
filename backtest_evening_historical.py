"""
Proper 10-Day Evening Scalper Backtest
Samples evening hours (4-10 PM ET) from historical data
"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

import yfinance as yf
import pandas as pd
import pandas_ta as ta
from datetime import datetime, timedelta
import pytz

print("\n" + "="*80)
print("EVENING SCALPER - 10-DAY HISTORICAL BACKTEST")
print("="*80 + "\n")

# Assets (optimized list)
assets = {
    'NQ': {'symbol': 'NQ=F', 'name': 'Nasdaq Futures', 'multiplier': 20},
    'ES': {'symbol': 'ES=F', 'name': 'S&P 500 Futures', 'multiplier': 50},
    'GC': {'symbol': 'GC=F', 'name': 'Gold', 'multiplier': 100},
    'CL': {'symbol': 'CL=F', 'name': 'Crude Oil', 'multiplier': 1000},
    'EUR': {'symbol': 'EURUSD=X', 'name': 'Euro/USD', 'multiplier': 125000}
}

print(f"Testing {len(assets)} assets:")
for ticker, info in assets.items():
    print(f"  • {ticker:4} - {info['name']}")

print(f"\nPeriod: Last 10 days")
print(f"Session: 4:00 PM - 10:00 PM ET")
print(f"Sampling: Every 2 hours during session\n")

all_signals = []
et_tz = pytz.timezone('US/Eastern')

# Test each asset
for ticker, info in assets.items():
    print(f"\n{'='*80}")
    print(f"Testing {ticker} - {info['name']}")
    print(f"{'='*80}\n")
    
    try:
        # Get 10 days of 5-min data
        stock = yf.Ticker(info['symbol'])
        df = stock.history(period="10d", interval="5m")
        
        if len(df) < 100:
            print(f"  ❌ Insufficient data ({len(df)} candles)\n")
            continue
        
        print(f"  ✅ Downloaded {len(df)} candles")
        
        # Convert to ET
        df.index = df.index.tz_convert(et_tz)
        
        # Filter for evening hours (16:00 - 22:00 ET)
        df['hour'] = df.index.hour
        evening_df = df[(df['hour'] >= 16) & (df['hour'] < 22)]
        
        print(f"  ✅ Evening candles: {len(evening_df)}")
        
        if len(evening_df) < 50:
            print(f"  ❌ Insufficient evening data\n")
            continue
        
        # Calculate indicators on evening data
        evening_df.ta.adx(length=14, append=True)
        evening_df.ta.bbands(length=20, std=2, append=True)
        evening_df.ta.rsi(length=14, append=True)
        evening_df.ta.atr(length=14, append=True)
        evening_df['VOL_SMA'] = evening_df['Volume'].rolling(20).mean()
        
        # Sample every 2 hours during evening session
        # Hours: 16, 18, 20 (4 PM, 6 PM, 8 PM)
        sample_hours = [16, 18, 20]
        
        signals_found = 0
        
        for hour in sample_hours:
            hour_df = evening_df[evening_df['hour'] == hour]
            
            if len(hour_df) == 0:
                continue
            
            # Take last candle from each hour
            for date in hour_df.index.date:
                day_hour_df = hour_df[hour_df.index.date == date]
                
                if len(day_hour_df) == 0:
                    continue
                
                last = day_hour_df.iloc[-1]
                
                # Check for signals
                price = last['Close']
                adx = last.get('ADX_14', 0)
                rsi = last.get('RSI_14', 50)
                atr = last.get('ATRr_14', 0)
                vol_ratio = last['Volume'] / last.get('VOL_SMA', 1) if last.get('VOL_SMA', 1) > 0 else 0
                upper_band = last.get('BBU_20_2.0', price)
                lower_band = last.get('BBL_20_2.0', price)
                middle_band = last.get('BBM_20_2.0', price)
                
                signal = None
                strategy = ""
                
                # Strategy 1: Breakout
                if vol_ratio > 1.5 and adx > 25:
                    if price > upper_band:
                        signal = "LONG"
                        strategy = "🚀 Breakout"
                    elif price < lower_band:
                        signal = "SHORT"
                        strategy = "🔻 Breakout"
                
                # Strategy 2: Mean Reversion
                elif adx < 20:
                    if rsi < 30 and price <= lower_band:
                        signal = "LONG"
                        strategy = "🔄 Mean Reversion"
                    elif rsi > 70 and price >= upper_band:
                        signal = "SHORT"
                        strategy = "🔄 Mean Reversion"
                
                # Strategy 3: Momentum
                elif 20 <= adx <= 30 and vol_ratio > 1.2:
                    if rsi > 55 and price > middle_band:
                        signal = "LONG"
                        strategy = "📈 Momentum"
                    elif rsi < 45 and price < middle_band:
                        signal = "SHORT"
                        strategy = "📉 Momentum"
                
                if signal:
                    signals_found += 1
                    
                    # Calculate trade setup
                    if signal == "LONG":
                        entry = price
                        stop = price - (atr * 1.5)
                        target1 = price + (atr * 2)
                        target2 = price + (atr * 4)
                    else:
                        entry = price
                        stop = price + (atr * 1.5)
                        target1 = price - (atr * 2)
                        target2 = price - (atr * 4)
                    
                    risk = abs(entry - stop)
                    reward1 = abs(target1 - entry)
                    
                    all_signals.append({
                        'date': last.name.strftime('%Y-%m-%d %H:%M'),
                        'ticker': ticker,
                        'name': info['name'],
                        'signal': signal,
                        'strategy': strategy,
                        'entry': entry,
                        'stop': stop,
                        'target1': target1,
                        'risk_dollars': risk * info['multiplier'],
                        'reward_dollars': reward1 * info['multiplier'],
                        'rr_ratio': reward1 / risk if risk > 0 else 0,
                        'rsi': rsi,
                        'adx': adx
                    })
        
        print(f"  ✅ Signals found: {signals_found}\n")
        
    except Exception as e:
        print(f"  ❌ Error: {e}\n")

# Summary
print("\n" + "="*80)
print("BACKTEST RESULTS")
print("="*80 + "\n")

if len(all_signals) == 0:
    print("❌ No signals found")
    print("\nPossible reasons:")
    print("  • Market conditions didn't meet strategy criteria")
    print("  • Low volatility period")
    print("  • Need to adjust strategy thresholds")
else:
    df_signals = pd.DataFrame(all_signals)
    
    print(f"Total Signals: {len(all_signals)}")
    print(f"\nBy Asset:")
    print(df_signals.groupby('ticker').size().to_string())
    
    print(f"\nBy Strategy:")
    print(df_signals.groupby('strategy').size().to_string())
    
    print(f"\nBy Direction:")
    print(df_signals.groupby('signal').size().to_string())
    
    total_risk = df_signals['risk_dollars'].sum()
    total_reward = df_signals['reward_dollars'].sum()
    avg_rr = df_signals['rr_ratio'].mean()
    
    print(f"\nRisk/Reward:")
    print(f"  Total Risk: ${total_risk:,.0f}")
    print(f"  Total Reward: ${total_reward:,.0f}")
    print(f"  Avg R/R Ratio: {avg_rr:.2f}:1")
    
    print(f"\nSample Signals:")
    print(df_signals.head(10).to_string(index=False))

print("\n" + "="*80 + "\n")
