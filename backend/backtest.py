
import sys
import os
import pandas as pd
import numpy as np
import logging
import argparse

# Path setup
sys.path.append(os.getcwd())
try:
    from backend.ml.data_collector import HistoricalDataCollector
    from backend.ml.feature_engineer import FeatureEngineer
    from backend.analysis.technical_analysis import TechnicalAnalysis
    from backend.analysis.trade_calculator import TradeCalculator
except ImportError:
    sys.path.append(os.path.join(os.getcwd(), 'backend'))
    from ml.data_collector import HistoricalDataCollector
    from ml.feature_engineer import FeatureEngineer
    from analysis.trade_calculator import TradeCalculator

# Logging
logging.basicConfig(level=logging.INFO, format='%(message)s')
logger = logging.getLogger("BACKTEST")

class Backtester:
    def __init__(self, symbol="NQ", days=60, config=None):
        self.symbol = symbol
        self.days = days
        self.collector = HistoricalDataCollector()
        self.fe = FeatureEngineer()
        self.tc = TradeCalculator()
        
        # Default Config (Mean Reversion)
        self.config = config or {
            'rsi_short': 60,
            'rsi_long': 40,
            'atr_stop_mult': 1.5,
            'target1_ratio': 1.5,
            'target2_ratio': 3.0
        }
        
        # Apply config to TradeCalculator
        self.tc.default_atr_multiplier = self.config.get('atr_stop_mult', 1.5)
        self.tc.target1_ratio = self.config.get('target1_ratio', 1.5)
        self.tc.target2_ratio = self.config.get('target2_ratio', 3.0)
        
        self.trades = []
        self.equity = [100000] # Start with 100k dummy
        
    def run(self, verbose=True):
        if verbose: logger.info(f"--- STARTING BACKTEST: {self.symbol} ({self.days} Days) ---")
        
        # 1. Get Data
        df = self.collector.download_nq_data(symbol=self.symbol)
        
        if df.empty:
            logger.error("No data found for backtest.")
            return

        logger.info(f"Loaded {len(df)} candles.")

        # 2. Features (Calculate on FULL history before filtering)
        df = self.fe.calculate_all_features(df)
        
        # Filter last N days AFTER features ready
        cutoff = pd.Timestamp.now(tz=df.index.tz) - pd.Timedelta(days=self.days)
        df = df[df.index >= cutoff]
        
        logger.info(f"Backtesting on {len(df)} candles from {cutoff}")
        
        # 3. Simulate
        active_trade = None
        
        # Start from 1 since features are pre-calculated on history
        # (Though checks might access i-1, so safe start 1)
        for i in range(1, len(df)): 
            row = df.iloc[i]
            
            # Check Active Trade Exit
            if active_trade:
                result = self._check_exit(active_trade, row)
                if result:
                    self.trades.append(result)
                    # logger.info(f"{result['timestamp']} | {result['result']} | PnL: {result['pnl']:.2f}")
                    active_trade = None
                continue # One trade at a time
                
            # Generate Signal
            score = self._calculate_score(row)
            
            # Load Config Threshold
            try:
                # Mock config loading or use what's passed
                # In backtest we might want to force a specific threshold
                threshold = self.config.get('alert_threshold', 60)
            except:
                threshold = 60

            direction = "NEUTRAL"
            # INVERTED STRATEGY (Optimization) with Configurable Thresholds
            # Matches backend/main.py logic
            if score >= threshold: direction = "SHORT"
            elif score <= (100 - threshold): direction = "LONG"
            
            # --- PHASE 7: MACHINE LEARNING FILTER ---
            if self.config.get('use_ml') and direction in ["LONG", "SHORT"]:
                # Lazy load predictor
                if not hasattr(self, 'predictor'):
                    try:
                        # Try standard path first
                        from ml.xgboost_model import XGBoostPredictor
                        logger.info(f"Loading ML Model for {self.symbol} (Relative Path)")
                        self.predictor = XGBoostPredictor(symbol=self.symbol)
                    except ImportError:
                        try:
                            # Try package path
                            from backend.ml.xgboost_model import XGBoostPredictor
                            logger.info(f"Loading ML Model for {self.symbol} (Package Path)")
                            self.predictor = XGBoostPredictor(symbol=self.symbol)
                        except ImportError:
                             logger.error("ML Module not found (Tried relative and package paths).")
                             direction = "NEUTRAL"
                
                if hasattr(self, 'predictor') and self.predictor.is_trained:
                    # prepare features
                    feats = [self.predictor.feature_names] if self.predictor.feature_names else []
                    # self.predictor.feature_names is list of cols
                    try:
                        # Extract features for this row
                        # Ensure row has all features (it should, as FE run on DF)
                        # We need to pass values in correct order
                        # Efficient: row[feature_names].values
                        # But row is Series.
                         
                        # Quick fix for feature access
                        # We need to construct a dict or array 
                        # Predictor expects array via 'predict' or dict via 'predict_with_features'
                        # Let's use predict_with_features? No, simpler to use array if index aligned.
                        
                        cols = self.predictor.feature_names
                        if cols:
                            # row is a Series with feature names as index
                            # row[cols] works if cols exist
                            X = row[cols].values.reshape(1, -1)
                            pred = self.predictor.predict(X)
                            
                            ml_conf = pred['confidence']
                            ml_dir = pred['direction'] # UP, DOWN, SIDEWAYS
                            
                            # DEBUG ML
                            # if i % 100 == 0: logger.info(f"ML Debug: Sig={direction} ML={ml_dir} Conf={ml_conf:.2f}")

                            # Logic: Block conflicting signals
                            # If TA is LONG, but ML is DOWN -> Block
                            # If TA is SHORT, but ML is UP -> Block
                            # If ML is SIDEWAYS -> Allow (Mean Reversion context)
                            
                            threshold = self.config.get('ml_threshold', 0.4) # Lower threshold for determining strong conviction
                            
                            if direction == "LONG":
                                if ml_dir == "DOWN" and ml_conf > threshold:
                                    direction = "NEUTRAL"
                                    # logger.info(f"Blocked LONG by ML DOWN ({ml_conf:.2f})")
                                    
                            elif direction == "SHORT":
                                if ml_dir == "UP" and ml_conf > threshold:
                                    direction = "NEUTRAL"
                                    # logger.info(f"Blocked SHORT by ML UP ({ml_conf:.2f})")
                                    
                            # Optional: Require confirmation for trend trades?
                            # For now, just blocking conflicts is safer for Range markers.
                                
                            # Debug
                            # if direction != "NEUTRAL":
                            #    print(f"ML Approved: {ml_conf:.2f}")
                                    
                    except Exception as e:
                        # logic error or missing col
                        logger.warning(f"ML Prediction failed: {e}")
            
            # --- ADX FILTER (Storm Shelter) ---
            if self.config.get('use_adx_filter', False):
                adx = row.get('ADX_14', 0)
                # Ensure ADX is valid
                if adx is not None and not np.isnan(adx):
                    adx_threshold = self.config.get('adx_threshold', 30)
                    if adx > adx_threshold and direction != "NEUTRAL":
                        direction = "NEUTRAL"   
 
            # --- TREND FILTERS (Dip Buying in Trend) ---
            close = row['Close']
            ema200 = row.get('EMA_200')
            ema50 = row.get('EMA_50')
            ema21 = row.get('EMA_21')
            
            if ema200 and not np.isnan(ema200):
                if direction == "LONG" and close < ema200: 
                    direction = "NEUTRAL" # Buy only above 200 (Pullback)
                if direction == "SHORT" and close > ema200: 
                    direction = "NEUTRAL" # Sell only below 200 (Rally)
            
            if ema50 and ema21 and not np.isnan(ema50) and not np.isnan(ema21):
                if direction == "LONG" and ema21 < ema50: 
                    direction = "NEUTRAL"
                if direction == "SHORT" and ema21 > ema50: 
                    direction = "NEUTRAL"

            if direction in ["LONG", "SHORT"]:
                # Calculate Setup
                setup = self.tc.calculate_trade_setup(df.iloc[:i+1], direction, confidence=abs(score-50)*2/100)
                
                # Enter Trade
                active_trade = {
                    'entry': setup['entry'],
                    'stop': setup['stop_loss'],
                    't1': setup['target1'],
                    't2': setup['target2'],
                    'direction': setup.get('direction', direction), # Use calculated direction (handles Sweeps)
                    'timestamp': row.name, 
                    't1_hit': False
                }

        self._report(verbose=verbose)

    def _calculate_score(self, row):
        """Replicate main.py Technical Analysis scoring"""
        score = 50
        rsi = row.get('RSI', 50)
        sma_10 = row.get('SMA_10', 0)
        sma_20 = row.get('SMA_20', 0)
        sma_50 = row.get('SMA_50', 0)
        close = row['Close']
        open_price = row['Open']

        # RSI Analysis
        if rsi > 60: score += 15
        elif rsi > 50: score += 8
        elif rsi < 40: score -= 15
        elif rsi < 50: score -= 8
        if rsi > 70: score -= 10
        if rsi < 30: score += 10

        # Moving Averages
        if close > sma_10: score += 8
        else: score -= 8
        if close > sma_20: score += 6
        else: score -= 6
        if sma_50 > 0:
            if close > sma_50: score += 4
            else: score -= 4

        # Trend Strength
        if sma_10 > sma_20: score += 8
        else: score -= 8

        # Candle
        if close > open_price: score += 5
        else: score -= 5

        return max(0, min(100, score))

        self._report()
        
    def _check_exit(self, trade, row):
        high = row['High']
        low = row['Low']
        
        if trade['direction'] == "LONG":
            # Check Stop
            if low <= trade['stop']:
                return self._close_trade(trade, trade['stop'], "LOSS")
            
            # Check T1
            if high >= trade['t1'] and not trade['t1_hit']:
                trade['t1_hit'] = True
                trade['stop'] = trade['entry'] # Breakeven
                
            # Check T2
            if high >= trade['t2']:
                return self._close_trade(trade, trade['t2'], "WIN")
                
        else: # SHORT
            if high >= trade['stop']:
                 return self._close_trade(trade, trade['stop'], "LOSS")
            
            if low <= trade['t1'] and not trade['t1_hit']:
                trade['t1_hit'] = True
                trade['stop'] = trade['entry']
                
            if low <= trade['t2']:
                return self._close_trade(trade, trade['t2'], "WIN")
                
        return None

    def _close_trade(self, trade, exit_price, result):
        pnl = exit_price - trade['entry']
        if trade['direction'] == "SHORT":
            pnl = -pnl
        return {
            'timestamp': trade['timestamp'],
            'type': trade['direction'],
            'result': result,
            'pnl': pnl
        }

    def _report(self, verbose=True):
        if not self.trades:
            if verbose: logger.info("No trades generated.")
            return

        df_res = pd.DataFrame(self.trades)
        wins = df_res[df_res['pnl'] > 0]
        
        win_rate = len(wins) / len(df_res) * 100
        total_pnl = df_res['pnl'].sum()
        
        self.stats = {
            'win_rate': win_rate,
            'pnl': total_pnl,
            'trades': len(df_res)
        }
        
        if verbose:
            print("\n" + "="*40)
            print(f"BACKTEST RESULTS ({self.days} Days)")
            print("="*40)
            print(f"Total Trades: {len(df_res)}")
            print(f"Win Rate:     {win_rate:.1f}%")
            print(f"Total PnL:    {total_pnl:.2f} pts")
            print(f"Avg Trade:    {df_res['pnl'].mean():.2f} pts")
            print("="*40 + "\n")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Backtest NQ AI Strategy')
    parser.add_argument('--days', type=int, default=60, help='Days to backtest')
    parser.add_argument('--threshold', type=int, default=60, help='Alert Threshold')
    parser.add_argument('--ml', action='store_true', help='Enable ML Filter')
    parser.add_argument('--symbol', type=str, default='NQ', help='Symbol to test')
    
    args = parser.parse_args()
    
    config = {
        'alert_threshold': args.threshold,
        'use_ml': args.ml,
        'ml_model_path': f'backend/ml/models/xgboost_model_{args.symbol}.pkl'
    }
    
    # Check if ML model exists if requested
    if args.ml and not os.path.exists(config['ml_model_path']):
        print(f"WARNING: ML Model not found at {config['ml_model_path']}. Using default.")
        config['ml_model_path'] = 'backend/ml/models/xgboost_model.pkl'

    bt = Backtester(symbol=args.symbol, days=args.days, config=config)
    bt.run()
