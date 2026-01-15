"""
Multi-Timeframe Analysis
Analyzes multiple timeframes to confirm trend strength
"""

import yfinance as yf
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)


class MultiTimeframeAnalyzer:
    """Analyzes multiple timeframes for trend confirmation"""
    
    def __init__(self):
        self.timeframes = {
            '5m': {'period': '5d', 'interval': '5m', 'weight': 0.15},
            '15m': {'period': '5d', 'interval': '15m', 'weight': 0.20},
            '1h': {'period': '1mo', 'interval': '1h', 'weight': 0.25},
            '4h': {'period': '3mo', 'interval': '1h', 'weight': 0.25},  # Aggregate from 1h
            '1d': {'period': '1y', 'interval': '1d', 'weight': 0.15}
        }
    
    def analyze(self, symbol="NQ=F"):
        """
        Analyze all timeframes
        
        Returns:
            dict with analysis results
        """
        try:
            results = {}
            
            for tf_name, tf_config in self.timeframes.items():
                trend = self._analyze_timeframe(
                    symbol, 
                    tf_config['period'], 
                    tf_config['interval']
                )
                results[tf_name] = {
                    'trend': trend,
                    'weight': tf_config['weight']
                }
            
            # Calculate overall alignment
            alignment = self._calculate_alignment(results)
            
            return {
                'timeframes': results,
                'alignment': alignment,
                'score_boost': self._calculate_score_boost(alignment),
                'summary': self._generate_summary(results, alignment)
            }
            
        except Exception as e:
            logger.error(f"Multi-timeframe analysis failed: {e}")
            return self._fallback_analysis()
    
    def _analyze_timeframe(self, symbol, period, interval):
        """
        Analyze single timeframe
        
        Returns:
            'BULLISH', 'BEARISH', or 'NEUTRAL'
        """
        try:
            # Download data
            data = yf.download(symbol, period=period, interval=interval, progress=False)
            
            if data.empty:
                return 'NEUTRAL'
            
            # Calculate indicators
            close = data['Close']
            
            # Simple Moving Averages
            sma_fast = close.rolling(10).mean()
            sma_slow = close.rolling(20).mean()
            
            # Current values
            current_price = close.iloc[-1]
            current_sma_fast = sma_fast.iloc[-1]
            current_sma_slow = sma_slow.iloc[-1]
            
            # Trend determination
            bullish_signals = 0
            bearish_signals = 0
            
            # 1. Price vs SMAs
            if current_price > current_sma_fast:
                bullish_signals += 1
            else:
                bearish_signals += 1
            
            if current_price > current_sma_slow:
                bullish_signals += 1
            else:
                bearish_signals += 1
            
            # 2. SMA crossover
            if current_sma_fast > current_sma_slow:
                bullish_signals += 1
            else:
                bearish_signals += 1
            
            # 3. Recent price action (last 5 candles)
            recent_change = (close.iloc[-1] - close.iloc[-5]) / close.iloc[-5]
            if recent_change > 0.002:  # 0.2% up
                bullish_signals += 1
            elif recent_change < -0.002:  # 0.2% down
                bearish_signals += 1
            
            # Determine trend
            if bullish_signals >= 3:
                return 'BULLISH'
            elif bearish_signals >= 3:
                return 'BEARISH'
            else:
                return 'NEUTRAL'
                
        except Exception as e:
            logger.warning(f"Timeframe analysis failed for {interval}: {e}")
            return 'NEUTRAL'
    
    def _calculate_alignment(self, results):
        """
        Calculate how aligned the timeframes are
        
        Returns:
            dict with alignment metrics
        """
        trends = [tf['trend'] for tf in results.values()]
        
        bullish_count = trends.count('BULLISH')
        bearish_count = trends.count('BEARISH')
        neutral_count = trends.count('NEUTRAL')
        total = len(trends)
        
        # Calculate weighted alignment
        weighted_score = 0
        for tf_name, tf_data in results.items():
            if tf_data['trend'] == 'BULLISH':
                weighted_score += tf_data['weight']
            elif tf_data['trend'] == 'BEARISH':
                weighted_score -= tf_data['weight']
        
        # Determine overall direction
        if weighted_score > 0.3:
            direction = 'BULLISH'
        elif weighted_score < -0.3:
            direction = 'BEARISH'
        else:
            direction = 'NEUTRAL'
        
        # Calculate alignment percentage
        if direction == 'BULLISH':
            alignment_pct = (bullish_count / total) * 100
        elif direction == 'BEARISH':
            alignment_pct = (bearish_count / total) * 100
        else:
            alignment_pct = (neutral_count / total) * 100
        
        return {
            'direction': direction,
            'percentage': alignment_pct,
            'bullish_count': bullish_count,
            'bearish_count': bearish_count,
            'neutral_count': neutral_count,
            'weighted_score': weighted_score,
            'strength': self._get_strength(alignment_pct)
        }
    
    def _get_strength(self, alignment_pct):
        """Get strength label"""
        if alignment_pct >= 80:
            return 'VERY STRONG'
        elif alignment_pct >= 60:
            return 'STRONG'
        elif alignment_pct >= 40:
            return 'MODERATE'
        else:
            return 'WEAK'
    
    def _calculate_score_boost(self, alignment):
        """
        Calculate score boost based on alignment
        
        Returns:
            int: Points to add to AI score
        """
        alignment_pct = alignment['percentage']
        direction = alignment['direction']
        
        if direction == 'NEUTRAL':
            return 0
        
        # Strong alignment = bigger boost
        if alignment_pct >= 80:
            return 15
        elif alignment_pct >= 60:
            return 10
        elif alignment_pct >= 40:
            return 5
        else:
            return 0
    
    def _generate_summary(self, results, alignment):
        """Generate human-readable summary"""
        summary = []
        
        for tf_name, tf_data in results.items():
            emoji = "✅" if tf_data['trend'] == 'BULLISH' else "❌" if tf_data['trend'] == 'BEARISH' else "⚠️"
            summary.append(f"{tf_name}: {tf_data['trend']} {emoji}")
        
        return "\n".join(summary)
    
    def _fallback_analysis(self):
        """Fallback when analysis fails"""
        return {
            'timeframes': {},
            'alignment': {
                'direction': 'NEUTRAL',
                'percentage': 0,
                'strength': 'UNKNOWN'
            },
            'score_boost': 0,
            'summary': 'Multi-timeframe analysis unavailable'
        }


if __name__ == "__main__":
    # Test multi-timeframe analysis
    logging.basicConfig(level=logging.INFO)
    
    print("="*60)
    print("MULTI-TIMEFRAME ANALYSIS TEST")
    print("="*60)
    
    analyzer = MultiTimeframeAnalyzer()
    
    print("\nAnalyzing NQ across all timeframes...")
    results = analyzer.analyze()
    
    print("\n📊 TIMEFRAME ANALYSIS:")
    print(results['summary'])
    
    print(f"\n📈 ALIGNMENT:")
    print(f"Direction: {results['alignment']['direction']}")
    print(f"Percentage: {results['alignment']['percentage']:.0f}%")
    print(f"Strength: {results['alignment']['strength']}")
    print(f"Score Boost: +{results['score_boost']} points")
    
    print("\n" + "="*60)
