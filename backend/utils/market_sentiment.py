"""
Market Sentiment Collector
Fetches real-time sentiment data (Fear & Greed, VIX, etc.)
Part of the Hybrid Automation Strategy for NQ AI Alerts
"""

import yfinance as yf
import requests
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

class MarketSentiment:
    """Collects real-time market sentiment data"""
    
    @staticmethod
    def get_realtime_vix():
        """
        Get current VIX level (Volatility Index)
        Acts as a proxy for "Fear" in the market
        """
        try:
            vix = yf.Ticker("^VIX")
            # fast_info is often faster/more reliable for current price than history
            price = vix.fast_info.get('last_price')
            
            if price is None:
                # Fallback to history
                hist = vix.history(period="1d")
                if not hist.empty:
                    price = hist['Close'].iloc[-1]
            
            if price:
                logger.info(f"✅ VIX Level fetched: {price:.2f}")
                return round(price, 2)
            else:
                return None
                
        except Exception as e:
            logger.error(f"Failed to fetch VIX: {e}")
            return None

    @staticmethod
    def get_fear_and_greed_index():
        """
        Fetch Fear & Greed Index
        Tries public APIs or falls back to VIX-based estimation
        Returns: int (0-100) or None
        """
        # Option 1: Try reliable API (CNN is hard to scrape reliably without breaking)
        # We will use a trusted free alternative or VIX proxy for stability
        
        try:
            # Alternative.me Crypto Fear & Greed (Good proxy for general risk-on/off behavior in tech)
            r = requests.get("https://api.alternative.me/fng/?limit=1", timeout=5)
            if r.status_code == 200:
                data = r.json()
                score = int(data['data'][0]['value'])
                # logger.info(f"✅ Fear & Greed Index (Crypto Proxy): {score}")
                # Note: Crypto F&G is loosely correlated with NQ risk, but let's stick to VIX for pure equities if this feels off.
                # Actually, simplest "Robust" solution is VIX inverse scaling if no direct API.
                pass
        except Exception:
            pass
            
        # VIX Proxy (Stable & Robust)
        # VIX usually ranges 10-30. 
        # VIX 10 = Greed (Score 80-90)
        # VIX 20 = Neutral (Score 50)
        # VIX 30+ = Fear (Score 10-20)
        vix = MarketSentiment.get_realtime_vix()
        if vix:
            # Simple linear mapping: VIX 10->90, VIX 40->10
            # score = 90 - ((vix - 10) * (80/30)) 
            # score = 90 - (vix - 10) * 2.66
            score = max(0, min(100, 90 - (vix - 10) * 2.5))
            logger.info(f"✅ Estimated Fear & Greed from VIX ({vix}): {int(score)}")
            return int(score)
            
        return 50 # Default Neutral

    @staticmethod
    def get_market_context():
        """
        Get comprehensive market context dictionary
        """
        vix = MarketSentiment.get_realtime_vix()
        fng = MarketSentiment.get_fear_and_greed_index()
        
        sentiment_text = "Neutral"
        if fng:
            if fng > 75: sentiment_text = "Extreme Greed"
            elif fng > 60: sentiment_text = "Greed"
            elif fng < 25: sentiment_text = "Extreme Fear"
            elif fng < 40: sentiment_text = "Fear"
            
        return {
            "vix": vix,
            "fear_greed_index": fng,
            "sentiment_text": sentiment_text,
            "timestamp": datetime.now().isoformat()
        }

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    context = MarketSentiment.get_market_context()
    print(context)
