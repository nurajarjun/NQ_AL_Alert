from backend.ml.data_collector import HistoricalDataCollector
import pandas as pd

collector = HistoricalDataCollector()
print("Downloading TQQQ data...")
df = collector.download_nq_data(symbol="TQQQ")

print(f"\nIndex Type: {type(df.index)}")
print(f"Index values head: {df.index[:5]}")
print(f"Index values tail: {df.index[-5:]}")

if len(df) > 1:
    try:
        diff = df.index[1] - df.index[0]
        print(f"Diff type: {type(diff)}")
        print(f"Diff: {diff}")
        if hasattr(diff, 'total_seconds'):
            print(f"Total Seconds: {diff.total_seconds()}")
        else:
            print("Diff has no total_seconds")
    except Exception as e:
        print(f"Error calculating diff: {e}")
