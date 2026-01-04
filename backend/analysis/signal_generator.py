"""
Autonomous Signal Generator
Analyzes market and generates BUY/SELL signals automatically
"""

import yfinance as yf
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import logging
from typing import Dict, Optional

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
            direction = self._determine_direction(indicators, data)
            
            if direction is None:
                logger.info("No clear signal - market conditions not favorable")
                return None
            
            # Calculate entry, stop, targets
            signal = self._calculate_levels(direction, data, indicators)
            
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
        
        return indicators
    
    def _determine_direction(self, indicators: Dict, data: pd.DataFrame) -> Optional[str]:
        """
        Determine if we should go LONG or SHORT
        
        Returns:
            'LONG', 'SHORT', or None
        """
        current_price = indicators['current_price']
        ema20 = indicators['ema20']
        ema50 = indicators['ema50']
        ema200 = indicators['ema200']
        rsi = indicators['rsi']
        volume_ratio = indicators['volume_ratio']
        trend_strength = indicators['trend_strength']
        
        # Count bullish and bearish signals
        bullish_signals = 0
        bearish_signals = 0
        
        # 1. EMA Alignment
        if current_price > ema20 > ema50:
            bullish_signals += 2
        elif current_price < ema20 < ema50:
            bearish_signals += 2
        
        # 2. Price vs EMA200 (long-term trend)
        if current_price > ema200:
            bullish_signals += 1
        else:
            bearish_signals += 1
        
        # 3. RSI
        if 30 < rsi < 50:  # Oversold but recovering
            bullish_signals += 1
        elif 50 < rsi < 70:  # Overbought but not extreme
            bearish_signals += 1
        
        # 4. Volume confirmation
        if volume_ratio > 1.2:  # High volume
            if current_price > indicators['prev_close']:
                bullish_signals += 1
            else:
                bearish_signals += 1
        
        # 5. Recent price action
        recent_candles = data['Close'].tail(5)
        if recent_candles.is_monotonic_increasing:
            bullish_signals += 1
        elif recent_candles.is_monotonic_decreasing:
            bearish_signals += 1
        
        # 6. Trend strength (only trade strong trends)
        if trend_strength < 1.5:
            logger.info("Trend too weak - no signal")
            return None
        
        # Decision
        total_signals = bullish_signals + bearish_signals
        if total_signals == 0:
            return None
        
        bullish_pct = (bullish_signals / total_signals) * 100
        
        # Need strong conviction (≥70%)
        if bullish_pct >= 70:
            logger.info(f"LONG signal: {bullish_signals} bullish vs {bearish_signals} bearish")
            return "LONG"
        elif bullish_pct <= 30:
            logger.info(f"SHORT signal: {bearish_signals} bearish vs {bullish_signals} bullish")
            return "SHORT"
        else:
            logger.info(f"No clear signal: {bullish_pct:.0f}% bullish")
            return None
    
    def _calculate_levels(self, direction: str, data: pd.DataFrame, indicators: Dict) -> Dict:
        """Calculate entry, stop, and target levels"""
        current_price = indicators['current_price']
        atr = indicators['atr']
        
        # Entry at current price
        entry = current_price
        
        # Stop loss (2 ATR away)
        if direction == "LONG":
            stop = entry - (2 * atr)
            target1 = entry + (2 * atr * 2)  # 2:1 R/R
            target2 = entry + (2 * atr * 4)  # 4:1 R/R
        else:  # SHORT
            stop = entry + (2 * atr)
            target1 = entry - (2 * atr * 2)
            target2 = entry - (2 * atr * 4)
        
        return {
            'symbol': 'NQ',
            'direction': direction,
            'entry': float(entry),
            'stop': float(stop),
            'target1': float(target1),
            'target2': float(target2),
            'rsi': float(indicators['rsi']),
            'atr': float(atr),
            'volume_ratio': float(indicators['volume_ratio']),
            'timestamp': datetime.now().isoformat(),
            'source': 'autonomous'
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


class AutomousTrader:
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
        print("\n✅ SIGNAL GENERATED:")
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
