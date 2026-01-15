"""
Context Analyzer - Retrieves market context for AI decision making
Integrates: News, Sentiment, Market Data, Economic Calendar
"""

import aiohttp
import os
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import logging

logger = logging.getLogger(__name__)


class ContextAnalyzer:
    """Analyzes market context to provide AI with relevant information"""
    
    def __init__(self):
        self.alpha_vantage_key = os.getenv("ALPHA_VANTAGE_KEY")
        self.news_api_key = os.getenv("NEWS_API_KEY")
        try:
            from ..utils.economic_calendar import EconomicCalendar
        except ImportError:
            try:
                from utils.economic_calendar import EconomicCalendar
            except ImportError:
                 from backend.utils.economic_calendar import EconomicCalendar
        
        self.calendar = EconomicCalendar()

    async def get_market_context(self, symbol: str = "NQ") -> Dict:
        """
        Get comprehensive market context for the given symbol
        
        Args:
            symbol: Trading symbol (default: NQ for Nasdaq futures)
            
        Returns:
            Dictionary with market context data
        """
        try:
            # Run all context gathering in parallel
            # Note: In a real async app, we'd use asyncio.gather here
            context = {
                "timestamp": datetime.now().isoformat(),
                "symbol": symbol,
                "sentiment": await self._get_market_sentiment(),
                "news": await self._get_recent_news(),
                "market_conditions": await self._get_market_conditions(),
                "economic_events": await self._get_economic_events(),
                "time_analysis": self._analyze_time_of_day(),
            }
            
            logger.info(f"Market context retrieved successfully for {symbol}")
            return context
            
        except Exception as e:
            logger.error(f"Error getting market context: {str(e)}")
            return self._get_fallback_context()

    async def _get_economic_events(self) -> Dict:
        """Get upcoming economic events from calendar"""
        try:
            # Get next major event
            next_event = self.calendar.get_next_major_event()
            
            # Check if detailed today's events are needed
            today_events = [] # TODO: specific call for today's events if implemented in calendar
            
            return {
                "next_major_event": next_event,
                "is_event_day": next_event and next_event.get('days_away', 99) == 0,
                "risk_level": "HIGH" if next_event and next_event.get('days_away', 99) == 0 else "NORMAL"
            }
        except Exception as e:
            logger.warning(f"Could not fetch economic events: {e}")
            return {"next_major_event": None, "risk_level": "UNKNOWN"}

    # ... _get_market_sentiment kept as is ...

    async def _get_market_sentiment(self) -> Dict:
        """Get overall market sentiment from Fear & Greed Index and other sources"""
        try:
            # Fear & Greed Index (free, no API key needed)
            async with aiohttp.ClientSession() as session:
                # CNN Fear & Greed Index alternative API
                url = "https://api.alternative.me/fng/"
                async with session.get(url) as response:
                    if response.status == 200:
                        data = await response.json()
                        fng_value = int(data['data'][0]['value'])
                        fng_text = data['data'][0]['value_classification']
                        
                        return {
                            "fear_greed_index": fng_value,
                            "fear_greed_text": fng_text,
                            "sentiment_score": self._normalize_sentiment(fng_value),
                            "description": self._get_sentiment_description(fng_value)
                        }
        except Exception as e:
            logger.warning(f"Could not fetch sentiment data: {str(e)}")
        
        return {
            "fear_greed_index": 50,
            "fear_greed_text": "Neutral",
            "sentiment_score": 0,
            "description": "Sentiment data unavailable"
        }

    async def _get_recent_news(self) -> List[Dict]:
        """Get recent financial news headlines including Geopolitics & Macro"""
        try:
            if not self.news_api_key:
                logger.warning("NewsAPI key not configured")
                return []
            
            # Get news from last 2 hours
            from_time = (datetime.now() - timedelta(hours=4)).isoformat() # Expanded to 4h for macro
            
            async with aiohttp.ClientSession() as session:
                url = "https://newsapi.org/v2/everything"
                # Expanded query for Macro/Geopolitics
                query = "nasdaq OR federal reserve OR powell OR inflation OR geopolitics OR war OR oil price"
                
                params = {
                    "apiKey": self.news_api_key,
                    "q": query,
                    "from": from_time,
                    "sortBy": "publishedAt",
                    "language": "en",
                    "pageSize": 7 # Increased from 5
                }
                
                async with session.get(url, params=params) as response:
                    if response.status == 200:
                        data = await response.json()
                        articles = data.get('articles', [])
                        
                        return [
                            {
                                "title": article['title'],
                                "source": article['source']['name'],
                                "published": article['publishedAt'],
                                "sentiment": self._analyze_headline_sentiment(article['title']),
                                "category": self._categorize_news(article['title'])
                            }
                            for article in articles[:7]
                        ]
        except Exception as e:
            logger.warning(f"Could not fetch news: {str(e)}")
        
        return []

    def _categorize_news(self, title: str) -> str:
        """Categorize news into Market, Macro, or Geo"""
        title_lower = title.lower()
        if any(w in title_lower for w in ['war', 'conflict', 'geopolitics', 'tension', 'china', 'russia']):
            return "Geopolitics"
        elif any(w in title_lower for w in ['fed', 'rate', 'cpi', 'inflation', 'gdp', 'powell']):
            return "Macro"
        else:
            return "Market"

    async def _get_market_conditions(self) -> Dict:
        """Get current market conditions (VIX, SPY trend)"""
        try:
            # Note: Ideally we'd reuse the DataCollector for VIX, but for lightweight context 
            # we'll try to get it if available, or just use SPY as proxy.
            
            if not self.alpha_vantage_key:
                return self._get_default_market_conditions()
            
            async with aiohttp.ClientSession() as session:
                # Get SPY data
                url = "https://www.alphavantage.co/query"
                params = {
                    "function": "GLOBAL_QUOTE",
                    "symbol": "SPY",
                    "apikey": self.alpha_vantage_key
                }
                
                # We could also try fetching VIX if supported by provider or just check SPY volatility
                
                async with session.get(url, params=params) as response:
                    if response.status == 200:
                        data = await response.json()
                        quote = data.get('Global Quote', {})
                        
                        if quote:
                            price = float(quote.get('05. price', 0))
                            change_pct = float(quote.get('10. change percent', '0').rstrip('%'))
                            
                            # Estimate volatility/fear from spy move magnitude for now if VIX not avail
                            is_volatile = abs(change_pct) > 1.0
                            
                            return {
                                "spy_price": price,
                                "spy_change_pct": change_pct,
                                "spy_trend": "Bullish" if change_pct > 0.3 else "Bearish" if change_pct < -0.3 else "Neutral",
                                "market_strength": abs(change_pct),
                                "volatility_estimate": "High" if is_volatile else "Normal"
                            }
        except Exception as e:
            logger.warning(f"Could not fetch market conditions: {str(e)}")
        
        return self._get_default_market_conditions()

    def _analyze_time_of_day(self, timestamp: Optional[datetime] = None) -> Dict:
        """Analyze current time for trading quality (including Odd Hours)"""
        now = timestamp if timestamp else datetime.now()
        hour = now.hour
        minute = now.minute
        time_decimal = hour + minute / 60
        
        # Market hours analysis (ET timezone assumed)
        
        # 1. US Prime Hours (9:30 AM - 4:00 PM ET)
        if 9.5 <= time_decimal <= 11.5:
            quality = "Excellent"
            session = "US Morning Drive"
            reason = "High volume, strong trends"
        elif 11.5 < time_decimal < 14:
            quality = "Poor"
            session = "US Lunch"
            reason = "Choppy, low volatility"
        elif 14 <= time_decimal <= 15.5:
            quality = "Good"
            session = "US Afternoon"
            reason = "End of day positioning"
        elif 15.5 < time_decimal <= 16:
            quality = "Risky"
            session = "US Closing Bell"
            reason = "Extreme volatility/imbalance"
            
        # 2. London Open (3:00 AM - 5:00 AM ET)
        elif 3 <= time_decimal <= 5:
            quality = "Great"  # Upgrade for off-hours trader
            session = "London Open"
            reason = "European liquidity injection, often sets daily trend"
            
        # 3. Asian Open (6:00 PM - 10:00 PM ET)
        elif 18 <= time_decimal <= 22:
            quality = "Decent"
            session = "Asian Session"
            reason = "Lower volume, good for range scalping or mean reversion"
            
        # 4. Dead Zones
        elif 17 <= time_decimal < 18:
            quality = "Closed"
            session = "Market Maintenance"
            reason = "Futures market closed"
        else:
            quality = "Quiet"
            session = "Overnight/Pre-Market"
            reason = "Low liquidity, spread risk"
        
        return {
            "current_time": now.strftime("%H:%M ET"),
            "time_quality": quality,
            "session": session,
            "reason": reason,
            "is_prime_time": quality in ["Excellent", "Good", "Great", "Decent"]
        }
    
    def _normalize_sentiment(self, fng_value: int) -> float:
        """Normalize Fear & Greed (0-100) to sentiment score (-1 to 1)"""
        # 0 = Extreme Fear (-1), 50 = Neutral (0), 100 = Extreme Greed (1)
        return (fng_value - 50) / 50
    
    def _get_sentiment_description(self, fng_value: int) -> str:
        """Get human-readable sentiment description"""
        if fng_value <= 25:
            return "Extreme Fear - Potential buying opportunity"
        elif fng_value <= 45:
            return "Fear - Cautious market"
        elif fng_value <= 55:
            return "Neutral - Balanced market"
        elif fng_value <= 75:
            return "Greed - Optimistic market"
        else:
            return "Extreme Greed - Potential reversal risk"
    
    def _analyze_headline_sentiment(self, headline: str) -> str:
        """
        Analyze sentiment using VADER (Valence Aware Dictionary and sEntiment Reasoner)
        Much smarter than keyword counting!
        """
        try:
            from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
            analyzer = SentimentIntensityAnalyzer()
            
            # VADER returns a compound score from -1 (most negative) to +1 (most positive)
            vs = analyzer.polarity_scores(headline)
            compound = vs['compound']
            
            if compound >= 0.05:
                # Strong positive
                return "Positive"
            elif compound <= -0.05:
                # Strong negative
                return "Negative"
            else:
                return "Neutral"
                
        except ImportError:
            # Fallback to old keyword method if VADER not found
            logger.warning("VADER Sentiment not found, using fallback")
            return self._fallback_keyword_sentiment(headline)
            
    def _fallback_keyword_sentiment(self, headline: str) -> str:
        """Simple keyword-based sentiment (Fallback)"""
        headline_lower = headline.lower()
        
        positive_words = ['surge', 'rally', 'gain', 'rise', 'beat', 'strong', 'growth', 'up']
        negative_words = ['fall', 'drop', 'decline', 'loss', 'weak', 'down', 'crash', 'plunge']
        
        positive_count = sum(1 for word in positive_words if word in headline_lower)
        negative_count = sum(1 for word in negative_words if word in headline_lower)
        
        if positive_count > negative_count:
            return "Positive"
        elif negative_count > positive_count:
            return "Negative"
        else:
            return "Neutral"
    
    def _get_default_market_conditions(self) -> Dict:
        """Return default market conditions when API is unavailable"""
        return {
            "spy_price": 0,
            "spy_change_pct": 0,
            "spy_trend": "Unknown",
            "market_strength": 0,
            "volatility_estimate": "Unknown"
        }

    def _get_fallback_context(self) -> Dict:
        """Return minimal context when all APIs fail"""
        return {
            "timestamp": datetime.now().isoformat(),
            "symbol": "NQ",
            "sentiment": {
                "fear_greed_index": 50,
                "sentiment_score": 0,
                "description": "Data unavailable"
            },
            "news": [],
            "market_conditions": self._get_default_market_conditions(),
            "economic_events": {"next_major_event": None, "risk_level": "UNKNOWN"},
            "time_analysis": self._analyze_time_of_day(),
            "status": "Limited data - using fallback"
        }
    
    def format_context_summary(self, context: Dict) -> str:
        """Format context into human-readable summary"""
        sentiment = context.get('sentiment', {})
        market = context.get('market_conditions', {})
        time_info = context.get('time_analysis', {})
        news = context.get('news', [])
        
        summary = f"""
📊 MARKET CONTEXT
Sentiment: {sentiment.get('fear_greed_text', 'Unknown')} ({sentiment.get('fear_greed_index', 'N/A')})
SPY Trend: {market.get('spy_trend', 'Unknown')} ({market.get('spy_change_pct', 0):+.2f}%)
Time Quality: {time_info.get('time_quality', 'Unknown')}
Volatility: {market.get('volatility_estimate', 'Unknown')}

📰 RECENT NEWS ({len(news)} headlines)
"""
        
        for i, article in enumerate(news[:3], 1):
            summary += f"{i}. {article['title'][:60]}... ({article['sentiment']})\n"
        
        if not news:
            summary += "No recent news available\n"
        
        return summary.strip()
