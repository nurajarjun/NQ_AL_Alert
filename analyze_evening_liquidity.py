"""
Analyze evening scalper assets for volume and liquidity
"""
import yfinance as yf
import pandas as pd
from datetime import datetime

assets = {
    'NQ': {'symbol': 'NQ=F', 'name': 'Nasdaq Futures'},
    'ES': {'symbol': 'ES=F', 'name': 'S&P 500 Futures'},
    'NKD': {'symbol': 'NKD=F', 'name': 'Nikkei 225'},
    'GC': {'symbol': 'GC=F', 'name': 'Gold'},
    'SI': {'symbol': 'SI=F', 'name': 'Silver'},
    'HG': {'symbol': 'HG=F', 'name': 'Copper'},
    'CL': {'symbol': 'CL=F', 'name': 'Crude Oil'},
    'NG': {'symbol': 'NG=F', 'name': 'Natural Gas'},
    'JPY': {'symbol': 'JPY=X', 'name': 'Japanese Yen'},
    'EUR': {'symbol': 'EURUSD=X', 'name': 'Euro/USD'}
}

print("\n" + "="*80)
print("EVENING SCALPER - LIQUIDITY ANALYSIS")
print("="*80 + "\n")

results = []

for ticker, info in assets.items():
    try:
        print(f"Analyzing {info['name']} ({ticker})...")
        stock = yf.Ticker(info['symbol'])
        
        # Get 5-day 5-min data
        df = stock.history(period="5d", interval="5m")
        
        if len(df) == 0:
            print(f"  ❌ NO DATA\n")
            results.append({
                'Ticker': ticker,
                'Name': info['name'],
                'Candles': 0,
                'Avg_Volume': 0,
                'Avg_Spread_%': 0,
                'Tradeable': '❌ NO'
            })
            continue
        
        # Calculate metrics
        avg_volume = df['Volume'].mean()
        avg_spread_pct = ((df['High'] - df['Low']) / df['Close'] * 100).mean()
        
        # Determine if tradeable
        # Criteria: Avg volume > 100 AND has recent data
        is_tradeable = avg_volume > 100 and len(df) > 100
        
        results.append({
            'Ticker': ticker,
            'Name': info['name'],
            'Candles': len(df),
            'Avg_Volume': int(avg_volume),
            'Avg_Spread_%': round(avg_spread_pct, 3),
            'Tradeable': '✅ YES' if is_tradeable else '❌ NO'
        })
        
        print(f"  Candles: {len(df)}")
        print(f"  Avg Volume: {int(avg_volume)}")
        print(f"  Avg Spread: {avg_spread_pct:.3f}%")
        print(f"  Tradeable: {'✅ YES' if is_tradeable else '❌ NO'}\n")
        
    except Exception as e:
        print(f"  ❌ ERROR: {e}\n")
        results.append({
            'Ticker': ticker,
            'Name': info['name'],
            'Candles': 0,
            'Avg_Volume': 0,
            'Avg_Spread_%': 0,
            'Tradeable': '❌ NO'
        })

# Create summary table
df_results = pd.DataFrame(results)
df_results = df_results.sort_values('Avg_Volume', ascending=False)

print("\n" + "="*80)
print("SUMMARY - SORTED BY VOLUME")
print("="*80 + "\n")
print(df_results.to_string(index=False))

# Recommendations
print("\n" + "="*80)
print("RECOMMENDATIONS")
print("="*80 + "\n")

tradeable = df_results[df_results['Tradeable'] == '✅ YES']
not_tradeable = df_results[df_results['Tradeable'] == '❌ NO']

print(f"✅ KEEP THESE ({len(tradeable)} assets):")
for _, row in tradeable.iterrows():
    print(f"  • {row['Ticker']:4} - {row['Name']:25} (Vol: {row['Avg_Volume']:,})")

print(f"\n❌ REMOVE THESE ({len(not_tradeable)} assets):")
for _, row in not_tradeable.iterrows():
    print(f"  • {row['Ticker']:4} - {row['Name']:25} (Vol: {row['Avg_Volume']:,})")

print("\n" + "="*80)
