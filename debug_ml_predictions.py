
import sys
import os
import pandas as pd
import logging
from backend.ml.data_collector import HistoricalDataCollector
from backend.ml.feature_engineer import FeatureEngineer
from backend.ml.xgboost_model import XGBoostPredictor

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("DEBUG_ML")

def debug_ml():
    print("="*60)
    print("DEBUGGING ML PREDICTIONS (LAST 5 DAYS)")
    print("="*60)
    
    # 1. Load Data
    collector = HistoricalDataCollector()
    df = collector.download_nq_data()
    
    # 2. Features
    fe = FeatureEngineer()
    df = fe.calculate_all_features(df)
    
    # Filter last 5 days
    cutoff = pd.Timestamp.now(tz=df.index.tz) - pd.Timedelta(days=5)
    df_recent = df[df.index >= cutoff]
    
    print(f"Loaded {len(df_recent)} candles from {cutoff}")
    
    # 3. Load Model
    try:
        predictor = XGBoostPredictor(symbol="NQ")
        if not predictor.is_trained:
            print("ERROR: ML Model not trained!")
            return
    except Exception as e:
        print(f"ERROR Loading Model: {e}")
        return

    print(f"Model Loaded: {predictor.model_path}")
    
    # 4. Predict
    results = []
    
    for i in range(len(df_recent)):
        row = df_recent.iloc[i]
        timestamp = row.name
        
        # Prepare features
        try:
            # Reconstruct feature dict
            # In live usage we pass a dict, but predictor can take array
            # Let's use the predictor's feature_names to extract correct columns
            cols = predictor.feature_names
            if not cols:
                print("Model has no feature names!")
                break
                
            X = row[cols].values.reshape(1, -1)
            pred = predictor.predict(X)
            
            results.append({
                'Time': timestamp,
                'Direction': pred['direction'],
                'Conf': pred['confidence'],
                'Side%': pred['probabilities']['sideways'],
                'Down%': pred['probabilities']['down'],
                'Up%': pred['probabilities']['up']
            })
            
        except Exception as e:
            print(f"Prediction failed at {timestamp}: {e}")
            
    # 5. Report
    print("\nPrediction Distribution:")
    df_res = pd.DataFrame(results)
    print(df_res['Direction'].value_counts())
    
    print("\nDetailed Log (Last 20 Candles):")
    print(f"{'Time':<25} {'Dir':<10} {'Conf':<6} {'Side%':<6} {'Down%':<6} {'Up%':<6}")
    print("-" * 70)
    
    for res in results[-20:]:
        print(f"{str(res['Time']):<25} {res['Direction']:<10} {res['Conf']:.2f}   {res['Side%']:.2f}   {res['Down%']:.2f}   {res['Down%']:.2f}")

    print("\nAnalysing Confidence Levels:")
    print(f"Avg Confidence: {df_res['Conf'].mean():.2f}")
    print(f"Max Confidence: {df_res['Conf'].max():.2f}")
    print(f"Min Confidence: {df_res['Conf'].min():.2f}")

if __name__ == "__main__":
    debug_ml()
