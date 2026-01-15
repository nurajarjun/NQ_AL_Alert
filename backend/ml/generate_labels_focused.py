
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
logger = logging.getLogger("LABEL_GEN_FOCUSED")

class FocusedLabelGenerator:
    def __init__(self):
        self.collector = HistoricalDataCollector()
        self.fe = FeatureEngineer()
        self.tc = TradeCalculator()
        
    def generate_labels(self, lookahead=120):
        # Load Data (2 Years)
        logger.info("Loading Data (730 Days)...")
        end_date = pd.Timestamp.now()
        start_date = end_date - pd.Timedelta(days=730)
        df = self.collector.download_nq_data(start_date=start_date, end_date=end_date)
        
        # Features
        logger.info("Calculating Features...")
        df = self.fe.calculate_all_features(df)
        
        # CRITICAL: Filter to ONLY Mean Reversion Features
        logger.info("Filtering to Mean Reversion Features Only...")
        keep_features = [
            'RSI',           # Primary signal
            'ATR',           # Risk sizing
            'ATR_Pct',       # Volatility %
            'Volume',        # Liquidity
            'STOCHRSIk_14_14_3_3',  # RSI confirmation
            'STOCHRSId_14_14_3_3',  # RSI divergence
            'BBB_20_2.0_2.0',       # Bollinger bandwidth (volatility)
            'BBU_20_2.0_2.0',       # Upper band (resistance)
            'BBL_20_2.0_2.0',       # Lower band (support)
            'OBV',                   # Volume flow
            'EFI',                   # Force index
            'DayOfWeek',            # Session bias
            'Hour'                   # Intraday timing
        ]
        
        # Keep only these columns + OHLCV
        base_cols = ['Open', 'High', 'Low', 'Close', 'Volume']
        available_features = [f for f in keep_features if f in df.columns]
        df_focused = df[base_cols + available_features].copy()
        
        logger.info(f"Reduced from {len(df.columns)} to {len(df_focused.columns)} features")
        logger.info(f"Generating Labels for {len(df_focused)} candles...")
        
        # Arrays for speed
        closes = df_focused['Close'].values
        highs = df_focused['High'].values
        lows = df_focused['Low'].values
        atrs = df_focused['ATR'].values
        rsis = df_focused['RSI'].values
        
        targets = []
        valid_indices = []
        
        count_longs = 0
        count_shorts = 0
        count_wins = 0
        
        for i in range(len(df_focused) - lookahead):
            rsi = rsis[i]
            
            # 1. Check Signal
            signal = None
            if rsi >= 70: signal = "SHORT"
            elif rsi <= 30: signal = "LONG"
            
            if signal is None:
                continue
                
            # 2. Define Parameters
            current_close = closes[i]
            atr = atrs[i]
            if np.isnan(atr): continue
            
            stop_dist = atr * 1.5
            target_dist = atr * 1.5
            
            # 3. Check Outcome
            is_win = 0
            
            if signal == "SHORT":
                count_shorts += 1
                stop_price = current_close + stop_dist
                target_price = current_close - target_dist
                
                for j in range(1, lookahead):
                    idx = i + j
                    h = highs[idx]
                    l = lows[idx]
                    
                    if h >= stop_price:
                        is_win = 0
                        break
                    if l <= target_price:
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
                    
                    if l <= stop_price:
                        is_win = 0
                        break
                    if h >= target_price:
                        is_win = 1
                        break
            
            targets.append(is_win)
            valid_indices.append(df_focused.index[i])
            if is_win: count_wins += 1
            
            if len(targets) % 100 == 0:
                print(".", end="", flush=True)

        # Create Filtered DataFrame
        filtered_df = df_focused.loc[valid_indices].copy()
        filtered_df['target'] = targets
        
        # Save
        output_path = "backend/data/training_data_focused.csv"
        os.makedirs("backend/data", exist_ok=True)
        filtered_df.to_csv(output_path)
        
        logger.info(f"\nSaved {len(filtered_df)} SIGNAL rows to {output_path}")
        logger.info(f"Longs: {count_longs}, Shorts: {count_shorts}")
        logger.info(f"Win Rate (Base): {count_wins/len(filtered_df)*100:.1f}%")
        logger.info(f"Features Used: {len(available_features)}")
        
        return output_path

if __name__ == "__main__":
    lg = FocusedLabelGenerator()
    lg.generate_labels()
