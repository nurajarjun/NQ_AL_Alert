"""
Global Trading Manager
Handles 24/5 trading sessions, extended hours, and global market context.
"""
import logging
from datetime import datetime, time
import pytz
import pandas as pd

logger = logging.getLogger(__name__)

class GlobalMarketManager:
    """Manages global trading sessions and time-based logic"""
    
    def __init__(self):
        self.timezone = pytz.timezone('US/Eastern')
        
        # Define Sessions
        self.SESSIONS = {
            'ASIA': (time(18, 0), time(3, 0)),    # 6PM - 3AM ET
            'LONDON': (time(3, 0), time(9, 30)),  # 3AM - 9:30AM ET
            'NY_AM': (time(9, 30), time(12, 0)),  # 9:30AM - 12PM ET
            'NY_PM': (time(12, 0), time(16, 0)),  # 12PM - 4PM ET
            'POST': (time(16, 0), time(17, 0))    # 4PM - 5PM ET
        }
    
    def get_current_session(self, current_time=None):
        """Get the current market session name"""
        if current_time is None:
            current_time = datetime.now(self.timezone).time()
            
        # Linear check (simple implementation)
        # Note: Handling overnight (18:00 - 03:00) requires crossing midnight check
        
        t = current_time
        
        # ASIA: 18:00 - 23:59 OR 00:00 - 03:00
        if t >= time(18, 0) or t < time(3, 0):
            return 'ASIA'
            
        if t >= time(3, 0) and t < time(9, 30):
            return 'LONDON'
            
        if t >= time(9, 30) and t < time(12, 0):
            return 'NY_AM'
            
        if t >= time(12, 0) and t < time(16, 0):
            return 'NY_PM'
            
        if t >= time(16, 0) and t < time(17, 0):
            return 'POST'
            
        return 'MAINTENANCE'

    def get_session_details(self, current_time=None):
        """Get full session details including quality and volume expectations"""
        session = self.get_current_session(current_time)
        
        details = {
            'session': session,
            'quality': 'NORMAL',
            'volume_expectation': 'NORMAL',
            'recommendation': 'Standard trading conditions'
        }
        
        if session == 'ASIA':
            details.update({
                'quality': 'LOW',
                'volume_expectation': 'LOW',
                'recommendation': '⚠️ Low volume, expect range-bound PA or slow trends.'
            })
        elif session == 'LONDON':
            details.update({
                'quality': 'HIGH',
                'volume_expectation': 'HIGH',
                'recommendation': '✅ High volatility expected on open. Good for trends.'
            })
        elif session == 'NY_AM':
            details.update({
                'quality': 'PRIME',
                'volume_expectation': 'MAX',
                'recommendation': '🔥 Best time for trading. Highest liquidity.'
            })
        elif session == 'NY_PM':
            details.update({
                'quality': 'NORMAL',
                'volume_expectation': 'MEDIUM',
                'recommendation': 'Watch for late-day reversals or trend continuations.'
            })
        elif session == 'POST':
            details.update({
                'quality': 'LOW',
                'volume_expectation': 'LOW',
                'recommendation': 'Closing bell over. Spreads may widen.'
            })
        
        return details

    def is_market_open(self):
        """Is the global market open for trading?"""
        # Crypto is 24/7, Futures 24/5 (closed Fri 5PM - Sun 6PM ET)
        # Simple RTH check for now, upgrade later
        return True # Stub
