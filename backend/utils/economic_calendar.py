"""
Economic Calendar Integration
Filters trades during high-impact economic events (Fed, CPI, NFP, etc.)
"""
import os
import logging
from datetime import datetime, timedelta
from typing import Tuple, Optional, List, Dict
import aiohttp
import json
from pathlib import Path

logger = logging.getLogger(__name__)

class EconomicCalendar:
    """
    Manages economic event calendar to avoid trading during high-impact news
    """
    
    # High-impact events to avoid
    HIGH_IMPACT_EVENTS = [
        'FOMC', 'Federal Reserve', 'Interest Rate Decision',
        'CPI', 'Consumer Price Index', 'Inflation',
        'NFP', 'Non-Farm Payroll', 'Employment',
        'GDP', 'Gross Domestic Product',
        'PCE', 'Personal Consumption',
        'Retail Sales', 'Unemployment Rate'
    ]
    
    def __init__(self, cache_dir: str = "backend/data/calendar"):
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.events_cache: Dict[str, List[Dict]] = {}
        self.cache_file = self.cache_dir / "economic_events.json"
        self._load_cache()
    
    def _load_cache(self):
        """Load cached events from disk"""
        try:
            if self.cache_file.exists():
                with open(self.cache_file, 'r') as f:
                    self.events_cache = json.load(f)
                logger.info(f"Loaded {len(self.events_cache)} cached event days")
        except Exception as e:
            logger.warning(f"Failed to load event cache: {e}")
            self.events_cache = {}
    
    def _save_cache(self):
        """Save events cache to disk"""
        try:
            with open(self.cache_file, 'w') as f:
                json.dump(self.events_cache, f, indent=2)
        except Exception as e:
            logger.error(f"Failed to save event cache: {e}")
    
    async def is_safe_to_trade(self, timestamp: datetime) -> Tuple[bool, Optional[str]]:
        """
        Check if timestamp is safe for trading (not near major economic event)
        
        Args:
            timestamp: Time to check
            
        Returns:
            (is_safe, event_name): True if safe, False if within event window
        """
        date_key = timestamp.strftime('%Y-%m-%d')
        
        # Get today's events
        events = await self.get_events_for_date(timestamp.date())
        
        # Check if within 30 minutes of any high-impact event
        for event in events:
            event_time = datetime.fromisoformat(event['time'])
            time_diff = abs((timestamp - event_time).total_seconds() / 60)
            
            if time_diff < 30:  # Within 30 minutes
                logger.info(f"Economic Filter: {event['name']} in {time_diff:.0f} min")
                return False, event['name']
        
        return True, None
    
    async def get_events_for_date(self, date) -> List[Dict]:
        """
        Get economic events for a specific date
        
        Args:
            date: Date to check
            
        Returns:
            List of events with 'time', 'name', 'impact'
        """
        date_key = date.strftime('%Y-%m-%d')
        
        # Check cache first
        if date_key in self.events_cache:
            return self.events_cache[date_key]
            
        # Check Historical Database (Hardcoded 2024-2026)
        hist_events = self.get_historical_events(date_key)
        if hist_events:
            return hist_events
        
        # Fetch from API (or use hardcoded schedule for now)
        events = await self._fetch_events_from_api(date)
        
        # Cache the results
        self.events_cache[date_key] = events
        self._save_cache()
        
        return events
    
    def get_historical_events(self, date_key: str) -> List[Dict]:
        """
        Get hardcoded historical events (2024-2026) for Training
        """
        # FOMC Meetings (Fed Interest Rate)
        fomc_dates = {
            # 2024
            '2024-01-31', '2024-03-20', '2024-05-01', '2024-06-12', 
            '2024-07-31', '2024-09-18', '2024-11-07', '2024-12-18',
            # 2025
            '2025-01-29', '2025-03-19', '2025-05-07', '2025-06-18',
            '2025-07-30', '2025-09-17', '2025-10-29', '2025-12-10',
            # 2026 (Projected/Scheduled)
            '2026-01-28', '2026-03-18', '2026-04-29', '2026-06-17',
            '2026-07-29', '2026-09-16', '2026-11-04', '2026-12-16'
        }
        
        # CPI (Inflation)
        cpi_dates = {
            # 2024
            '2024-01-11', '2024-02-13', '2024-03-12', '2024-04-10', '2024-05-15', '2024-06-12',
            '2024-07-11', '2024-08-14', '2024-09-11', '2024-10-10', '2024-11-13', '2024-12-11',
            # 2025
            '2025-01-15', '2025-02-12', '2025-03-12', '2025-04-10', '2025-05-14', '2025-06-11',
            '2025-07-11', '2025-08-13', '2025-09-11', '2025-10-10', '2025-11-13', '2025-12-11',
            # 2026 (Approx 12th-15th)
            '2026-01-14', '2026-02-12'
        }
        
        # NFP (Jobs - 1st Friday usually)
        nfp_dates = {
            # 2024
            '2024-01-05', '2024-02-02', '2024-03-08', '2024-04-05', '2024-05-03', '2024-06-07',
            '2024-07-05', '2024-08-02', '2024-09-06', '2024-10-04', '2024-11-01', '2024-12-06',
            # 2025
            '2025-01-10', '2025-02-07', '2025-03-07', '2025-04-04', '2025-05-02', '2025-06-06',
            '2025-07-03', '2025-08-01', '2025-09-05', '2025-10-03', '2025-11-07', '2025-12-05',
            # 2026
            '2026-01-09', '2026-02-06'
        }
        
        # Tech Earnings (NVDA, AAPL, MSFT)
        earnings_dates = {
            # NVDA
            '2024-02-21': 'NVDA Earnings', '2024-05-22': 'NVDA Earnings', 
            '2024-08-28': 'NVDA Earnings', '2024-11-20': 'NVDA Earnings',
            '2025-02-26': 'NVDA Earnings', '2025-05-29': 'NVDA Earnings',
            '2025-08-27': 'NVDA Earnings', '2025-11-19': 'NVDA Earnings',
            # AAPL
            '2024-02-01': 'AAPL Earnings', '2024-05-02': 'AAPL Earnings',
            '2024-08-01': 'AAPL Earnings', '2024-10-31': 'AAPL Earnings',
            '2025-01-30': 'AAPL Earnings', '2025-05-01': 'AAPL Earnings',
            '2025-07-31': 'AAPL Earnings', '2025-10-30': 'AAPL Earnings',
            # MSFT
            '2024-01-30': 'MSFT Earnings', '2024-04-25': 'MSFT Earnings',
            '2024-07-30': 'MSFT Earnings', '2024-10-30': 'MSFT Earnings',
            '2025-01-29': 'MSFT Earnings', '2025-04-30': 'MSFT Earnings',
            '2025-07-30': 'MSFT Earnings', '2025-10-29': 'MSFT Earnings'
        }

        events = []
        if date_key in fomc_dates:
            events.append({'time': f"{date_key}T14:00:00", 'name': 'FOMC Meeting', 'impact': 'HIGH'})
        if date_key in cpi_dates:
            events.append({'time': f"{date_key}T08:30:00", 'name': 'CPI Report', 'impact': 'HIGH'})
        if date_key in nfp_dates:
            events.append({'time': f"{date_key}T08:30:00", 'name': 'Non-Farm Payrolls', 'impact': 'HIGH'})
        if date_key in earnings_dates:
            events.append({'time': f"{date_key}T16:00:00", 'name': earnings_dates[date_key], 'impact': 'HIGH'})
            
        return events

    def get_all_event_dates(self) -> Dict[str, set]:
        """
        Get all historical event dates by category for vectorized ML processing
        Merges Hardcoded History (2024-2025) with Live Cache (2026)
        """
        # 1. Base Hardcoded Data
        events = {
            'FOMC': {
                '2024-01-31', '2024-03-20', '2024-05-01', '2024-06-12', 
                '2024-07-31', '2024-09-18', '2024-11-07', '2024-12-18',
                '2025-01-29', '2025-03-19', '2025-05-07', '2025-06-18',
                '2025-07-30', '2025-09-17', '2025-10-29', '2025-12-10',
                '2026-01-28', '2026-03-18', '2026-04-29', '2026-06-17',
                '2026-07-29', '2026-09-16', '2026-11-04', '2026-12-16'
            },
            'CPI': {
                '2024-01-11', '2024-02-13', '2024-03-12', '2024-04-10', '2024-05-15', '2024-06-12',
                '2024-07-11', '2024-08-14', '2024-09-11', '2024-10-10', '2024-11-13', '2024-12-11',
                '2025-01-15', '2025-02-12', '2025-03-12', '2025-04-10', '2025-05-14', '2025-06-11',
                '2025-07-11', '2025-08-13', '2025-09-11', '2025-10-10', '2025-11-13', '2025-12-11',
                '2026-01-14', '2026-02-12'
            },
            'NFP': {
                '2024-01-05', '2024-02-02', '2024-03-08', '2024-04-05', '2024-05-03', '2024-06-07',
                '2024-07-05', '2024-08-02', '2024-09-06', '2024-10-04', '2024-11-01', '2024-12-06',
                '2025-01-10', '2025-02-07', '2025-03-07', '2025-04-04', '2025-05-02', '2025-06-06',
                '2025-07-03', '2025-08-01', '2025-09-05', '2025-10-03', '2025-11-07', '2025-12-05',
                '2026-01-09', '2026-02-06'
            },
            'EARNINGS': {
                '2024-02-21', '2024-05-22', '2024-08-28', '2024-11-20',
                '2025-02-26', '2025-05-29', '2025-08-27', '2025-11-19',
                '2024-02-01', '2024-05-02', '2024-08-01', '2024-10-31',
                '2025-01-30', '2025-05-01', '2025-07-31', '2025-10-30',
                '2024-01-30', '2024-04-25', '2024-07-30', '2024-10-30',
                '2025-01-29', '2025-04-30', '2025-07-30', '2025-10-29'
            }
        }
        
        # 2. Merge Live Cache (The "Update" Mechanic)
        # Iterate over all cached days and add any matching events
        for date_key, day_events in self.events_cache.items():
            for event in day_events:
                name = event['name'].lower()
                
                if 'fomc' in name or 'federal reserve' in name:
                    events['FOMC'].add(date_key)
                elif 'cpi' in name or 'inflation' in name:
                    events['CPI'].add(date_key)
                elif 'non-farm' in name or 'nfp' in name or 'unemployment' in name:
                    events['NFP'].add(date_key)
        
        return events

    async def _fetch_events_from_api(self, date) -> List[Dict]:
        """
        Fetch events from ForexFactory XML Feed (This Week + Next Week)
        and merge with hardcoded major events.
        """
        # 1. Start with Hardcoded 2026 major events (Base Layer)
        major_events_2026 = {
            # FOMC Meetings (2 PM ET)
            '2026-01-28': [{'time': '2026-01-28T14:00:00', 'name': 'FOMC Meeting', 'impact': 'HIGH'}],
            '2026-03-18': [{'time': '2026-03-18T14:00:00', 'name': 'FOMC Meeting', 'impact': 'HIGH'}],
            '2026-04-29': [{'time': '2026-04-29T14:00:00', 'name': 'FOMC Meeting', 'impact': 'HIGH'}],
            '2026-06-17': [{'time': '2026-06-17T14:00:00', 'name': 'FOMC Meeting', 'impact': 'HIGH'}],
            '2026-07-29': [{'time': '2026-07-29T14:00:00', 'name': 'FOMC Meeting', 'impact': 'HIGH'}],
            '2026-09-16': [{'time': '2026-09-16T14:00:00', 'name': 'FOMC Meeting', 'impact': 'HIGH'}],
            '2026-11-04': [{'time': '2026-11-04T14:00:00', 'name': 'FOMC Meeting', 'impact': 'HIGH'}],
            '2026-12-16': [{'time': '2026-12-16T14:00:00', 'name': 'FOMC Meeting', 'impact': 'HIGH'}],
            # Note: Other Jan events are removed here as they will be fetched dynamically
        }

        # 2. Fetch Dynamic Data from ForexFactory (This Week & Next Week)
        # We fetch ALL available dynamic data, cache it, and then return what's asked
        
        feed_urls = [
            "https://nfs.faireconomy.media/ff_calendar_thisweek.xml",
            "https://nfs.faireconomy.media/ff_calendar_nextweek.xml"
        ]
        
        import xml.etree.ElementTree as ET
        
        dynamic_events = {}
        
        async with aiohttp.ClientSession() as session:
            for url in feed_urls:
                try:
                    async with session.get(url) as response:
                        if response.status == 200:
                            xml_content = await response.text()
                            try:
                                root = ET.fromstring(xml_content)
                                for event in root.findall('event'):
                                    country = event.find('country').text
                                    impact = event.find('impact').text
                                    
                                    # Filter: Major Global Currencies and High/Medium Impact
                                    # Added EUR, GBP, JPY, CNY for Global Trading Sessions
                                    major_currencies = ['USD', 'EUR', 'GBP', 'JPY', 'CNY']
                                    if country in major_currencies and impact in ['High', 'Medium']:
                                        title = event.find('title').text
                                        date_str = event.find('date').text # MM-DD-YYYY
                                        time_str = event.find('time').text # HH:mm(am/pm) usually, check format
                                        
                                        # Format Date: MM-DD-YYYY -> YYYY-MM-DD
                                        try:
                                            # Parse date (ForexFactory uses MM-DD-YYYY)
                                            # And Time (1:30pm)
                                            dt_str = f"{date_str} {time_str}"
                                            # FF usually sends ET or GMT, need to verify. 
                                            # Assuming the feed gives times that are relatively usable.
                                            # A safe bet for now is parsing as standard datetime
                                            
                                            # Quick parse logic
                                            m, d, y = map(int, date_str.split('-'))
                                            
                                            # Parse time is tricky (1:30pm), let's just store as IS
                                            # or proper ISO if possible. 
                                            # For now, let's format YYYY-MM-DD for key
                                            iso_date = f"{y}-{m:02d}-{d:02d}"
                                            
                                            # Create Event Object
                                            # We construct a rough ISO timestamp by parsing 12h time
                                            # 1:30pm -> 13:30
                                            # time_str extraction:
                                            time_obj = datetime.strptime(time_str, "%I:%M%p")
                                            iso_time = f"{iso_date}T{time_obj.hour:02d}:{time_obj.minute:02d}:00"

                                            if iso_date not in dynamic_events:
                                                dynamic_events[iso_date] = []
                                            
                                            dynamic_events[iso_date].append({
                                                'time': iso_time,
                                                'name': title,
                                                'impact': impact.upper()
                                            })
                                            
                                        except ValueError as e:
                                            logger.warning(f"Error parsing event date/time: {date_str} {time_str} - {e}")
                                            continue

                            except ET.ParseError:
                                logger.error(f"Failed to parse XML from {url}")
                except Exception as e:
                    logger.warning(f"Failed to fetch ForexFactory feed: {e}")

        # 3. Merge Dynamic Data into Cache (Global update)
        # This is a side-effect: we update self.events_cache with EVERYTHING we found
        for d_key, events_list in dynamic_events.items():
            # If we have hardcoded events for this day, merge them
            # Prefer Dynamic if duplicates, or just append?
            # Append is safer to not lose FOMC if FF doesn't have it yet
            if d_key in self.events_cache:
                # Basic dedup by name
                existing_names = {e['name'] for e in self.events_cache[d_key]}
                for new_ev in events_list:
                    if new_ev['name'] not in existing_names:
                        self.events_cache[d_key].append(new_ev)
            else:
                self.events_cache[d_key] = events_list
        
        # Also merge into the local 'major_events_2026' dict for the specific return
        # But actually, simpler: just return what is now in self.events_cache for the requested date
        # If requested date wasn't in dynamic feeds (e.g. 3 months out), fall back to hardcoded
        
        date_key = date.strftime('%Y-%m-%d')
        
        # Check cache again (now populated)
        if date_key in self.events_cache:
            return self.events_cache[date_key]
            
        # Fallback to hardcoded if strictly needed (e.g. far future FOMC)
        return major_events_2026.get(date_key, [])
    
    def get_next_major_event(self) -> Optional[Dict]:
        """Get the next upcoming major economic event"""
        now = datetime.now()
        
        # Check next 30 days
        for i in range(30):
            check_date = (now + timedelta(days=i)).date()
            events = []
            
            # Synchronous version for quick check
            date_key = check_date.strftime('%Y-%m-%d')
            if date_key in self.events_cache:
                events = self.events_cache[date_key]
            
            for event in events:
                event_time = datetime.fromisoformat(event['time'])
                if event_time > now:
                    return {
                        'name': event['name'],
                        'time': event_time,
                        'days_away': (event_time.date() - now.date()).days
                    }
        
        return None


if __name__ == "__main__":
    # Test the economic calendar
    import asyncio
    
    async def test():
        cal = EconomicCalendar()
        
        # Test current time
        now = datetime.now()
        is_safe, event = await cal.is_safe_to_trade(now)
        print(f"Current time safe to trade: {is_safe}")
        if not is_safe:
            print(f"  Reason: {event}")
        
        # Test FOMC day
        fomc_day = datetime(2026, 1, 28, 14, 15)  # 15 min after FOMC
        is_safe, event = await cal.is_safe_to_trade(fomc_day)
        print(f"\nFOMC day (2:15 PM): {is_safe}")
        if not is_safe:
            print(f"  Reason: {event}")
        
        # Test safe day
        safe_day = datetime(2026, 1, 15, 10, 0)
        is_safe, event = await cal.is_safe_to_trade(safe_day)
        print(f"\nRegular day: {is_safe}")
        
        # Next event
        next_event = cal.get_next_major_event()
        if next_event:
            print(f"\nNext major event: {next_event['name']}")
            print(f"  Date: {next_event['time']}")
            print(f"  Days away: {next_event['days_away']}")
    
    asyncio.run(test())
