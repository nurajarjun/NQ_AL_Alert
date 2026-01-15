#!/usr/bin/env python3
"""
Comprehensive Backtest System
Tests all symbols at different times over 5 days
"""

import sys
import os
import pandas as pd
import numpy as np
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Tuple
import json

# Setup paths
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

from ml.data_collector import HistoricalDataCollector
from ml.feature_engineer import FeatureEngineer
from ml.xgboost_model import XGBoostPredictor
from analysis.trade_calculator import TradeCalculator

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Symbols to test
SYMBOLS = ["NQ", "ES", "TQQQ", "SQQQ", "SOXL", "SOXS"]

# Market sessions (ET times)
SESSIONS = {
    'pre_market': (4, 9.5),      # 4:00 AM - 9:30 AM
    'morning': (9.5, 11),         # 9:30 AM - 11:00 AM
    'midday': (11, 14),           # 11:00 AM - 2:00 PM
    'power_hour': (14, 16),       # 2:00 PM - 4:00 PM
    'after_hours': (16, 20)       # 4:00 PM - 8:00 PM
}

class ComprehensiveBacktester:
    """Comprehensive backtester for multiple symbols and timeframes"""
    
    def __init__(self, days=5, verbose=True):
        self.days = days
        self.verbose = verbose
        self.collector = HistoricalDataCollector()
        self.feature_engineer = FeatureEngineer()
        self.trade_calculator = TradeCalculator()
        
        # Results storage
        self.all_trades = []
        self.symbol_stats = {}
        self.session_stats = {}
        
        # ML models (lazy loaded)
        self.ml_models = {}
        
    def get_ml_model(self, symbol):
        """Lazy load ML model for symbol"""
        if symbol not in self.ml_models:
            try:
                logger.info(f"Loading ML model for {symbol}...")
                model = XGBoostPredictor(symbol=symbol)
                if model.is_trained:
                    self.ml_models[symbol] = model
                    logger.info(f"✅ {symbol} model loaded")
                else:
                    logger.warning(f"⚠️ {symbol} model not trained, using TA only")
                    self.ml_models[symbol] = None
            except Exception as e:
                logger.warning(f"❌ Failed to load {symbol} model: {e}")
                self.ml_models[symbol] = None
        
        return self.ml_models[symbol]
    
    def calculate_score(self, row):
        """Calculate technical analysis score (from main.py)"""
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
    
    def get_session_name(self, hour):
        """Determine session name from hour (ET)"""
        for session_name, (start, end) in SESSIONS.items():
            if start <= hour < end:
                return session_name
        return 'closed'
    
    def run_backtest(self):
        """Run comprehensive backtest across all symbols"""
        logger.info("="*80)
        logger.info("COMPREHENSIVE BACKTEST - 5 Days, All Symbols")
        logger.info("="*80)
        
        for symbol in SYMBOLS:
            logger.info(f"\n{'='*80}")
            logger.info(f"Testing {symbol}...")
            logger.info(f"{'='*80}")
            
            try:
                self.test_symbol(symbol)
            except Exception as e:
                logger.error(f"❌ Error testing {symbol}: {e}")
                import traceback
                traceback.print_exc()
                continue
        
        # Generate reports
        self.generate_reports()
    
    def test_symbol(self, symbol):
        """Test a single symbol over 5 days"""
        # 1. Get data
        logger.info(f"Fetching {symbol} data...")
        df = self.collector.download_nq_data(symbol=symbol)
        
        if df.empty:
            logger.warning(f"No data for {symbol}")
            return
        
        logger.info(f"Loaded {len(df)} candles")
        
        # 2. Calculate features
        logger.info("Calculating features...")
        df = self.feature_engineer.calculate_all_features(df)
        
        # 3. Filter to last N days
        cutoff = pd.Timestamp.now(tz=df.index.tz) - pd.Timedelta(days=self.days)
        df = df[df.index >= cutoff]
        
        logger.info(f"Testing {len(df)} candles from {cutoff.date()}")
        
        # 4. Load ML model
        ml_model = self.get_ml_model(symbol)
        
        # 5. Sample test points (every 4 hours to get different times)
        test_indices = list(range(0, len(df), 4))
        
        logger.info(f"Testing {len(test_indices)} time points...")
        
        # 6. Run predictions at each point
        for idx in test_indices:
            if idx + 5 >= len(df):  # Need lookahead for exit
                continue
            
            row = df.iloc[idx]
            timestamp = row.name
            
            # Calculate TA score
            score = self.calculate_score(row)
            
            # Determine direction (mean reversion strategy)
            threshold = 70
            if score >= threshold:
                direction = "SHORT"
            elif score <= (100 - threshold):
                direction = "LONG"
            else:
                direction = "NEUTRAL"
            
            # ML enhancement
            strategy = "TA"
            if ml_model and direction != "NEUTRAL":
                try:
                    X = df.iloc[idx:idx+1].drop(['Target'], axis=1, errors='ignore')
                    
                    # Align features
                    if ml_model.feature_names:
                        X_aligned = pd.DataFrame(0, index=X.index, columns=ml_model.feature_names)
                        for col in X.columns:
                            if col in ml_model.feature_names:
                                X_aligned[col] = X[col]
                        X = X_aligned
                    
                    prediction = ml_model.model.predict(X.values)[0]
                    probabilities = ml_model.model.predict_proba(X.values)[0]
                    
                    dir_map = {0: "SIDEWAYS", 1: "DOWN", 2: "UP"}
                    ml_direction = dir_map.get(prediction, "NEUTRAL")
                    ml_confidence = probabilities[prediction]
                    
                    # Filter conflicting signals
                    if direction == "LONG" and ml_direction == "DOWN" and ml_confidence > 0.4:
                        direction = "NEUTRAL"
                        strategy = "ML_FILTERED"
                    elif direction == "SHORT" and ml_direction == "UP" and ml_confidence > 0.4:
                        direction = "NEUTRAL"
                        strategy = "ML_FILTERED"
                    else:
                        strategy = "ML_ENHANCED"
                        
                except Exception as e:
                    logger.debug(f"ML prediction failed: {e}")
                    strategy = "TA"
            
            if direction == "NEUTRAL":
                continue
            
            # Calculate trade setup
            confidence = abs(score - 50) * 2 / 100
            setup = self.trade_calculator.calculate_trade_setup(
                df.iloc[:idx+1], 
                direction, 
                confidence
            )
            
            # Simulate trade execution
            trade_result = self.simulate_trade(
                symbol=symbol,
                timestamp=timestamp,
                direction=direction,
                setup=setup,
                df=df,
                entry_idx=idx,
                strategy=strategy,
                confidence=confidence * 100
            )
            
            if trade_result:
                self.all_trades.append(trade_result)
    
    def simulate_trade(self, symbol, timestamp, direction, setup, df, entry_idx, strategy, confidence):
        """Simulate trade execution and track result"""
        entry = setup['entry']
        stop = setup['stop_loss']
        t1 = setup['target1']
        t2 = setup['target2']
        
        # Track through next 5 candles (5 hours for 1h data)
        max_lookahead = min(5, len(df) - entry_idx - 1)
        
        t1_hit = False
        exit_price = None
        exit_reason = None
        
        for i in range(1, max_lookahead + 1):
            candle = df.iloc[entry_idx + i]
            high = candle['High']
            low = candle['Low']
            
            if direction == "LONG":
                # Check stop
                if low <= stop:
                    exit_price = stop
                    exit_reason = "STOP_LOSS"
                    break
                
                # Check T1
                if high >= t1 and not t1_hit:
                    t1_hit = True
                    stop = entry  # Move to breakeven
                
                # Check T2
                if high >= t2:
                    exit_price = t2
                    exit_reason = "TARGET_2"
                    break
            
            else:  # SHORT
                # Check stop
                if high >= stop:
                    exit_price = stop
                    exit_reason = "STOP_LOSS"
                    break
                
                # Check T1
                if low <= t1 and not t1_hit:
                    t1_hit = True
                    stop = entry
                
                # Check T2
                if low <= t2:
                    exit_price = t2
                    exit_reason = "TARGET_2"
                    break
        
        # If no exit, close at last candle
        if exit_price is None:
            exit_price = df.iloc[entry_idx + max_lookahead]['Close']
            exit_reason = "TIME_EXIT"
        
        # Calculate P&L
        pnl_points = exit_price - entry
        if direction == "SHORT":
            pnl_points = -pnl_points
        
        # Estimate dollar P&L (rough approximation)
        multipliers = {
            'NQ': 20,    # $20 per point
            'ES': 50,    # $50 per point
            'TQQQ': 100, # $1 per share, assume 100 shares
            'SQQQ': 100,
            'SOXL': 100,
            'SOXS': 100
        }
        multiplier = multipliers.get(symbol, 1)
        pnl_dollars = pnl_points * multiplier
        
        # Determine result
        if pnl_points > 0:
            result = "WIN"
        elif pnl_points < 0:
            result = "LOSS"
        else:
            result = "BREAKEVEN"
        
        # Get session
        hour = timestamp.hour
        session = self.get_session_name(hour)
        
        return {
            'timestamp': timestamp,
            'symbol': symbol,
            'direction': direction,
            'entry_price': entry,
            'stop_loss': stop,
            'target1': t1,
            'target2': t2,
            'exit_price': exit_price,
            'exit_reason': exit_reason,
            'pnl_points': pnl_points,
            'pnl_dollars': pnl_dollars,
            'result': result,
            'strategy': strategy,
            'confidence': confidence,
            'session': session,
            't1_hit': t1_hit
        }
    
    def generate_reports(self):
        """Generate comprehensive reports"""
        if not self.all_trades:
            logger.warning("No trades to report!")
            return
        
        logger.info(f"\n{'='*80}")
        logger.info("GENERATING REPORTS")
        logger.info(f"{'='*80}")
        
        # Convert to DataFrame
        df = pd.DataFrame(self.all_trades)
        
        # Save CSV
        csv_path = 'backtest_results.csv'
        df.to_csv(csv_path, index=False)
        logger.info(f"✅ Saved CSV: {csv_path}")
        
        # Generate markdown report
        self.generate_markdown_report(df)
        
        # Print summary to console
        self.print_summary(df)
    
    def generate_markdown_report(self, df):
        """Generate detailed markdown report"""
        report = []
        report.append("# Comprehensive Backtest Results\n")
        report.append(f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        report.append(f"**Period:** Last {self.days} days\n")
        report.append(f"**Symbols:** {', '.join(SYMBOLS)}\n")
        report.append("\n---\n")
        
        # Executive Summary
        report.append("\n## Executive Summary\n")
        total_trades = len(df)
        wins = len(df[df['result'] == 'WIN'])
        win_rate = (wins / total_trades * 100) if total_trades > 0 else 0
        total_pnl = df['pnl_dollars'].sum()
        
        report.append(f"- **Total Trades:** {total_trades}\n")
        report.append(f"- **Win Rate:** {win_rate:.1f}%\n")
        report.append(f"- **Total P&L:** ${total_pnl:,.2f}\n")
        report.append(f"- **Average Trade:** ${df['pnl_dollars'].mean():,.2f}\n")
        report.append("\n")
        
        # Per-Symbol Analysis
        report.append("## Per-Symbol Performance\n")
        report.append("\n| Symbol | Trades | Win Rate | Total P&L | Avg P&L |\n")
        report.append("|--------|--------|----------|-----------|----------|\n")
        
        for symbol in SYMBOLS:
            symbol_df = df[df['symbol'] == symbol]
            if len(symbol_df) == 0:
                continue
            
            s_trades = len(symbol_df)
            s_wins = len(symbol_df[symbol_df['result'] == 'WIN'])
            s_win_rate = (s_wins / s_trades * 100) if s_trades > 0 else 0
            s_pnl = symbol_df['pnl_dollars'].sum()
            s_avg = symbol_df['pnl_dollars'].mean()
            
            report.append(f"| {symbol} | {s_trades} | {s_win_rate:.1f}% | ${s_pnl:,.2f} | ${s_avg:,.2f} |\n")
        
        report.append("\n")
        
        # Time-of-Day Analysis
        report.append("## Time-of-Day Performance\n")
        report.append("\n| Session | Trades | Win Rate | Avg P&L |\n")
        report.append("|---------|--------|----------|----------|\n")
        
        for session in ['pre_market', 'morning', 'midday', 'power_hour', 'after_hours']:
            session_df = df[df['session'] == session]
            if len(session_df) == 0:
                continue
            
            sess_trades = len(session_df)
            sess_wins = len(session_df[session_df['result'] == 'WIN'])
            sess_win_rate = (sess_wins / sess_trades * 100) if sess_trades > 0 else 0
            sess_avg = session_df['pnl_dollars'].mean()
            
            report.append(f"| {session.replace('_', ' ').title()} | {sess_trades} | {sess_win_rate:.1f}% | ${sess_avg:,.2f} |\n")
        
        report.append("\n")
        
        # Strategy Comparison
        report.append("## Strategy Performance\n")
        report.append("\n| Strategy | Trades | Win Rate | Total P&L |\n")
        report.append("|----------|--------|----------|----------|\n")
        
        for strategy in df['strategy'].unique():
            strat_df = df[df['strategy'] == strategy]
            st_trades = len(strat_df)
            st_wins = len(strat_df[strat_df['result'] == 'WIN'])
            st_win_rate = (st_wins / st_trades * 100) if st_trades > 0 else 0
            st_pnl = strat_df['pnl_dollars'].sum()
            
            report.append(f"| {strategy} | {st_trades} | {st_win_rate:.1f}% | ${st_pnl:,.2f} |\n")
        
        report.append("\n")
        
        # Best/Worst Trades
        report.append("## Notable Trades\n")
        report.append("\n### Best Trade\n")
        best = df.loc[df['pnl_dollars'].idxmax()]
        report.append(f"- **Symbol:** {best['symbol']}\n")
        report.append(f"- **Time:** {best['timestamp']}\n")
        report.append(f"- **Direction:** {best['direction']}\n")
        report.append(f"- **P&L:** ${best['pnl_dollars']:,.2f}\n")
        report.append("\n")
        
        report.append("### Worst Trade\n")
        worst = df.loc[df['pnl_dollars'].idxmin()]
        report.append(f"- **Symbol:** {worst['symbol']}\n")
        report.append(f"- **Time:** {worst['timestamp']}\n")
        report.append(f"- **Direction:** {worst['direction']}\n")
        report.append(f"- **P&L:** ${worst['pnl_dollars']:,.2f}\n")
        report.append("\n")
        
        # Write report
        report_path = 'backtest_results.md'
        with open(report_path, 'w') as f:
            f.write(''.join(report))
        
        logger.info(f"✅ Saved report: {report_path}")
    
    def print_summary(self, df):
        """Print summary to console"""
        print("\n" + "="*80)
        print("COMPREHENSIVE BACKTEST RESULTS")
        print("="*80)
        print(f"Period: Last {self.days} days")
        print(f"Symbols: {', '.join(SYMBOLS)}")
        print()
        
        total_trades = len(df)
        wins = len(df[df['result'] == 'WIN'])
        win_rate = (wins / total_trades * 100) if total_trades > 0 else 0
        total_pnl = df['pnl_dollars'].sum()
        
        print("OVERALL PERFORMANCE")
        print("-" * 80)
        print(f"Total Trades:  {total_trades}")
        print(f"Win Rate:      {win_rate:.1f}%")
        print(f"Total P&L:     ${total_pnl:,.2f}")
        print(f"Average Trade: ${df['pnl_dollars'].mean():,.2f}")
        print()
        
        print("PER-SYMBOL BREAKDOWN")
        print("-" * 80)
        for symbol in SYMBOLS:
            symbol_df = df[df['symbol'] == symbol]
            if len(symbol_df) == 0:
                continue
            
            s_trades = len(symbol_df)
            s_wins = len(symbol_df[symbol_df['result'] == 'WIN'])
            s_win_rate = (s_wins / s_trades * 100) if s_trades > 0 else 0
            s_pnl = symbol_df['pnl_dollars'].sum()
            
            print(f"{symbol:6} | {s_trades:2} trades | {s_win_rate:5.1f}% win | ${s_pnl:+8,.2f}")
        
        print()
        print("FILES GENERATED")
        print("-" * 80)
        print("✅ backtest_results.csv")
        print("✅ backtest_results.md")
        print("="*80 + "\n")


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='Comprehensive Backtest System')
    parser.add_argument('--days', type=int, default=5, help='Number of days to backtest')
    parser.add_argument('--symbol', type=str, help='Test single symbol only')
    parser.add_argument('--verbose', action='store_true', help='Verbose output')
    
    args = parser.parse_args()
    
    # Override symbols if single symbol requested
    if args.symbol:
        SYMBOLS = [args.symbol.upper()]
    
    backtester = ComprehensiveBacktester(days=args.days, verbose=args.verbose)
    backtester.run_backtest()
