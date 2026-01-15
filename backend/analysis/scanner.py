"""
Stock Scanner Module
Finds high Relative Strength (RS) stocks for trading
"""

import yfinance as yf
import pandas as pd
import logging
import asyncio

logger = logging.getLogger(__name__)

class StockScanner:
    """Scans watchlist for high-potential setups"""
    
    def __init__(self):
        # Default watchlist (High Beta / Tech)
        self.watchlist = [
            'NVDA', 'AMD', 'TSLA', 'META', 'AAPL', 'MSFT', 'AMZN', 'GOOGL',
            'Netflix', 'COIN', 'MSTR', 'SMCI', 'ARM'
        ]
        self.benchmark = 'SPY'
        
    async def scan_market(self) -> dict:
        """
        Scan watchlist for top picks
        
        Returns:
            dict with top_bullish and top_bearish lists
        """
        logger.info("Scanning market for top stocks...")
        results = []
        
        try:
            # simple loop for now (can be parallelized)
            for symbol in self.watchlist:
                # Correct symbol if needed (Netflix -> NFLX)
                if symbol == 'Netflix': symbol = 'NFLX'
                
                metrics = await self._analyze_stock(symbol)
                if metrics:
                    results.append(metrics)
            
            # Sort by Relative Strength Score
            results.sort(key=lambda x: x['rs_score'], reverse=True)
            
            top_bullish = [r for r in results if r['bias'] == 'BULLISH'][:3]
            top_bearish = [r for r in results if r['bias'] == 'BEARISH'][:3] # Inverse sort
            
            return {
                'timestamp': pd.Timestamp.now().isoformat(),
                'top_bullish': top_bullish,
                'top_bearish': top_bearish,
                'scanned_count': len(results)
            }
            
        except Exception as e:
            logger.error(f"Scanner failed: {e}")
            return {'top_bullish': [], 'top_bearish': []}
    
    async def _analyze_stock(self, symbol: str) -> dict:
        """Analyze single stock for RS and Trend"""
        try:
            # Fetch 1mo data
            ticker = yf.Ticker(symbol)
            hist = ticker.history(period='1mo')
            
            if hist.empty: return None
            
            current = hist['Close'].iloc[-1]
            start_price = hist['Close'].iloc[0]
            
            # Simple Relative Performance calculation
            perf = ((current - start_price) / start_price) * 100
            
            # Trend Check (SMA 5 > SMA 10)
            sma5 = hist['Close'].tail(5).mean()
            sma10 = hist['Close'].tail(10).mean()
            
            volume_ratio = hist['Volume'].iloc[-1] / hist['Volume'].mean()
            
            bias = 'BULLISH' if sma5 > sma10 else 'BEARISH'
            
            # HEURISTIC SCORE
            score = perf  # Baseline score is performance
            if bias == 'BULLISH': score += 5
            if volume_ratio > 1.5: score += 5 
            
            return {
                'symbol': symbol,
                'price': float(current),
                'perf_1mo': float(perf),
                'bias': bias,
                'vol_ratio': float(volume_ratio),
                'rs_score': float(score)
            }
            
        except Exception:
            return None

if __name__ == "__main__":
    # Test Scanner
    import asyncio
    logging.basicConfig(level=logging.INFO)
    
    scanner = StockScanner()
    loop = asyncio.get_event_loop()
    metrics = loop.run_until_complete(scanner.scan_market())
    
    print("\n🚀 TOP BULLISH STOCKS:")
    for s in metrics['top_bullish']:
        print(f"  {s['symbol']}: ${s['price']:.2f} (+{s['perf_1mo']:.1f}%) [RS: {s['rs_score']:.1f}]")
