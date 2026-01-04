"""
Pattern Recognition Database
Stores trade history and finds similar patterns
"""

import sqlite3
import json
from datetime import datetime
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
import logging

logger = logging.getLogger(__name__)


class PatternDatabase:
    """Stores and retrieves similar trading patterns"""
    
    def __init__(self, db_path="database/patterns.db"):
        self.db_path = db_path
        self._init_database()
    
    def _init_database(self):
        """Initialize database tables"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Create trades table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS trades (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TEXT NOT NULL,
                    direction TEXT NOT NULL,
                    entry REAL NOT NULL,
                    stop REAL NOT NULL,
                    target1 REAL NOT NULL,
                    target2 REAL,
                    rsi REAL,
                    atr REAL,
                    volume_ratio REAL,
                    ai_score INTEGER,
                    outcome TEXT,
                    profit_loss REAL,
                    exit_price REAL,
                    exit_time TEXT,
                    features TEXT,
                    notes TEXT
                )
            ''')
            
            conn.commit()
            conn.close()
            logger.info(f"Pattern database initialized at {self.db_path}")
            
        except Exception as e:
            logger.error(f"Database initialization failed: {e}")
    
    def store_trade(self, trade_data):
        """
        Store a trade in the database
        
        Args:
            trade_data: dict with trade information
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Extract features for similarity matching
            features = self._extract_features(trade_data)
            
            cursor.execute('''
                INSERT INTO trades (
                    timestamp, direction, entry, stop, target1, target2,
                    rsi, atr, volume_ratio, ai_score, features
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                trade_data.get('timestamp', datetime.now().isoformat()),
                trade_data['direction'],
                trade_data['entry'],
                trade_data['stop'],
                trade_data.get('target1'),
                trade_data.get('target2'),
                trade_data.get('rsi'),
                trade_data.get('atr'),
                trade_data.get('volume_ratio'),
                trade_data.get('ai_score'),
                json.dumps(features)
            ))
            
            conn.commit()
            trade_id = cursor.lastrowid
            conn.close()
            
            logger.info(f"Trade stored with ID: {trade_id}")
            return trade_id
            
        except Exception as e:
            logger.error(f"Failed to store trade: {e}")
            return None
    
    def update_trade_outcome(self, trade_id, outcome, profit_loss, exit_price):
        """
        Update trade with outcome
        
        Args:
            trade_id: Trade ID
            outcome: 'WIN' or 'LOSS'
            profit_loss: Profit/loss amount
            exit_price: Exit price
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                UPDATE trades
                SET outcome = ?, profit_loss = ?, exit_price = ?, exit_time = ?
                WHERE id = ?
            ''', (outcome, profit_loss, exit_price, datetime.now().isoformat(), trade_id))
            
            conn.commit()
            conn.close()
            
            logger.info(f"Trade {trade_id} updated: {outcome}, P/L: {profit_loss}")
            
        except Exception as e:
            logger.error(f"Failed to update trade: {e}")
    
    def find_similar_patterns(self, current_trade, top_k=15):
        """
        Find similar historical patterns
        
        Args:
            current_trade: Current trade data
            top_k: Number of similar patterns to return
            
        Returns:
            List of similar trades with similarity scores
        """
        try:
            # Extract features from current trade
            current_features = self._extract_features(current_trade)
            current_vector = np.array(list(current_features.values())).reshape(1, -1)
            
            # Get all historical trades
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT id, timestamp, direction, entry, stop, target1,
                       outcome, profit_loss, features
                FROM trades
                WHERE outcome IS NOT NULL
                ORDER BY timestamp DESC
                LIMIT 1000
            ''')
            
            historical_trades = cursor.fetchall()
            conn.close()
            
            if not historical_trades:
                return []
            
            # Calculate similarities
            similarities = []
            
            for trade in historical_trades:
                trade_id, timestamp, direction, entry, stop, target1, outcome, profit_loss, features_json = trade
                
                # Skip if different direction
                if direction != current_trade['direction']:
                    continue
                
                # Parse features
                try:
                    features = json.loads(features_json)
                    feature_vector = np.array(list(features.values())).reshape(1, -1)
                    
                    # Calculate cosine similarity
                    similarity = cosine_similarity(current_vector, feature_vector)[0][0]
                    
                    similarities.append({
                        'trade_id': trade_id,
                        'timestamp': timestamp,
                        'similarity': float(similarity),
                        'outcome': outcome,
                        'profit_loss': profit_loss,
                        'entry': entry,
                        'stop': stop,
                        'target1': target1
                    })
                    
                except Exception as e:
                    continue
            
            # Sort by similarity
            similarities.sort(key=lambda x: x['similarity'], reverse=True)
            
            return similarities[:top_k]
            
        except Exception as e:
            logger.error(f"Failed to find similar patterns: {e}")
            return []
    
    def calculate_win_rate(self, similar_patterns):
        """
        Calculate win rate from similar patterns
        
        Returns:
            dict with statistics
        """
        if not similar_patterns:
            return {
                'win_rate': 0,
                'total_trades': 0,
                'wins': 0,
                'losses': 0,
                'avg_win': 0,
                'avg_loss': 0
            }
        
        wins = [p for p in similar_patterns if p['outcome'] == 'WIN']
        losses = [p for p in similar_patterns if p['outcome'] == 'LOSS']
        
        total = len(similar_patterns)
        win_count = len(wins)
        loss_count = len(losses)
        
        avg_win = np.mean([w['profit_loss'] for w in wins]) if wins else 0
        avg_loss = np.mean([l['profit_loss'] for l in losses]) if losses else 0
        
        return {
            'win_rate': (win_count / total) if total > 0 else 0,
            'total_trades': total,
            'wins': win_count,
            'losses': loss_count,
            'avg_win': float(avg_win),
            'avg_loss': float(avg_loss),
            'expectancy': (win_count * avg_win + loss_count * avg_loss) / total if total > 0 else 0
        }
    
    def _extract_features(self, trade_data):
        """
        Extract numerical features for similarity matching
        
        Returns:
            dict of features
        """
        entry = trade_data['entry']
        stop = trade_data['stop']
        target1 = trade_data.get('target1', entry)
        
        risk = abs(entry - stop)
        reward = abs(target1 - entry)
        rr_ratio = reward / risk if risk > 0 else 0
        
        return {
            'rsi': trade_data.get('rsi', 50),
            'atr': trade_data.get('atr', 40),
            'atr_pct': (trade_data.get('atr', 40) / entry) * 100 if entry > 0 else 0,
            'volume_ratio': trade_data.get('volume_ratio', 1.0),
            'rr_ratio': rr_ratio,
            'risk_pct': (risk / entry) * 100 if entry > 0 else 0,
            'ai_score': trade_data.get('ai_score', 50) / 100,  # Normalize
        }
    
    def get_statistics(self):
        """Get overall database statistics"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('SELECT COUNT(*) FROM trades')
            total_trades = cursor.fetchone()[0]
            
            cursor.execute('SELECT COUNT(*) FROM trades WHERE outcome = "WIN"')
            total_wins = cursor.fetchone()[0]
            
            cursor.execute('SELECT COUNT(*) FROM trades WHERE outcome = "LOSS"')
            total_losses = cursor.fetchone()[0]
            
            cursor.execute('SELECT AVG(profit_loss) FROM trades WHERE outcome = "WIN"')
            avg_win = cursor.fetchone()[0] or 0
            
            cursor.execute('SELECT AVG(profit_loss) FROM trades WHERE outcome = "LOSS"')
            avg_loss = cursor.fetchone()[0] or 0
            
            conn.close()
            
            return {
                'total_trades': total_trades,
                'completed_trades': total_wins + total_losses,
                'wins': total_wins,
                'losses': total_losses,
                'win_rate': (total_wins / (total_wins + total_losses)) if (total_wins + total_losses) > 0 else 0,
                'avg_win': avg_win,
                'avg_loss': avg_loss
            }
            
        except Exception as e:
            logger.error(f"Failed to get statistics: {e}")
            return {}


if __name__ == "__main__":
    # Test pattern database
    logging.basicConfig(level=logging.INFO)
    
    print("="*60)
    print("PATTERN DATABASE TEST")
    print("="*60)
    
    db = PatternDatabase()
    
    # Test trade
    test_trade = {
        'direction': 'LONG',
        'entry': 21880,
        'stop': 21850,
        'target1': 21940,
        'rsi': 55,
        'atr': 35,
        'volume_ratio': 1.3,
        'ai_score': 75
    }
    
    print("\n1. Storing test trade...")
    trade_id = db.store_trade(test_trade)
    print(f"   Trade ID: {trade_id}")
    
    print("\n2. Finding similar patterns...")
    similar = db.find_similar_patterns(test_trade, top_k=5)
    print(f"   Found {len(similar)} similar patterns")
    
    print("\n3. Database statistics:")
    stats = db.get_statistics()
    for key, value in stats.items():
        print(f"   {key}: {value}")
    
    print("\n" + "="*60)
