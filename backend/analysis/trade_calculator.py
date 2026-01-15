"""
Trade Calculator
Calculates entry, stop loss, targets, support/resistance levels
"""

import pandas as pd
import numpy as np
from typing import Dict, List
import logging
import sys

logger = logging.getLogger(__name__)


class TradeCalculator:
    """Calculates complete trade setup with targets and key levels"""
    
    def __init__(self):
        self.default_atr_multiplier = 1.5  # For stop loss
        self.target1_ratio = 1.5  # Risk:Reward for T1
        self.target2_ratio = 3.0  # Risk:Reward for T2
        self.sweep_lookback = 20  # Lookback for swing points

    
    def calculate_trade_setup(self, df: pd.DataFrame, direction: str, confidence: float) -> Dict:
        """
        Calculate complete trade setup
        
        Args:
            df: DataFrame with OHLCV and indicators
            direction: 'LONG', 'SHORT', or 'NEUTRAL'
            confidence: Confidence score (0-1)
            
        Returns:
            Dict with entry, stops, targets, and key levels
        """
        try:
            if direction == 'NEUTRAL' or len(df) < 20:
                return self._fallback_setup()
            
            # Get current price and ATR
            current_price = float(df['Close'].iloc[-1])
            atr = self._calculate_atr(df)
            
            # Calculate stop loss based on ATR
            stop_distance = atr * self.default_atr_multiplier
            
            # Check for Liquidity Sweep (High Conviction Reversal)
            # sweep_signal = self.detect_liquidity_sweep(df)
            sweep_signal = None 
            is_sweep = False
            
            # if sweep_signal:
            #    direction = sweep_signal['direction']
            #    logger.info(f"🌊 Liquidity Sweep Detected! Overriding direction to {direction}")
            #    is_sweep = True
            
            # Calculate levels based on direction
            if direction in ['LONG', 'UP']:
                entry = current_price
                stop_loss = entry - stop_distance
                target1 = entry + (stop_distance * self.target1_ratio)
                target2 = entry + (stop_distance * self.target2_ratio)
                
                # If sweep, tighten stop to just below the sweep wick
                if is_sweep and sweep_signal.get('sweep_level'):
                    stop_loss = sweep_signal['sweep_level'] - (atr * 0.5) # Tighter stop on sweep
                    
            else:  # SHORT/DOWN
                entry = current_price
                stop_loss = entry + stop_distance
                target1 = entry - (stop_distance * self.target1_ratio)
                target2 = entry - (stop_distance * self.target2_ratio)
                
                # If sweep, tighten stop to just above the sweep wick
                if is_sweep and sweep_signal.get('sweep_level'):
                    stop_loss = sweep_signal['sweep_level'] + (atr * 0.5)

            
            # Calculate support and resistance levels
            support_levels = self._calculate_support_levels(df, current_price)
            resistance_levels = self._calculate_resistance_levels(df, current_price)
            
            # Calculate risk metrics
            risk_per_contract = abs(entry - stop_loss) * 20  # NQ = $20 per point
            reward_t1 = abs(target1 - entry) * 20
            reward_t2 = abs(target2 - entry) * 20
            
            # Calculate signed distances (negative for risk, positive for reward)
            if direction in ['LONG', 'UP']:
                stop_distance_signed = -(entry - stop_loss)  # Negative (risk)
                target1_distance_signed = target1 - entry    # Positive (reward)
                target2_distance_signed = target2 - entry    # Positive (reward)
            else:  # SHORT/DOWN
                stop_distance_signed = -(stop_loss - entry)  # Negative (risk)
                target1_distance_signed = entry - target1    # Positive (reward)
                target2_distance_signed = entry - target2    # Positive (reward)
            
            # Determine trade type based on target distance and ATR
            trade_type = self._determine_trade_type(
                stop_distance, 
                abs(target1 - entry),
                abs(target2 - entry),
                atr
            )
            
            # Get expected duration
            duration = self._get_expected_duration(trade_type, abs(target1 - entry), atr)
            
            return {
                'entry': round(entry, 2),
                'stop_loss': round(stop_loss, 2),
                'target1': round(target1, 2),
                'target2': round(target2, 2),
                'stop_distance': round(stop_distance_signed, 2),
                'target1_distance': round(target1_distance_signed, 2),
                'target2_distance': round(target2_distance_signed, 2),
                'support_levels': [round(s, 2) for s in support_levels],
                'resistance_levels': [round(r, 2) for r in resistance_levels],
                'risk_per_contract': round(risk_per_contract, 2),
                'reward_t1': round(reward_t1, 2),
                'reward_t2': round(reward_t2, 2),
                'risk_reward_t1': round(self.target1_ratio, 1),
                'risk_reward_t2': round(self.target2_ratio, 1),
                'atr': round(atr, 2),
                'direction': direction,
                'trade_type': trade_type,
                'trade_type': trade_type,
                'expected_duration': duration,
                'is_sweep': is_sweep,
                'sweep_details': sweep_signal if is_sweep else None
            }
            
        except Exception as e:
            logger.error(f"Error calculating trade setup: {e}")
            return self._fallback_setup()
    
    def detect_liquidity_sweep(self, df: pd.DataFrame) -> Dict:
        """
        Detect 'Liquidity Sweep' / 'Tag n Turn' patterns
        
        Logic:
        1. Find recent Swing Low/High (Support/Resistance)
        2. Check if current candle 'sweeps' it (Wick goes beyond, Body closes inside)
        """
        try:
            if len(df) < self.sweep_lookback + 2:
                return None
                
            current = df.iloc[-1]
            prev_candles = df.iloc[-self.sweep_lookback:-1]
            
            # --- Bullish Sweep (Sweep Lows) ---
            # Find significant swing low in lookback
            recent_low = prev_candles['Low'].min()
            
            # Condition: Low went below recent_low, but Close stayed above it
            if current['Low'] < recent_low and current['Close'] > recent_low:
                # Validation: Wick Size > Body Size (Hammer-like) helps confirmation
                body = abs(current['Close'] - current['Open'])
                lower_wick = current['Close'] - current['Low'] if current['Close'] > current['Open'] else current['Open'] - current['Low']
                
                if lower_wick > body: # Nice rejection wick
                    return {
                        'direction': 'LONG',
                        'sweep_level': recent_low,
                        'type': 'Bullish Liquidity Sweep'
                    }
            
            # --- Bearish Sweep (Sweep Highs) ---
            # Find significant swing high
            recent_high = prev_candles['High'].max()
            
            # Condition: High went above recent_high, but Close stayed below it
            if current['High'] > recent_high and current['Close'] < recent_high:
                # Validation: Upper wick > Body
                body = abs(current['Close'] - current['Open'])
                upper_wick = current['High'] - current['Close'] if current['Close'] > current['Open'] else current['High'] - current['Open']
                
                if upper_wick > body: # Nice rejection wick
                    return {
                        'direction': 'SHORT',
                        'sweep_level': recent_high,
                        'type': 'Bearish Liquidity Sweep'
                    }
                    
            return None
            
        except Exception as e:
            logger.error(f"Error detecting sweep: {e}")
            return None

    def _calculate_atr(self, df: pd.DataFrame, period: int = 14) -> float:
        """Calculate Average True Range"""
        try:
            # Check if ATR already calculated
            if 'ATR_14' in df.columns:
                return float(df['ATR_14'].iloc[-1])
            
            # Calculate manually
            high = df['High']
            low = df['Low']
            close = df['Close'].shift(1)
            
            tr1 = high - low
            tr2 = abs(high - close)
            tr3 = abs(low - close)
            
            tr = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
            atr = tr.rolling(window=period).mean().iloc[-1]
            
            return float(atr) if not pd.isna(atr) else 50.0  # Default fallback
            
        except Exception as e:
            logger.warning(f"ATR calculation failed: {e}")
            return 50.0  # Default ATR for NQ
    
    def _calculate_support_levels(self, df: pd.DataFrame, current_price: float) -> List[float]:
        """Calculate support levels using swing lows"""
        try:
            # Get recent lows (last 50 candles)
            recent_data = df.tail(50)
            lows = recent_data['Low'].values
            
            # Find swing lows (local minima)
            support_levels = []
            for i in range(2, len(lows) - 2):
                if lows[i] < lows[i-1] and lows[i] < lows[i-2] and \
                   lows[i] < lows[i+1] and lows[i] < lows[i+2]:
                    if lows[i] < current_price:  # Only levels below current price
                        support_levels.append(lows[i])
            
            # Sort and get top 3 closest levels
            support_levels = sorted(support_levels, reverse=True)[:3]
            
            # MERGE EXPERT LEVELS
            try:
                sys.path.insert(0, 'backend')
                from analysis.expert_input import ExpertContext
                expert_levels = ExpertContext().data.get('key_levels', {}).get('support', [])
                # Add expert levels that are below current price
                for level in expert_levels:
                    if level < current_price:
                        support_levels.append(level)
                support_levels = sorted(list(set(support_levels)), reverse=True)[:3]
            except Exception as e:
                logger.error(f"Failed to merge expert support: {e}")

            # If not enough levels, add round numbers
            if len(support_levels) < 3:
                round_level = (current_price // 50) * 50  # Round to nearest 50
                for i in range(3 - len(support_levels)):
                    support_levels.append(round_level - (50 * (i + 1)))
            
            return support_levels[:3]
            
        except Exception as e:
            logger.warning(f"Support calculation failed: {e}")
            return [current_price - 50, current_price - 100, current_price - 150]
    
    def _calculate_resistance_levels(self, df: pd.DataFrame, current_price: float) -> List[float]:
        """Calculate resistance levels using swing highs"""
        try:
            # Get recent highs (last 50 candles)
            recent_data = df.tail(50)
            highs = recent_data['High'].values
            
            # Find swing highs (local maxima)
            resistance_levels = []
            for i in range(2, len(highs) - 2):
                if highs[i] > highs[i-1] and highs[i] > highs[i-2] and \
                   highs[i] > highs[i+1] and highs[i] > highs[i+2]:
                    if highs[i] > current_price:  # Only levels above current price
                        resistance_levels.append(highs[i])
            
            # Sort and get top 3 closest levels
            resistance_levels = sorted(resistance_levels)[:3]
            
            # MERGE EXPERT LEVELS
            try:
                sys.path.insert(0, 'backend')
                from analysis.expert_input import ExpertContext
                expert_levels = ExpertContext().data.get('key_levels', {}).get('resistance', [])
                # Add expert levels that are above current price
                for level in expert_levels:
                    if level > current_price:
                        resistance_levels.append(level)
                resistance_levels = sorted(list(set(resistance_levels)))[:3]
            except:
                pass

            # If not enough levels, add round numbers
            if len(resistance_levels) < 3:
                round_level = ((current_price // 50) + 1) * 50  # Round up to nearest 50
                for i in range(3 - len(resistance_levels)):
                    resistance_levels.append(round_level + (50 * i))
            
            return resistance_levels[:3]
            
        except Exception as e:
            logger.warning(f"Resistance calculation failed: {e}")
            return [current_price + 50, current_price + 100, current_price + 150]
    
    def _determine_trade_type(self, stop_distance, target1_distance, target2_distance, atr):
        """
        Determine if this is a Scalp, Day Trade, or Swing Trade
        
        Based on:
        - Target distance relative to ATR
        - Risk/Reward profile
        """
        # Calculate target as multiple of ATR
        t1_atr_multiple = target1_distance / atr if atr > 0 else 0
        t2_atr_multiple = target2_distance / atr if atr > 0 else 0
        
        # Classification logic
        if t1_atr_multiple < 1.0:
            # Very tight targets = Scalp
            return "SCALP"
        elif t1_atr_multiple < 2.0 and t2_atr_multiple < 4.0:
            # Moderate targets, achievable same day = Day Trade
            return "DAY TRADE"
        else:
            # Large targets, may need overnight = Swing Trade
            return "SWING TRADE"
    
    def _get_expected_duration(self, trade_type, target1_distance, atr):
        """Get expected time to reach target"""
        durations = {
            "SCALP": "15-60 minutes",
            "DAY TRADE": "2-6 hours",
            "SWING TRADE": "1-3 days"
        }
        
        # Add specific guidance
        if trade_type == "SCALP":
            return "15-60 min (Quick in/out)"
        elif trade_type == "DAY TRADE":
            return "2-6 hours (Close before 4 PM)"
        else:
            return "1-3 days (Hold overnight)"
    
    def _fallback_setup(self) -> Dict:
        """Fallback when calculation fails"""
        return {
            'entry': 0,
            'stop_loss': 0,
            'target1': 0,
            'target2': 0,
            'stop_distance': 0,
            'target1_distance': 0,
            'target2_distance': 0,
            'support_levels': [],
            'resistance_levels': [],
            'risk_per_contract': 0,
            'reward_t1': 0,
            'reward_t2': 0,
            'risk_reward_t1': 0,
            'risk_reward_t2': 0,
            'atr': 0,
            'direction': 'NEUTRAL',
            'trade_type': 'UNKNOWN',
            'expected_duration': 'Unknown'
        }
    
    def format_trade_setup(self, setup: Dict) -> str:
        """Format trade setup for display"""
        if setup['entry'] == 0:
            return "Trade setup unavailable"
        
        direction_emoji = "🟢" if setup['direction'] in ['LONG', 'UP'] else "🔴"
        
        # Trade type emoji
        type_emoji = {
            'SCALP': '⚡',
            'DAY TRADE': '📊',
            'SWING TRADE': '📈'
        }.get(setup['trade_type'], '❓')
        
        lines = [
            f"{direction_emoji} **TRADE SETUP ({setup['direction']})**",
            f"{'🌊 **LIQUIDITY SWEEP DETECTED** 🌊' if setup.get('is_sweep') else ''}",
            f"{type_emoji} **Type: {setup['trade_type']}** ({setup['expected_duration']})",
            f"",
            f"📍 Entry: {setup['entry']:,.2f}",
            f"🛑 Stop: {setup['stop_loss']:,.2f} ({setup['stop_distance']:+.0f} pts)",
            f"🎯 T1: {setup['target1']:,.2f} ({setup['target1_distance']:+.0f} pts) [{setup['risk_reward_t1']}R]",
            f"🎯 T2: {setup['target2']:,.2f} ({setup['target2_distance']:+.0f} pts) [{setup['risk_reward_t2']}R]",
            f"",
            f"📊 **KEY LEVELS**",
            f"Support: {' | '.join([f'{s:,.0f}' for s in setup['support_levels']])}",
            f"Resistance: {' | '.join([f'{r:,.0f}' for r in setup['resistance_levels']])}",
            f"",
            f"💰 Risk: ${setup['risk_per_contract']:,.0f}/contract",
            f"📈 ATR: {setup['atr']:.1f} pts"
        ]
        
        return "\n".join(lines)


if __name__ == "__main__":
    # Test the calculator
    import yfinance as yf
    
    logging.basicConfig(level=logging.INFO)
    
    print("Testing Trade Calculator...")
    
    # Download sample data
    nq = yf.download("NQ=F", period="5d", interval="1h")
    
    calculator = TradeCalculator()
    
    # Test LONG setup
    setup = calculator.calculate_trade_setup(nq, "LONG", 0.85)
    print("\n" + "="*60)
    print(calculator.format_trade_setup(setup))
    print("="*60)
