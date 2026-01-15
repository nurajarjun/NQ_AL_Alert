"""
Earnings Calendar for NQ Top Holdings
Filters trades during earnings weeks for major NQ components
"""
import os
import logging
from datetime import datetime, timedelta
from typing import Tuple, Optional, List, Dict
import yfinance as yf
import json
from pathlib import Path

logger = logging.getLogger(__name__)

class EarningsCalendar:
    """
    Tracks earnings for top NQ holdings to avoid trading during earnings volatility
    """
    
    # Top 5 NQ holdings (represent ~42% of index)
    NQ_TOP_HOLDINGS = {
        'AAPL': 'Apple',
        'MSFT': 'Microsoft', 
        'NVDA': 'Nvidia',
        'GOOGL': 'Alphabet',
        'AMZN': 'Amazon'
    }
    
    def __init__(self, cache_dir: str = "backend/data/calendar"):
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.earnings_cache: Dict[str, Dict] = {}
        self.cache_file = self.cache_dir / "earnings_dates.json"
        self._load_cache()
    
    def _load_cache(self):
        """Load cached earnings dates from disk"""
        try:
            if self.cache_file.exists():
                with open(self.cache_file, 'r') as f:
                    self.earnings_cache = json.load(f)
                logger.info(f"Loaded earnings cache for {len(self.earnings_cache)} symbols")
        except Exception as e:
            logger.warning(f"Failed to load earnings cache: {e}")
            self.earnings_cache = {}
    
    def _save_cache(self):
        """Save earnings cache to disk"""
        try:
            with open(self.cache_file, 'w') as f:
                json.dump(self.earnings_cache, f, indent=2)
        except Exception as e:
            logger.error(f"Failed to save earnings cache: {e}")
    
    async def is_earnings_week(self, timestamp: datetime) -> Tuple[bool, Optional[str]]:
        """
        Check if any top NQ holding reports earnings within 3 days
        
        Args:
            timestamp: Time to check
            
        Returns:
            (is_earnings_week, symbol): True if earnings week, symbol reporting
        """
        for symbol, name in self.NQ_TOP_HOLDINGS.items():
            next_earnings = await self.get_next_earnings(symbol)
            
            if next_earnings:
                days_until = (next_earnings - timestamp.date()).days
                
                # Skip trades 3 days before and 1 day after earnings
                if -1 <= days_until <= 3:
                    logger.info(f"Earnings Filter: {name} ({symbol}) reports in {days_until} days")
                    return True, f"{name} ({symbol})"
        
        return False, None
    
    async def get_next_earnings(self, symbol: str) -> Optional[datetime.date]:
        """
        Get next earnings date for a symbol
        
        Args:
            symbol: Stock ticker
            
        Returns:
            Next earnings date or None
        """
        # Check cache first (refresh daily)
        today = datetime.now().date().isoformat()
        
        if symbol in self.earnings_cache:
            cache_entry = self.earnings_cache[symbol]
            if cache_entry.get('cached_date') == today:
                earnings_str = cache_entry.get('next_earnings')
                if earnings_str:
                    return datetime.fromisoformat(earnings_str).date()
                return None
        
        # Fetch from Yahoo Finance
        try:
            ticker = yf.Ticker(symbol)
            calendar = ticker.calendar
            
            if calendar is not None and 'Earnings Date' in calendar:
                # Yahoo returns a range, take the first date
                earnings_dates = calendar['Earnings Date']
                if len(earnings_dates) > 0:
                    next_date = earnings_dates[0]
                    
                    # Cache the result
                    self.earnings_cache[symbol] = {
                        'cached_date': today,
                        'next_earnings': next_date.isoformat() if hasattr(next_date, 'isoformat') else str(next_date),
                        'company': self.NQ_TOP_HOLDINGS[symbol]
                    }
                    self._save_cache()
                    
                    return next_date.date() if hasattr(next_date, 'date') else next_date
        
        except Exception as e:
            logger.warning(f"Failed to fetch earnings for {symbol}: {e}")
        
        # Cache miss/failure
        self.earnings_cache[symbol] = {
            'cached_date': today,
            'next_earnings': None,
            'company': self.NQ_TOP_HOLDINGS[symbol]
        }
        self._save_cache()
        
        return None
    
    def get_upcoming_earnings(self, days_ahead: int = 14) -> List[Dict]:
        """
        Get all upcoming earnings in next N days
        
        Args:
            days_ahead: Number of days to look ahead
            
        Returns:
            List of earnings events
        """
        upcoming = []
        now = datetime.now().date()
        
        for symbol, name in self.NQ_TOP_HOLDINGS.items():
            if symbol in self.earnings_cache:
                earnings_str = self.earnings_cache[symbol].get('next_earnings')
                if earnings_str:
                    earnings_date = datetime.fromisoformat(earnings_str).date()
                    days_until = (earnings_date - now).days
                    
                    if 0 <= days_until <= days_ahead:
                        upcoming.append({
                            'symbol': symbol,
                            'company': name,
                            'date': earnings_date,
                            'days_until': days_until
                        })
        
        return sorted(upcoming, key=lambda x: x['days_until'])


if __name__ == "__main__":
    # Test the earnings calendar
    import asyncio
    
    async def test():
        cal = EarningsCalendar()
        
        print("Testing Earnings Calendar...")
        print("=" * 60)
        
        # Test current time
        now = datetime.now()
        is_earnings, symbol = await cal.is_earnings_week(now)
        print(f"\nCurrent time in earnings week: {is_earnings}")
        if is_earnings:
            print(f"  Company: {symbol}")
        
        # Get upcoming earnings
        print("\nUpcoming Earnings (Next 14 Days):")
        print("-" * 60)
        upcoming = cal.get_upcoming_earnings(14)
        
        if upcoming:
            for event in upcoming:
                print(f"{event['company']:15s} ({event['symbol']:5s}) - {event['date']} ({event['days_until']} days)")
        else:
            print("No earnings scheduled in next 14 days (or cache empty)")
        
        print("\n" + "=" * 60)
        print("Note: Run this during market hours for live data")
        print("Cache refreshes daily")
    
    asyncio.run(test())
