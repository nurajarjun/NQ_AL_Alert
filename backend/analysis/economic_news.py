"""
Economic Calendar & News Analyzer
Tracks economic events, Fed announcements, and breaking news
"""

import requests
import yfinance as yf
from datetime import datetime, timedelta
import logging
from typing import Dict, List, Optional

logger = logging.getLogger(__name__)


class EconomicCalendar:
    """Monitors economic events and their impact on NQ"""
    
    def __init__(self):
        # Major economic events that move NQ
        self.high_impact_events = [
            'FOMC', 'Fed', 'Interest Rate', 'CPI', 'Inflation',
            'NFP', 'Non-Farm', 'Payroll', 'GDP', 'Unemployment',
            'Retail Sales', 'PMI', 'ISM', 'Powell', 'Yellen'
        ]
        
        # Tech earnings (CRITICAL for NQ!)
        self.tech_giants = [
            'AAPL', 'MSFT', 'GOOGL', 'GOOG', 'AMZN', 'NVDA', 
            'TSLA', 'META', 'NFLX', 'AMD', 'INTC', 'ORCL'
        ]
    
    def get_todays_events(self) -> Dict:
        """
        Get today's economic events and earnings
        
        Returns:
            dict with events and their impact
        """
        try:
            events = {
                'high_impact': [],
                'medium_impact': [],
                'tech_earnings': [],
                'warnings': []
            }
            
            # Check for major economic events
            economic_events = self._check_economic_events()
            if economic_events:
                events['high_impact'].extend(economic_events)
            
            # Check for tech earnings
            earnings = self._check_tech_earnings()
            if earnings:
                events['tech_earnings'].extend(earnings)
            
            # Generate warnings
            if events['high_impact']:
                events['warnings'].append("⚠️ High-impact economic event today - expect volatility")
            
            if events['tech_earnings']:
                events['warnings'].append("📊 Major tech earnings today - NQ may be volatile")
            
            # Calculate risk level
            events['risk_level'] = self._calculate_risk_level(events)
            events['trading_recommendation'] = self._get_trading_recommendation(events)
            
            return events
            
        except Exception as e:
            logger.error(f"Error getting economic events: {e}")
            return self._fallback_events()
    
    def _check_economic_events(self) -> List[Dict]:
        """
        Check for major economic events today
        
        In production, this would call an economic calendar API
        For now, returns simulated data based on day of week
        """
        events = []
        
        today = datetime.now()
        day_of_week = today.weekday()  # 0=Monday, 4=Friday
        
        # Simulate common event schedule
        if day_of_week == 2:  # Wednesday - FOMC common
            events.append({
                'event': 'FOMC Meeting Possible',
                'time': '14:00 ET',
                'impact': 'HIGH',
                'expected': 'Check Fed calendar'
            })
        
        if day_of_week == 4:  # Friday - Jobs report
            week_of_month = (today.day - 1) // 7 + 1
            if week_of_month == 1:  # First Friday
                events.append({
                    'event': 'Non-Farm Payroll (NFP)',
                    'time': '08:30 ET',
                    'impact': 'VERY HIGH',
                    'expected': 'Major volatility expected'
                })
        
        # CPI typically mid-month
        if 10 <= today.day <= 15:
            events.append({
                'event': 'CPI Report Possible',
                'time': '08:30 ET',
                'impact': 'VERY HIGH',
                'expected': 'Check economic calendar'
            })
        
        return events
    
    def _check_tech_earnings(self) -> List[Dict]:
        """
        Check for tech earnings today using LIVE yfinance data
        """
        earnings = []
        today = datetime.now().date()
        
        # Optimization: Only check if we are in a likely earnings month + day
        # But to be safe and "No Guess Game", we check the big ones.
        # This might be slow (12 API calls), so we limit to Top 6 for speed
        top_focus = ['NVDA', 'AAPL', 'MSFT', 'AMZN', 'GOOGL', 'META']
        
        for ticker in top_focus:
            try:
                stock = yf.Ticker(ticker)
                cal = stock.calendar
                
                if cal and isinstance(cal, dict) and 'Earnings Date' in cal:
                    dates = cal['Earnings Date']
                    # yfinance returns list of dates (usually next one)
                    for d in dates:
                        if d == today:
                             earnings.append({
                                'ticker': ticker,
                                'time': 'After Close', # Assumption, or check more deep data
                                'impact': 'VERY HIGH' if ticker == 'NVDA' else 'HIGH',
                                'note': 'Live Earnings Date Match'
                            })
            except Exception: pass
        
        return earnings

    def _get_trading_recommendation(self, risk_level: str) -> str:
        """Get trading recommendation based on risk level"""
        if risk_level == "EXTREME":
            return "⛔ DO NOT TRADE during event window"
        elif risk_level == "HIGH":
            return "⚠️ Reduce position size, tighten stops"
        elif risk_level == "ELEVATED":
            return "👀 Monitor positions closely"
        else:
            return "✅ Normal trading conditions"
                


    def _calculate_risk_level(self, events: Dict) -> str:
        """Calculate overall risk level"""
        if events['high_impact'] or len(events['tech_earnings']) >= 1: # Stricter
            return 'VERY HIGH'
        elif events['medium_impact']:
            return 'MEDIUM'
        else:
            return 'NORMAL'

    # ... (Keep existing methods) ...

class NewsAnalyzer:
    """Analyzes breaking news and sentiment"""
    
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key
        self.base_url = "https://newsapi.org/v2/everything"
    
    def get_market_news(self) -> Dict:
        """
        Get latest market news (Priority: NewsAPI -> yfinance -> Fallback)
        """
        # 1. Try NewsAPI (Paid/Key)
        if self.api_key:
            try:
                # ... (Existing NewsAPI logic) ...
                return self._fetch_newsapi()
            except Exception:
                pass
        
        # 2. Try Yahoo Finance (Free, Live)
        return self._fetch_yfinance_news()
        
    def _fetch_newsapi(self):
        # ... (Refactored existing logic) ...
        params = {
            'q': 'nasdaq OR "tech stocks" OR "NQ futures"',
            'language': 'en',
            'sortBy': 'publishedAt',
            'pageSize': 10,
            'apiKey': self.api_key
        }
        response = requests.get(self.base_url, params=params, timeout=5)
        if response.status_code == 200:
            data = response.json()
            articles = data.get('articles', [])
            sentiment = self._analyze_sentiment(articles)
            return {
                'articles': articles[:5],
                'sentiment': sentiment,
                'headline_summary': self._get_headline_summary(articles)
            }
        raise Exception("NewsAPI Failed")

    def _fetch_yfinance_news(self) -> Dict:
        """Fetch live news from yfinance (QQQ/NQ)"""
        try:
            # Use QQQ as proxy for NQ news
            ticker = yf.Ticker("QQQ")
            news_items = ticker.news
            
            if not news_items:
                return self._fallback_news()
                
            # Normalize structure to match NewsAPI for _analyze_sentiment
            articles = []
            for item in news_items:
                # Handle nested content structure if present
                content = item
                if 'content' in item: 
                    content = item['content']
                
                articles.append({
                    'title': content.get('title', ''),
                    'description': content.get('summary', ''), # Use summary as dest
                    'source': {'name': content.get('provider', {}).get('displayName', 'Yahoo')}
                })
            
            sentiment = self._analyze_sentiment(articles)
            
            return {
                'articles': articles[:5],
                'sentiment': sentiment,
                'headline_summary': self._get_headline_summary(articles)
            }
            
        except Exception as e:
            logger.error(f"yfinance news failed: {e}")
            return self._fallback_news()

    def _analyze_sentiment(self, articles: List[Dict]) -> Dict:
        # ... (Keep existing sentiment logic) ...
        positive_words = ['surge', 'rally', 'gain', 'jump', 'soar', 'bullish', 'optimistic', 'growth', 'higher', 'up']
        negative_words = ['plunge', 'crash', 'fall', 'drop', 'decline', 'bearish', 'pessimistic', 'recession', 'lower', 'down', 'loss']
        
        positive_count = 0
        negative_count = 0
        
        for article in articles[:10]:
            title = article.get('title', '').lower()
            description = article.get('description', '').lower() # Adjusted to match yf mapping
            text = f"{title} {description}"
            
            for word in positive_words:
                if word in text: positive_count += 1
            for word in negative_words:
                if word in text: negative_count += 1
        
        total = positive_count + negative_count
        if total == 0:
            return {'direction': 'NEUTRAL', 'score': 50, 'confidence': 'LOW'}
        
        positive_pct = (positive_count / total) * 100
        
        if positive_pct >= 60: # Tweaked threshold
            direction = 'BULLISH'
        elif positive_pct <= 40:
            direction = 'BEARISH'
        else:
            direction = 'NEUTRAL'
        
        return {
            'direction': direction,
            'score': int(positive_pct),
            'confidence': 'MEDIUM',
            'positive_count': positive_count,
            'negative_count': negative_count
        }

    # ... (Keep helpers) ...
    def _get_headline_summary(self, articles: List[Dict]) -> str:
        """Get summary of top headlines"""
        if not articles:
            return "No recent news"
        
        headlines = []
        for article in articles[:3]:
            title = article.get('title', 'No title')
            headlines.append(f"• {title}")
        
        return "\n".join(headlines)
    
    def _fallback_news(self) -> Dict:
        """Fallback when all news unavailable"""
        return {
            'articles': [],
            'sentiment': {
                'direction': 'NEUTRAL',
                'score': 50,
                'confidence': 'UNKNOWN'
            },
            'headline_summary': 'News data unavailable'
        }


if __name__ == "__main__":
    # Test economic calendar
    logging.basicConfig(level=logging.INFO)
    
    print("="*60)
    print("ECONOMIC CALENDAR & NEWS TEST")
    print("="*60)
    
    # Test economic calendar
    print("\n1. Economic Calendar:")
    calendar = EconomicCalendar()
    events = calendar.get_todays_events()
    
    print(f"\nRisk Level: {events['risk_level']}")
    print(f"Recommendation: {events['trading_recommendation']}")
    print(f"\n{calendar.format_events_summary(events)}")
    
    # Test news analyzer
    print("\n2. News Analysis:")
    news = NewsAnalyzer()  # No API key = fallback mode
    news_data = news.get_market_news()
    
    print(f"\nSentiment: {news_data['sentiment']['direction']}")
    print(f"Score: {news_data['sentiment']['score']}/100")
    
    print("\n" + "="*60)
