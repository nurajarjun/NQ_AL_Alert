import yfinance as yf
import pandas as pd

print("Testing ETF Data Collection...")
print("="*60)

symbols = ['TQQQ', 'SQQQ', 'SOXL', 'SOXS']

for symbol in symbols:
    print(f"\n{symbol}:")
    try:
        # Try 6 months of hourly data
        data = yf.download(symbol, period='6mo', interval='1h', progress=False)
        print(f"  6mo hourly: {len(data)} rows")
        
        if len(data) < 100:
            # Try 3 months
            data = yf.download(symbol, period='3mo', interval='1h', progress=False)
            print(f"  3mo hourly: {len(data)} rows")
        
        if len(data) < 100:
            # Try daily data instead
            data = yf.download(symbol, period='1y', interval='1d', progress=False)
            print(f"  1y daily: {len(data)} rows")
        
        if len(data) > 0:
            print(f"  Start: {data.index[0]}")
            print(f"  End: {data.index[-1]}")
            print(f"  ✅ Data available")
        else:
            print(f"  ❌ No data")
            
    except Exception as e:
        print(f"  ❌ Error: {e}")

print("\n" + "="*60)
