
import yfinance as yf
import logging
import json
import asyncio
import sys
import os

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("LIVE_TEST")

def test_earnings_live():
    logger.info("--- Testing Live Earnings (yfinance) ---")
    tickers = ['NVDA', 'AAPL', 'MSFT']
    
    for symbol in tickers:
        try:
            t = yf.Ticker(symbol)
            # Fetch calendar
            cal = t.calendar
            
            logger.info(f"Checking {symbol}...")
            if cal:
                # It's a dict
                logger.info(f"✅ FOUND Calendar data per {symbol}")
                logger.info(f"   Keys: {list(cal.keys())}")
                logger.info(f"   Sample: {cal}")
            else:
                logger.warning(f"⚠️ No calendar data for {symbol}")
                
        except Exception as e:
            logger.error(f"❌ Failed to fetch {symbol}: {e}")

def test_news_live():
    logger.info("\n--- Testing Live News (yfinance) ---")
    try:
        # NQ Futures or Tech ETF
        t = yf.Ticker("QQQ") 
        news = t.news
        
        if news:
            logger.info(f"✅ FOUND {len(news)} news items")
            # Print raw first item to debug keys
            logger.info(f"   DEBUG RAW: {news[0]}")
            
            for item in news[:2]:
                # Try common keys
                title = item.get('title', item.get('content', {}).get('title'))
                pub = item.get('publisher', 'Unknown')
                logger.info(f"   📰 {title} ({pub})")
        else:
            logger.warning("⚠️ No news found for QQQ")
            
    except Exception as e:
        logger.error(f"❌ Failed to news: {e}")

def test_integration():
    logger.info("\n--- Testing Integration (economic_news.py) ---")
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    from analysis.economic_news import NewsAnalyzer, EconomicCalendar
    
    # 1. News Analyzer (Fallback to YF)
    logger.info("Testing NewsAnalyzer (No API Key)...")
    news = NewsAnalyzer() # No key
    data = news.get_market_news()
    
    if data['articles']:
        logger.info(f"✅ NewsAnalyzer returned {len(data['articles'])} articles via YF")
        logger.info(f"   Sentiment: {data['sentiment']['direction']} ({data['sentiment']['score']}%)")
        logger.info(f"   Summary: \n{data['headline_summary']}")
    else:
        logger.error("❌ NewsAnalyzer returned no articles")
        
    # 2. Earnings Check
    logger.info("\nTesting EconomicCalendar (Live Earnings)...")
    cal = EconomicCalendar()
    # We can't force it to find earnings unless today is an earnings day
    # But we can run the check and see if it crashes
    try:
        earnings = cal._check_tech_earnings()
        logger.info(f"✅ _check_tech_earnings ran successfully (Found: {len(earnings)})")
    except Exception as e:
        logger.error(f"❌ _check_tech_earnings CRASHED: {e}")

if __name__ == "__main__":
    # test_earnings_live()
    # test_news_live()
    test_integration()

