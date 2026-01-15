"""
Autonomous Signal Generator
Analyzes market and generates BUY/SELL signals automatically
"""

import yfinance as yf
import pandas as pd
import pandas_ta as ta
import numpy as np
from datetime import datetime, timedelta
import logging
import sys
from typing import Dict, Optional, Tuple

logger = logging.getLogger(__name__)


class SignalGenerator:
    """Generates autonomous trading signals for NQ futures"""
    
    def __init__(self):
        self.symbol = "NQ=F"  # NQ Futures
        self.timeframe = "5m"  # 5-minute candles
        
    def generate_signal(self) -> Optional[Dict]:
        """
        Analyze market and generate autonomous signal
        
        Returns:
            dict with signal data or None if no signal
        """
        try:
            logger.info("Generating autonomous signal...")
            
            # Get market data
            data = self._get_market_data()
            if data is None or data.empty:
                return None
            
            # Calculate indicators
            indicators = self._calculate_indicators(data)
            
            # Determine direction
            direction, context = self._determine_direction(indicators, data)
            
            if direction is None:
                logger.info("No clear signal - market conditions not favorable")
                return None
            
            # Calculate entry, stop, targets
            signal = self._calculate_levels(direction, data, indicators, context)
            
            logger.info(f"✅ Signal generated: {direction} at {signal['entry']}")
            
            return signal
            
        except Exception as e:
            logger.error(f"Signal generation failed: {e}")
            return None
    
    def _get_market_data(self) -> Optional[pd.DataFrame]:
        """Get recent market data"""
        try:
            # Download recent data
            ticker = yf.Ticker(self.symbol)
            data = ticker.history(period="5d", interval=self.timeframe)
            
            if data.empty:
                logger.warning("No market data available")
                return None
            
            return data
            
        except Exception as e:
            logger.error(f"Failed to get market data: {e}")
            return None
    
    def _calculate_indicators(self, data: pd.DataFrame) -> Dict:
        """Calculate technical indicators"""
        indicators = {}
        
        # RSI
        delta = data['Close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
        rs = gain / loss
        indicators['rsi'] = 100 - (100 / (1 + rs)).iloc[-1]
        
        # ATR
        high_low = data['High'] - data['Low']
        high_close = np.abs(data['High'] - data['Close'].shift())
        low_close = np.abs(data['Low'] - data['Close'].shift())
        ranges = pd.concat([high_low, high_close, low_close], axis=1)
        true_range = ranges.max(axis=1)
        indicators['atr'] = true_range.rolling(14).mean().iloc[-1]
        
        # Moving Averages
        indicators['ema20'] = data['Close'].ewm(span=20).mean().iloc[-1]
        indicators['ema50'] = data['Close'].ewm(span=50).mean().iloc[-1]
        indicators['ema200'] = data['Close'].ewm(span=200).mean().iloc[-1]
        
        # Volume
        indicators['volume_ratio'] = data['Volume'].iloc[-1] / data['Volume'].rolling(20).mean().iloc[-1]
        
        # Price action
        indicators['current_price'] = data['Close'].iloc[-1]
        indicators['prev_close'] = data['Close'].iloc[-2]
        indicators['high'] = data['High'].iloc[-1]
        indicators['low'] = data['Low'].iloc[-1]
        
        # Trend strength
        indicators['trend_strength'] = abs(indicators['ema20'] - indicators['ema50']) / indicators['atr']
        
        # ADX (Chop Indicator)
        try:
            adx_df = ta.adx(data['High'], data['Low'], data['Close'], length=14)
            # ADX_14, DMP_14, DMN_14
            if adx_df is not None and not adx_df.empty:
               indicators['adx'] = adx_df['ADX_14'].iloc[-1]
            else:
               indicators['adx'] = 25 # Default if fail
        except Exception as e:
            logger.warning(f"ADX calculation failed: {e}")
            indicators['adx'] = 25
        
        return indicators
    
    def _determine_direction(self, indicators: Dict, data: pd.DataFrame) -> Tuple[Optional[str], Dict]:
        """
        Determine direction and return context data
        Returns: (Direction, ContextDict)
        """
        # ... (keep existing indicator unpacking) ...
        current_price = indicators['current_price']
        ema20 = indicators['ema20']
        ema50 = indicators['ema50']
        ema200 = indicators['ema200']
        rsi = indicators['rsi']
        volume_ratio = indicators['volume_ratio']
        trend_strength = indicators['trend_strength']
        
        bullish_signals = 0
        bearish_signals = 0
        
        context = {
            'expert_bias': 'NEUTRAL',
            'news_sentiment': {},
            'economic_events': []
        }

        # 1. EMA Alignment
        if current_price > ema20 > ema50: bullish_signals += 2
        elif current_price < ema20 < ema50: bearish_signals += 2
        
        # 2. Price vs EMA200
        if current_price > ema200: bullish_signals += 1
        else: bearish_signals += 1
        
        # 3. RSI
        if 30 < rsi < 50: bullish_signals += 1
        elif 50 < rsi < 70: bearish_signals += 1
        
        # 4. Volume
        if volume_ratio > 1.2:
            if current_price > indicators['prev_close']: bullish_signals += 1
            else: bearish_signals += 1
        
        # 5. Price Action
        recent_candles = data['Close'].tail(5)
        if recent_candles.is_monotonic_increasing: bullish_signals += 1
        elif recent_candles.is_monotonic_decreasing: bearish_signals += 1
        
        # 6. Trend Strength
        if trend_strength < 1.0: pass
        
        # --- EXPERT CONTEXT ---
        try:
            sys.path.insert(0, 'backend')
            from analysis.expert_input import ExpertContext
            expert = ExpertContext()
            expert.refresh() # Force reload from disk
            bias = expert.data.get('bias', 'NEUTRAL').upper()
            context['expert_bias'] = bias
            
            if bias == "LONG":
                bullish_signals += 1
            elif bias == "SHORT":
                bearish_signals += 1
        except Exception: pass

        # --- NEWS SENTIMENT ---
        try:
            from analysis.economic_news import NewsAnalyzer
            news = NewsAnalyzer()
            news_data = news.get_market_news()
            context['news_sentiment'] = news_data.get('sentiment', {})
            
            sent_dir = context['news_sentiment'].get('direction', 'NEUTRAL')
            sent_score = context['news_sentiment'].get('score', 50)
            
            if sent_dir == "BULLISH" and sent_score > 65: bullish_signals += 0.5
            elif sent_dir == "BEARISH" and sent_score < 35: bearish_signals += 0.5
        except Exception: pass
        
        # --- ECONOMIC EVENTS ---
        try:
            from analysis.economic_news import EconomicCalendar
            cal = EconomicCalendar()
            events = cal.get_todays_events()
            # Flatten for simpler context
            context['economic_events'] = events.get('high_impact', []) + events.get('tech_earnings', [])
            context['risk_level'] = events.get('risk_level', 'NORMAL')
        except Exception: pass

        # Decision
        total_signals = bullish_signals + bearish_signals
        if total_signals == 0:
            return None, context
        
        # --- CHOP FILTER (ADX) ---
        sys.path.insert(0, 'backend')
        from utils.config import ConfigManager
        config = ConfigManager()
        adx_threshold = config.get('adx_threshold', 25) # Default 25
        
        adx = indicators.get('adx', 25)
        context['adx'] = adx # For Telegram
        
        if adx < adx_threshold:
            logger.info(f"⛔ Signal Filtered: ADX {adx:.1f} < {adx_threshold} (CHOP)")
            # Add to context so user knows why
            context['filter_reason'] = f"Market is Choppy (ADX {adx:.1f} < {adx_threshold})"
            return None, context

        bullish_pct = (bullish_signals / total_signals) * 100
        from utils.config import ConfigManager
        config = ConfigManager()
        threshold = config.get('alert_threshold', 70)
        
        direction = None
        if bullish_pct >= threshold: direction = "LONG"
        elif bullish_pct <= (100 - threshold): direction = "SHORT"
        
        return direction, context

    def _calculate_levels(self, direction: str, data: pd.DataFrame, indicators: Dict, context: Dict) -> Dict:
        """Calculate levels and attach context"""
        # ... (Keep existing level calc) ...
        current_price = indicators['current_price']
        atr = indicators['atr']
        entry = current_price
        
        if direction == "LONG":
            stop = entry - (2 * atr)
            target1 = entry + (4 * atr)
            target2 = entry + (8 * atr)
        else:
            stop = entry + (2 * atr)
            target1 = entry - (4 * atr)
            target2 = entry - (8 * atr)
            
        return {
            'symbol': 'NQ',
            'direction': direction,
            'entry': float(entry),
            'stop': float(stop),
            'target1': float(target1),
            'target2': float(target2),
            'rsi': float(indicators['rsi']),
            'atr': float(indicators['atr']),
            'volume_ratio': float(indicators['volume_ratio']),
            'timestamp': datetime.now().isoformat(),
            'expert_bias': context.get('expert_bias', 'NEUTRAL'),
            'news_sentiment': context.get('news_sentiment', {}),
            'economic_context': { # Match Telegram Bot key expectation
                'risk_level': context.get('risk_level', 'NORMAL'),
                'high_impact': context.get('economic_events', [])
            }
        }
    
    def should_generate_signal(self) -> bool:
        """
        Check if we should generate a new signal
        
        Returns:
            True if conditions are right for signal generation
        """
        # Check market hours (NQ trades nearly 24/5)
        now = datetime.now()
        
        # Don't trade on weekends
        if now.weekday() >= 5:  # Saturday or Sunday
            return False
        
        # Don't trade during low liquidity hours (example)
        hour = now.hour
        if 0 <= hour < 6:  # Late night/early morning
            return False
        
        return True


class AutonomousTrader:
    """Manages autonomous trading - generates signals periodically"""
    
    def __init__(self, signal_generator: SignalGenerator, check_interval: int = 300):
        """
        Args:
            signal_generator: SignalGenerator instance
            check_interval: How often to check for signals (seconds)
        """
        self.signal_generator = signal_generator
        self.check_interval = check_interval
        self.last_signal_time = None
        self.min_signal_gap = 900  # Minimum 15 minutes between signals
    
    def should_check_for_signal(self) -> bool:
        """Check if enough time has passed since last signal"""
        if self.last_signal_time is None:
            return True
        
        time_since_last = (datetime.now() - self.last_signal_time).total_seconds()
        return time_since_last >= self.min_signal_gap
    
    def get_signal_if_ready(self) -> Optional[Dict]:
        """
        Check if we should generate a signal and do so if conditions are met
        
        Returns:
            Signal dict or None
        """
        # Check if we should even try
        if not self.signal_generator.should_generate_signal():
            return None
        
        # Check if enough time has passed
        if not self.should_check_for_signal():
            return None
        
        # Generate signal
        signal = self.signal_generator.generate_signal()
        
        if signal:
            self.last_signal_time = datetime.now()
        
        return signal


if __name__ == "__main__":
    # Test signal generator
    logging.basicConfig(level=logging.INFO)
    
    print("="*60)
    print("AUTONOMOUS SIGNAL GENERATOR TEST")
    print("="*60)
    
    generator = SignalGenerator()
    
    print("\nGenerating signal...")
    signal = generator.generate_signal()
    
    if signal:
        print("\nSIGNAL GENERATED:")
        print(f"Direction: {signal['direction']}")
        print(f"Entry: {signal['entry']:.2f}")
        print(f"Stop: {signal['stop']:.2f}")
        print(f"Target 1: {signal['target1']:.2f}")
        print(f"Target 2: {signal['target2']:.2f}")
        print(f"RSI: {signal['rsi']:.1f}")
        print(f"ATR: {signal['atr']:.1f}")
        print(f"Volume Ratio: {signal['volume_ratio']:.2f}")
    else:
        print("\n❌ No signal - market conditions not favorable")
    
    print("\n" + "="*60)
