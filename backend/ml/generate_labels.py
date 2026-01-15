
import sys
import os
import pandas as pd
import numpy as np
import logging

# Path setup
sys.path.append(os.getcwd())
try:
    from backend.ml.data_collector import HistoricalDataCollector
    from backend.ml.feature_engineer import FeatureEngineer
    from backend.analysis.trade_calculator import TradeCalculator
except ImportError:
    sys.path.append(os.path.join(os.getcwd(), 'backend'))
    from ml.data_collector import HistoricalDataCollector
    from ml.feature_engineer import FeatureEngineer
    from analysis.trade_calculator import TradeCalculator

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("LABEL_GEN")

class LabelGenerator:
    def __init__(self):
        self.collector = HistoricalDataCollector()
        self.fe = FeatureEngineer()
        self.tc = TradeCalculator()
        
    def generate_labels(self, lookahead=120): # 120 Hours (1 week) max hold
        # Load Data (2 Years)
        logger.info("Loading Data (730 Days)...")
        end_date = pd.Timestamp.now()
        start_date = end_date - pd.Timedelta(days=730)
        df = self.collector.download_nq_data(start_date=start_date, end_date=end_date)
        
        # Features
        logger.info("Calculating Features...")
        df = self.fe.calculate_all_features(df)
        
        logger.info(f"Generating Labels for {len(df)} candles...")
        
        # Arrays for speed
        closes = df['Close'].values
        highs = df['High'].values
        lows = df['Low'].values
        atrs = df['ATR'].values
        rsis = df['RSI'].values
        
        targets = []
        valid_indices = []
        
        count_longs = 0
        count_shorts = 0
        count_wins = 0
        
        for i in range(len(df) - lookahead):
            rsi = rsis[i]
            
            # 1. Check Signal
            signal = None # "LONG" or "SHORT"
            if rsi >= 70: signal = "SHORT"
            elif rsi <= 30: signal = "LONG"
            
            if signal is None:
                continue # Skip this row (Not a trade setup)
                
            # 2. Define Parameters
            current_close = closes[i]
            atr = atrs[i]
            if np.isnan(atr): continue
            
            stop_dist = atr * 1.5
            target_dist = atr * 1.5 # Target 1 (Scalp/Bank)
            
            # 3. Check Outcome
            is_win = 0
            
            if signal == "SHORT":
                count_shorts += 1
                stop_price = current_close + stop_dist
                target_price = current_close - target_dist
                
                # Scan Future Candle
                for j in range(1, lookahead):
                    idx = i + j
                    h = highs[idx]
                    l = lows[idx]
                    
                    if h >= stop_price: # Stopped Out
                        is_win = 0
                        break
                    if l <= target_price: # Target Hit
                        is_win = 1
                        break
                        
            elif signal == "LONG":
                count_longs += 1
                stop_price = current_close - stop_dist
                target_price = current_close + target_dist
                
                for j in range(1, lookahead):
                    idx = i + j
                    h = highs[idx]
                    l = lows[idx]
                    
                    if l <= stop_price: # Stopped Out
                        is_win = 0
                        break
                    if h >= target_price: # Target Hit
                        is_win = 1
                        break
            
            targets.append(is_win)
            valid_indices.append(df.index[i])
            if is_win: count_wins += 1
            
            if len(targets) % 100 == 0:
                print(".", end="", flush=True)

        # Create Filtered DataFrame
        filtered_df = df.loc[valid_indices].copy()
        filtered_df['target'] = targets
        
        # Save
        output_path = "backend/data/training_data.csv"
        os.makedirs("backend/data", exist_ok=True)
        filtered_df.to_csv(output_path)
        
        logger.info(f"\nSaved {len(filtered_df)} SIGNAL rows to {output_path}")
        logger.info(f"Longs: {count_longs}, Shorts: {count_shorts}")
        logger.info(f"Win Rate (Base): {count_wins/len(filtered_df)*100:.1f}%")
        
        return output_path

if __name__ == "__main__":
    lg = LabelGenerator()
    lg.generate_labels()
