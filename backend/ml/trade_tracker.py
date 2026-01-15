"""
Trade Tracker - Continuous Learning System
Logs every trade for performance analysis and model retraining
"""

import sqlite3
import pandas as pd
from datetime import datetime
import logging
import json

logger = logging.getLogger(__name__)

class TradeTracker:
    """Tracks all trades for continuous learning"""
    
    def __init__(self, db_path="ml/data/trades.db"):
        self.db_path = db_path
        self._init_database()
    
    def _init_database(self):
        """Create trades table if not exists"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS trades (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp DATETIME,
                symbol TEXT,
                direction TEXT,
                entry_price REAL,
                exit_price REAL,
                profit_loss REAL,
                profit_pct REAL,
                features TEXT,
                model_confidence REAL,
                win BOOLEAN,
                hold_time_minutes INTEGER
            )
        ''')
        
        conn.commit()
        conn.close()
        logger.info(f"Trade tracker initialized: {self.db_path}")
    
    def log_trade(self, trade_data: dict):
        """
        Log a completed trade
        
        Args:
            trade_data: {
                'symbol': 'NQ',
                'direction': 'LONG',
                'entry_price': 18500,
                'exit_price': 18550,
                'features': {...},  # Dict of features at entry
                'model_confidence': 0.85
            }
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Calculate P/L
        if trade_data['direction'] == 'LONG':
            profit_loss = trade_data['exit_price'] - trade_data['entry_price']
        else:
            profit_loss = trade_data['entry_price'] - trade_data['exit_price']
        
        profit_pct = (profit_loss / trade_data['entry_price']) * 100
        win = profit_loss > 0
        
        cursor.execute('''
            INSERT INTO trades (
                timestamp, symbol, direction, entry_price, exit_price,
                profit_loss, profit_pct, features, model_confidence, win, hold_time_minutes
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            datetime.now(),
            trade_data['symbol'],
            trade_data['direction'],
            trade_data['entry_price'],
            trade_data['exit_price'],
            profit_loss,
            profit_pct,
            json.dumps(trade_data.get('features', {})),
            trade_data.get('model_confidence', 0),
            win,
            trade_data.get('hold_time_minutes', 0)
        ))
        
        conn.commit()
        conn.close()
        
        logger.info(f"Trade logged: {trade_data['symbol']} {trade_data['direction']} "
                   f"{'WIN' if win else 'LOSS'} {profit_pct:.2f}%")
    
    def get_performance_stats(self, symbol=None, days=30):
        """Get performance statistics"""
        conn = sqlite3.connect(self.db_path)
        
        query = "SELECT * FROM trades WHERE timestamp >= datetime('now', '-{} days')".format(days)
        if symbol:
            query += f" AND symbol = '{symbol}'"
        
        df = pd.read_sql_query(query, conn)
        conn.close()
        
        if df.empty:
            return {
                'total_trades': 0,
                'win_rate': 0,
                'avg_profit': 0,
                'total_pnl': 0
            }
        
        return {
            'total_trades': len(df),
            'win_rate': (df['win'].sum() / len(df)) * 100,
            'avg_profit': df['profit_pct'].mean(),
            'total_pnl': df['profit_loss'].sum(),
            'best_trade': df['profit_pct'].max(),
            'worst_trade': df['profit_pct'].min()
        }
    
    def get_feature_performance(self, days=30):
        """Analyze which features correlate with wins"""
        conn = sqlite3.connect(self.db_path)
        
        query = f"SELECT features, win FROM trades WHERE timestamp >= datetime('now', '-{days} days')"
        df = pd.read_sql_query(query, conn)
        conn.close()
        
        if df.empty:
            return {}
        
        # Parse features and analyze
        feature_wins = {}
        for _, row in df.iterrows():
            features = json.loads(row['features'])
            for feature, value in features.items():
                if feature not in feature_wins:
                    feature_wins[feature] = {'wins': 0, 'total': 0}
                
                feature_wins[feature]['total'] += 1
                if row['win']:
                    feature_wins[feature]['wins'] += 1
        
        # Calculate win rates per feature
        feature_performance = {}
        for feature, stats in feature_wins.items():
            feature_performance[feature] = {
                'win_rate': (stats['wins'] / stats['total']) * 100,
                'sample_size': stats['total']
            }
        
        return feature_performance

if __name__ == "__main__":
    # Test
    logging.basicConfig(level=logging.INFO)
    
    tracker = TradeTracker()
    
    # Simulate a trade
    test_trade = {
        'symbol': 'NQ',
        'direction': 'LONG',
        'entry_price': 18500,
        'exit_price': 18550,
        'features': {
            'RSI': 45,
            'EMA_20_60m': 18480,
            'FVG_Strength': 0.5
        },
        'model_confidence': 0.85,
        'hold_time_minutes': 30
    }
    
    tracker.log_trade(test_trade)
    
    stats = tracker.get_performance_stats()
    print(f"\nPerformance: {stats}")
