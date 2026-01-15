
import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta

print(f"Pandas version: {pd.__version__}")
print(f"yfinance version: {yf.__version__}")

end_date = datetime.now()
start_date = end_date - timedelta(days=729) # Try 729 days to be safe

tickers = ["NQ=F", "^NDX", "QQQ"]

for ticker in tickers:
    print(f"\nTesting ticker: {ticker} (1h interval, 729 days)")
    try:
        data = yf.download(ticker, start=start_date, end=end_date, interval="1h", progress=False)
        print(f"Data shape: {data.shape}")
        if data.empty:
            print("Data is empty!")
        else:
            print("Columns:", data.columns)
            print(data.head(2))
    except Exception as e:
        print(f"Error downloading {ticker}: {e}")
