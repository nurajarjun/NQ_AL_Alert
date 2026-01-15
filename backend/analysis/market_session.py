"""
Market Session Analyzer
Analyzes current market session and provides trading recommendations
"""

from datetime import datetime, time
import pytz
import logging

logger = logging.getLogger(__name__)


class MarketSessionAnalyzer:
    """Analyzes market sessions and trading conditions"""
    
    def __init__(self):
        self.et_tz = pytz.timezone('America/New_York')
        
        # Define NQ futures trading sessions
        self.sessions = {
            'pre_market': {'start': time(6, 0), 'end': time(9, 30), 'quality': 'MEDIUM'},
            'market_open': {'start': time(9, 30), 'end': time(11, 0), 'quality': 'EXCELLENT'},
            'mid_day': {'start': time(11, 0), 'end': time(14, 0), 'quality': 'GOOD'},
            'power_hour': {'start': time(14, 0), 'end': time(16, 0), 'quality': 'EXCELLENT'},
            'after_hours': {'start': time(16, 0), 'end': time(18, 0), 'quality': 'MEDIUM'},
            'overnight': {'start': time(18, 0), 'end': time(23, 59), 'quality': 'LOW'},
            'asian_session': {'start': time(0, 0), 'end': time(6, 0), 'quality': 'LOW'}
        }
    
    def get_current_session(self):
        """Get current trading session and analysis"""
        try:
            # Get current time in ET
            now_et = datetime.now(self.et_tz)
            current_time = now_et.time()
            day_of_week = now_et.weekday()  # 0=Monday, 6=Sunday
            
            # Check if weekend
            is_weekend = day_of_week >= 5  # Saturday or Sunday
            
            # Determine session
            session_name = self._get_session_name(current_time)
            session_info = self.sessions.get(session_name, {})
            
            # Get trading recommendation
            recommendation = self._get_trading_recommendation(
                session_name, 
                session_info.get('quality', 'UNKNOWN'),
                is_weekend,
                current_time
            )
            
            return {
                'current_time_et': now_et.strftime('%Y-%m-%d %H:%M:%S %Z'),
                'session': session_name,
                'quality': session_info.get('quality', 'UNKNOWN'),
                'is_weekend': is_weekend,
                'is_market_open': not is_weekend and session_name in ['market_open', 'mid_day', 'power_hour'],
                'recommendation': recommendation,
                'volume_expectation': self._get_volume_expectation(session_name, is_weekend),
                'volatility_expectation': self._get_volatility_expectation(session_name),
                'optimal_for': self._get_optimal_strategy(session_name)
            }
            
        except Exception as e:
            logger.error(f"Error analyzing market session: {e}")
            return self._fallback_session()
    
    def _get_session_name(self, current_time):
        """Determine which session we're in"""
        for session_name, session_data in self.sessions.items():
            start = session_data['start']
            end = session_data['end']
            
            # Handle overnight session that crosses midnight
            if session_name == 'overnight':
                if current_time >= start or current_time <= time(23, 59):
                    return session_name
            elif session_name == 'asian_session':
                if current_time >= start and current_time < time(6, 0):
                    return session_name
            else:
                if start <= current_time < end:
                    return session_name
        
        return 'unknown'
    
    def _get_trading_recommendation(self, session, quality, is_weekend, current_time):
        """Get specific trading recommendation"""
        if is_weekend:
            if current_time < time(18, 0):  # Before Sunday 6 PM ET
                return "⏸️ MARKET CLOSED - Wait for Sunday 6 PM ET open"
            else:
                return "✅ OVERNIGHT SESSION - Low volume, use caution"
        
        recommendations = {
            'market_open': "🔥 PRIME TIME - High volatility, best setups",
            'power_hour': "⚡ POWER HOUR - Strong momentum, trend following",
            'mid_day': "✅ ACTIVE TRADING - Normal conditions",
            'pre_market': "⚠️ PRE-MARKET - Reduced liquidity, wider spreads",
            'after_hours': "⚠️ AFTER HOURS - Lower volume, swing setups only",
            'overnight': "🌙 OVERNIGHT - Very low volume, experienced traders only",
            'asian_session': "😴 ASIAN SESSION - Minimal volume, avoid unless experienced"
        }
        
        return recommendations.get(session, "⚠️ UNKNOWN SESSION - Use caution")
    
    def _get_volume_expectation(self, session, is_weekend):
        """Expected volume level"""
        if is_weekend:
            return "VERY LOW"
        
        volume_map = {
            'market_open': 'VERY HIGH',
            'power_hour': 'VERY HIGH',
            'mid_day': 'HIGH',
            'pre_market': 'MEDIUM',
            'after_hours': 'LOW',
            'overnight': 'VERY LOW',
            'asian_session': 'VERY LOW'
        }
        return volume_map.get(session, 'UNKNOWN')
    
    def _get_volatility_expectation(self, session):
        """Expected volatility level"""
        volatility_map = {
            'market_open': 'HIGH',
            'power_hour': 'HIGH',
            'mid_day': 'MEDIUM',
            'pre_market': 'MEDIUM',
            'after_hours': 'LOW',
            'overnight': 'LOW',
            'asian_session': 'VERY LOW'
        }
        return volatility_map.get(session, 'UNKNOWN')
    
    def _get_optimal_strategy(self, session):
        """What trading style works best"""
        strategy_map = {
            'market_open': 'Scalping, Breakouts, Momentum',
            'power_hour': 'Trend Following, Breakouts',
            'mid_day': 'Range Trading, Mean Reversion',
            'pre_market': 'Gap Plays, News Trading',
            'after_hours': 'Swing Setups, Overnight Holds',
            'overnight': 'Swing Trading Only',
            'asian_session': 'Avoid or Swing Only'
        }
        return strategy_map.get(session, 'Unknown')
    
    def _fallback_session(self):
        """Fallback when analysis fails"""
        return {
            'current_time_et': 'Unknown',
            'session': 'unknown',
            'quality': 'UNKNOWN',
            'is_weekend': False,
            'is_market_open': False,
            'recommendation': '⚠️ Unable to determine session - Use caution',
            'volume_expectation': 'UNKNOWN',
            'volatility_expectation': 'UNKNOWN',
            'optimal_for': 'Unknown'
        }
    
    def format_session_info(self, session_data):
        """Format session info for display"""
        lines = [
            f"⏰ **MARKET SESSION**",
            f"Time (ET): {session_data['current_time_et']}",
            f"Session: {session_data['session'].replace('_', ' ').title()}",
            f"Quality: {session_data['quality']}",
            f"",
            f"📊 **CONDITIONS**",
            f"Volume: {session_data['volume_expectation']}",
            f"Volatility: {session_data['volatility_expectation']}",
            f"Best For: {session_data['optimal_for']}",
            f"",
            f"💡 {session_data['recommendation']}"
        ]
        
        return "\n".join(lines)


if __name__ == "__main__":
    # Test the analyzer
    logging.basicConfig(level=logging.INFO)
    
    print("="*60)
    print("MARKET SESSION ANALYZER TEST")
    print("="*60)
    
    analyzer = MarketSessionAnalyzer()
    session = analyzer.get_current_session()
    
    print("\n" + analyzer.format_session_info(session))
    print("\n" + "="*60)
