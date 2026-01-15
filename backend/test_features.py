
import sys
import os
import pandas as pd
import yfinance as yf

# Add root to path
sys.path.append(os.getcwd())

try:
    from backend.ml.feature_engineer import FeatureEngineer
except ImportError:
    print("Import failed, trying relative")
    sys.path.append(os.path.join(os.getcwd(), 'backend'))
    from ml.feature_engineer import FeatureEngineer

def test():
    print("Testing Feature Engineer...")
    
    # Get small amount of data
    print("Downloading data...")
    ticker = yf.Ticker("NQ=F")
    df = ticker.history(period="1y", interval="1d")
    
    if df.empty:
        print("No data found!")
        return

    print(f"Data shape: {df.shape}")
    
    fe = FeatureEngineer()
    try:
        df_features = fe.calculate_all_features(df)
        print("Features calculated.")
        
        last_row = df_features.iloc[-1]
        
        cols = df_features.columns.tolist()
        print(f"Total Columns: {len(cols)}")
        
        if 'EMA_21' in cols:
            print("✅ EMA_21 FOUND!")
            print(f"EMA_21 Value: {last_row['EMA_21']}")
            print(f"Close: {last_row['Close']}")
            if last_row['Close'] > last_row['EMA_21']:
                 print("Trend: UP")
            else:
                 print("Trend: DOWN")
        else:
            print("❌ EMA_21 NOT FOUND in columns!")
            print("Columns:", cols)
            
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test()
