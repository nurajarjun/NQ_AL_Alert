
import yfinance as yf
import pandas as pd
from datetime import datetime
import pytz

def verify_feeds():
    # Symbols: Nikkei 225, Gold, Copper, Crude Oil, JPY/USD
    symbols = {
        'Nikkei Index (Cash)': '^N225',
        'Nikkei Futures (CME)': 'NKD=F',
        'Nikkei Futures (Osaka)': 'NIY=F',
        'Gold': 'GC=F', 
        'Copper': 'HG=F', 
        'Crude Oil': 'CL=F', 
        'JPY/USD': 'JPY=X'
    }
    
    print(f"--- Asian Session Data Check ({datetime.now().strftime('%H:%M:%S')}) ---\n")
    
    results = []
    
    for name, ticker in symbols.items():
        try:
            print(f"Checking {name} ({ticker})...")
            # Get data for today
            stock = yf.Ticker(ticker)
            
            # Fetch last 1 day, 5m interval to see if it's active "light now"
            df = stock.history(period="1d", interval="5m")
            
            if df.empty:
                status = "NO DATA"
                last_price = 0
                volume = 0
                last_time = "N/A"
            else:
                last_row = df.iloc[-1]
                last_price = last_row['Close']
                volume = last_row['Volume']
                # Convert active time to ET
                last_time = df.index[-1].strftime('%H:%M ET')
                status = "LIVE"
            
            results.append({
                'Asset': name,
                'Symbol': ticker,
                'Status': status,
                'Price': last_price,
                'Last Time': last_time,
                'Volume (5m)': volume
            })
            
        except Exception as e:
            print(f"Error fetching {ticker}: {e}")
            results.append({'Asset': name, 'Symbol': ticker, 'Status': f"ERROR: {e}"})

    # Print Report
    print("\n" + "="*80)
    print(f"{'ASSET':<15} {'SYMBOL':<10} {'STATUS':<10} {'PRICE':<15} {'TIME (ET)':<15} {'VOL (5m)':<15}")
    print("="*80)
    
    for r in results:
        print(f"{r.get('Asset'):<15} {r.get('Symbol'):<10} {r.get('Status'):<10} {r.get('Price',0):<15.2f} {r.get('Last Time'):<15} {r.get('Volume (5m)',0):<15}")

if __name__ == "__main__":
    verify_feeds()
