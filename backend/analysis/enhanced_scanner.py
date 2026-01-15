"""
Enhanced Stock Scanner Module
Professional-grade scanner with targets, timelines, and multi-factor analysis
"""

import yfinance as yf
import pandas as pd
import numpy as np
import logging
import asyncio
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

class EnhancedStockScanner:
    """Advanced scanner with price targets, timelines, and divergence detection"""
    
    def __init__(self):
        # Expanded watchlist (High Beta / Tech Leaders)
        self.watchlist = [
            'NVDA', 'AMD', 'TSLA', 'META', 'AAPL', 'MSFT', 'AMZN', 'GOOGL',
            'NFLX', 'COIN', 'MSTR', 'SMCI', 'ARM', 'PLTR', 'SNOW'
        ]
        self.benchmark = 'SPY'
        
    async def scan_market(self, top_n=5) -> dict:
        """
        Scan market for top picks with full analysis
        
        Returns:
            dict with top_bullish and top_bearish with enhanced metrics
        """
        logger.info(f"Scanning {len(self.watchlist)} stocks for opportunities...")
        results = []
        
        try:
            for symbol in self.watchlist:
                metrics = await self._analyze_stock_enhanced(symbol)
                if metrics:
                    results.append(metrics)
            
            # Sort by composite score
            results.sort(key=lambda x: x['composite_score'], reverse=True)
            
            top_bullish = [r for r in results if r['bias'] == 'BULLISH'][:top_n]
            top_bearish = [r for r in results if r['bias'] == 'BEARISH'][:top_n]
            
            return {
                'timestamp': pd.Timestamp.now().isoformat(),
                'top_bullish': top_bullish,
                'top_bearish': top_bearish,
                'scanned_count': len(results)
            }
            
        except Exception as e:
            logger.error(f"Scanner failed: {e}")
            return {'top_bullish': [], 'top_bearish': []}
    
    async def _analyze_stock_enhanced(self, symbol: str) -> dict:
        """Enhanced analysis with targets, timelines, and divergence"""
        try:
            ticker = yf.Ticker(symbol)
            
            # Fetch 3 months of daily data
            hist = ticker.history(period='3mo', interval='1d')
            if hist.empty or len(hist) < 50:
                return None
            
            # Calculate technical indicators
            hist['RSI'] = self._calculate_rsi(hist['Close'], 14)
            hist['ATR'] = self._calculate_atr(hist, 14)
            hist['SMA_20'] = hist['Close'].rolling(20).mean()
            hist['SMA_50'] = hist['Close'].rolling(50).mean()
            hist['Volume_MA'] = hist['Volume'].rolling(20).mean()
            
            current = hist.iloc[-1]
            current_price = float(current['Close'])
            atr = float(current['ATR'])
            rsi = float(current['RSI'])
            
            # === 1. PRICE TARGETS (ATR-Based) ===
            if current_price > current['SMA_20']:  # Bullish
                target_price = current_price + (2.5 * atr)
                stop_loss = current_price - (1.0 * atr)
            else:  # Bearish
                target_price = current_price - (2.5 * atr)
                stop_loss = current_price + (1.0 * atr)
            
            risk_reward = abs(target_price - current_price) / abs(stop_loss - current_price)
            
            # === 2. TIMELINE CLASSIFICATION ===
            atr_pct = (atr / current_price) * 100
            if atr_pct > 3.0:
                timeline = "Day Trade (1-3 days)"
                timeline_days = "1-3"
            elif atr_pct > 1.5:
                timeline = "Swing (3-7 days)"
                timeline_days = "3-7"
            else:
                timeline = "Position (7-14 days)"
                timeline_days = "7-14"
            
            # === 3. RSI DIVERGENCE ===
            divergence = self._detect_divergence(hist)
            
            # === 4. VOLUME ANALYSIS ===
            volume_ratio = float(current['Volume'] / current['Volume_MA'])
            if volume_ratio > 2.0:
                volume_signal = "BREAKOUT"
            elif volume_ratio > 1.5:
                volume_signal = "ELEVATED"
            else:
                volume_signal = "NORMAL"
            
            # === 5. TREND & BIAS ===
            sma20 = float(current['SMA_20'])
            sma50 = float(current['SMA_50'])
            
            if current_price > sma20 > sma50:
                bias = 'BULLISH'
                trend_strength = "STRONG"
            elif current_price > sma20:
                bias = 'BULLISH'
                trend_strength = "MODERATE"
            elif current_price < sma20 < sma50:
                bias = 'BEARISH'
                trend_strength = "STRONG"
            elif current_price < sma20:
                bias = 'BEARISH'
                trend_strength = "MODERATE"
            else:
                bias = 'NEUTRAL'
                trend_strength = "WEAK"
            
            # === 6. EARNINGS CALENDAR CHECK ===
            earnings_warning = None
            try:
                # Check if earnings within next 7 days
                info = ticker.info
                earnings_date = info.get('earningsDate')
                if earnings_date:
                    # earnings_date is typically a timestamp
                    if isinstance(earnings_date, list) and len(earnings_date) > 0:
                        next_earnings = pd.Timestamp(earnings_date[0], unit='s')
                    else:
                        next_earnings = pd.Timestamp(earnings_date, unit='s')
                    
                    days_to_earnings = (next_earnings - pd.Timestamp.now()).days
                    if 0 <= days_to_earnings <= 7:
                        earnings_warning = f"Earnings in {days_to_earnings} days"
            except Exception:
                # Earnings data not available or error
                pass
            
            # === 7. COMPOSITE SCORE ===
            score = 50  # Base
            
            # Trend alignment
            if bias == 'BULLISH' and trend_strength == "STRONG": score += 20
            elif bias == 'BULLISH': score += 10
            elif bias == 'BEARISH' and trend_strength == "STRONG": score -= 20
            elif bias == 'BEARISH': score -= 10
            
            # RSI momentum
            if 40 < rsi < 60: score += 10  # Healthy
            elif rsi > 70: score -= 5  # Overbought
            elif rsi < 30: score += 15  # Oversold bounce potential
            
            # Volume confirmation
            if volume_signal == "BREAKOUT": score += 15
            elif volume_signal == "ELEVATED": score += 8
            
            # Divergence bonus
            if divergence == "Bullish": score += 20
            elif divergence == "Bearish": score -= 20
            
            # Risk/Reward quality
            if risk_reward > 3: score += 10
            elif risk_reward > 2: score += 5
            
            return {
                'symbol': symbol,
                'price': current_price,
                'target': round(target_price, 2),
                'stop': round(stop_loss, 2),
                'risk_reward': round(risk_reward, 2),
                'timeline': timeline,
                'timeline_days': timeline_days,
                'bias': bias,
                'trend_strength': trend_strength,
                'rsi': round(rsi, 1),
                'divergence': divergence,
                'volume_signal': volume_signal,
                'volume_ratio': round(volume_ratio, 2),
                'composite_score': round(score, 1),
                'atr': round(atr, 2),
                'earnings_warning': earnings_warning
            }
            
        except Exception as e:
            logger.warning(f"Failed to analyze {symbol}: {e}")
            return None
    
    def _calculate_rsi(self, prices, period=14):
        """Calculate RSI"""
        delta = prices.diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))
        return rsi
    
    def _calculate_atr(self, df, period=14):
        """Calculate Average True Range"""
        high_low = df['High'] - df['Low']
        high_close = abs(df['High'] - df['Close'].shift())
        low_close = abs(df['Low'] - df['Close'].shift())
        tr = pd.concat([high_low, high_close, low_close], axis=1).max(axis=1)
        atr = tr.rolling(window=period).mean()
        return atr
    
    def _detect_divergence(self, hist):
        """Detect RSI divergence (simplified)"""
        if len(hist) < 20:
            return None
        
        recent = hist.tail(20)
        
        # Check if price made new high but RSI didn't (Bearish Divergence)
        price_high_recent = recent['Close'].iloc[-5:].max()
        price_high_prev = recent['Close'].iloc[-20:-5].max()
        
        rsi_high_recent = recent['RSI'].iloc[-5:].max()
        rsi_high_prev = recent['RSI'].iloc[-20:-5].max()
        
        if price_high_recent > price_high_prev and rsi_high_recent < rsi_high_prev:
            return "Bearish"
        
        # Check if price made new low but RSI didn't (Bullish Divergence)
        price_low_recent = recent['Close'].iloc[-5:].min()
        price_low_prev = recent['Close'].iloc[-20:-5].min()
        
        rsi_low_recent = recent['RSI'].iloc[-5:].min()
        rsi_low_prev = recent['RSI'].iloc[-20:-5].min()
        
        if price_low_recent < price_low_prev and rsi_low_recent > rsi_low_prev:
            return "Bullish"
        
        return None
    
    def format_top_picks(self, results: dict) -> str:
        """Format top picks for display"""
        output = []
        output.append("🎯 TOP 5 STOCK PICKS\n")
        output.append("=" * 60)
        
        for i, stock in enumerate(results['top_bullish'], 1):
            emoji = ["🥇", "🥈", "🥉", "4️⃣", "5️⃣"][i-1]
            
            output.append(f"\n{emoji} {stock['symbol']} - ${stock['price']:.2f} → ${stock['target']:.2f} | {stock['timeline_days']} Days")
            output.append(f"   Stop: ${stock['stop']:.2f} | R:R {stock['risk_reward']:.1f}:1 | {stock['trend_strength']} {stock['bias']}")
            
            if stock['divergence']:
                output.append(f"   📊 {stock['divergence']} Divergence Detected")
            
            if stock['volume_signal'] in ['BREAKOUT', 'ELEVATED']:
                output.append(f"   📈 Volume: {stock['volume_signal']} ({stock['volume_ratio']:.1f}x avg)")
            
            if stock.get('earnings_warning'):
                output.append(f"   ⚠️ {stock['earnings_warning']} - Reduce size")
            
            output.append(f"   Score: {stock['composite_score']}/100")
        
        return "\n".join(output)

if __name__ == "__main__":
    # Test Enhanced Scanner
    import asyncio
    logging.basicConfig(level=logging.INFO)
    
    scanner = EnhancedStockScanner()
    loop = asyncio.get_event_loop()
    results = loop.run_until_complete(scanner.scan_market(top_n=5))
    
    print(scanner.format_top_picks(results))
