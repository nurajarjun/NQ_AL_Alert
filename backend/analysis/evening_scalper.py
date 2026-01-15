"""
Evening Scalper Module (Asian Session + After Hours)
Target: $500/day | Time: 4:00 PM - 10:00 PM ET
Assets: Futures (NQ, ES, NKD, GC, SI, CL, NG) + FX (JPY, EUR)
"""

import yfinance as yf
import pandas as pd
import pandas_ta as ta
import logging
from datetime import datetime, time
import pytz

logger = logging.getLogger(__name__)

class EveningScalper:
    def __init__(self):
        # OPTIMIZED: Only high-volume, liquid assets for scalping
        # Removed: NKD (low vol), HG (low vol), SI (low vol), NG (low vol), JPY (low vol)
        self.assets = {
            # US Futures (After Hours 4-8 PM) - HIGHEST VOLUME
            'NQ': {'symbol': 'NQ=F', 'name': 'Nasdaq Futures', 'multiplier': 20},
            'ES': {'symbol': 'ES=F', 'name': 'S&P 500 Futures', 'multiplier': 50},
            
            # Commodities (Active 24h) - GOOD VOLUME
            'GC': {'symbol': 'GC=F', 'name': 'Gold', 'multiplier': 100},
            'CL': {'symbol': 'CL=F', 'name': 'Crude Oil', 'multiplier': 1000},
            
            # FX (Active 24h) - EXCELLENT VOLUME
            'EUR': {'symbol': 'EURUSD=X', 'name': 'Euro/USD', 'multiplier': 125000}
        }
        
        # Extended session for more opportunities
        self.session_start = time(16, 0)  # 4:00 PM ET (After Hours)
        self.session_end = time(22, 0)    # 10:00 PM ET (Asian Close)
        self.timezone = pytz.timezone('US/Eastern')
        
        # Prop Fund Risk Management
        self.daily_target = 500
        self.max_loss = -250
        self.current_pnl = 0

    async def scan_market(self):
        """Scan all assets for actionable setups"""
        logger.info("🌙 Scanning Evening Markets (4 PM - 10 PM ET)...")
        results = []
        
        # Check time window
        now_et = datetime.now(self.timezone).time()
        in_session = self.session_start <= now_et <= self.session_end
        
        for ticker, info in self.assets.items():
            try:
                signal = await self._analyze_asset(ticker, info['symbol'], info['name'], info['multiplier'])
                if signal:
                    signal['in_session'] = in_session
                    results.append(signal)
            except Exception as e:
                logger.error(f"Error analyzing {ticker}: {e}")
                
        return results

    async def _analyze_asset(self, ticker, symbol, asset_name, multiplier):
        """Analyze asset and generate ACTIONABLE trade setup"""
        # Fetch 5m data for scalping
        stock = yf.Ticker(symbol)
        df = stock.history(period="5d", interval="5m")
        
        if len(df) < 50:
            return None
            
        # Calculate indicators
        df.ta.adx(length=14, append=True)
        df.ta.bbands(length=20, std=2, append=True)
        df.ta.rsi(length=14, append=True)
        df.ta.atr(length=14, append=True)
        df['VOL_SMA'] = df['Volume'].rolling(20).mean()
        
        last = df.iloc[-1]
        
        # Current values
        price = last['Close']
        adx = last.get('ADX_14', 0)
        rsi = last.get('RSI_14', 50)
        atr = last.get('ATRr_14', 0)
        vol_ratio = last['Volume'] / last.get('VOL_SMA', 1) if last.get('VOL_SMA', 1) > 0 else 0
        upper_band = last.get('BBU_20_2.0', price)
        lower_band = last.get('BBL_20_2.0', price)
        middle_band = last.get('BBM_20_2.0', price)
        
        signal = None
        strategy = ""
        confidence = "LOW"
        entry = None
        stop = None
        target1 = None
        target2 = None
        
        # === STRATEGY 1: BREAKOUT (High Volume + Strong Trend) ===
        # ADJUSTED: Lowered thresholds for more signals
        if vol_ratio > 1.2 and adx > 20:  # Was: 1.5 and 25
            if price > upper_band:
                signal = "LONG"
                strategy = "🚀 Breakout Long"
                confidence = "HIGH"
                entry = price
                stop = price - (atr * 1.5)
                target1 = price + (atr * 2)
                target2 = price + (atr * 4)
                
            elif price < lower_band:
                signal = "SHORT"
                strategy = "🔻 Breakout Short"
                confidence = "HIGH"
                entry = price
                stop = price + (atr * 1.5)
                target1 = price - (atr * 2)
                target2 = price - (atr * 4)
        
        # === STRATEGY 2: MEAN REVERSION (Range Bound) ===
        # ADJUSTED: Wider ADX and RSI ranges
        elif adx < 25:  # Was: 20
            # Oversold at support - BUY
            if rsi < 35 and price <= lower_band:  # Was: 30
                signal = "LONG"
                strategy = "🔄 Mean Reversion (Oversold)"
                confidence = "MEDIUM"
                entry = price
                stop = price - (atr * 1.0)
                target1 = middle_band  # Return to mean
                target2 = upper_band   # Full reversion
                
            # Overbought at resistance - SELL
            elif rsi > 65 and price >= upper_band:  # Was: 70
                signal = "SHORT"
                strategy = "🔄 Mean Reversion (Overbought)"
                confidence = "MEDIUM"
                entry = price
                stop = price + (atr * 1.0)
                target1 = middle_band
                target2 = lower_band
        
        # === STRATEGY 3: MOMENTUM CONTINUATION ===
        # ADJUSTED: Wider ADX range and lower volume requirement
        elif 15 <= adx <= 35 and vol_ratio > 1.0:  # Was: 20-30 and 1.2
            # Bullish momentum
            if rsi > 55 and price > middle_band:
                signal = "LONG"
                strategy = "📈 Momentum Long"
                confidence = "MEDIUM"
                entry = price
                stop = price - (atr * 1.5)
                target1 = price + (atr * 1.5)
                target2 = price + (atr * 3)
                
            # Bearish momentum
            elif rsi < 45 and price < middle_band:
                signal = "SHORT"
                strategy = "📉 Momentum Short"
                confidence = "MEDIUM"
                entry = price
                stop = price + (atr * 1.5)
                target1 = price - (atr * 1.5)
                target2 = price - (atr * 3)
        
        if signal and entry and stop and target1:
            # Calculate risk/reward
            risk = abs(entry - stop)
            reward1 = abs(target1 - entry)
            reward2 = abs(target2 - entry) if target2 else reward1 * 2
            
            rr_ratio1 = reward1 / risk if risk > 0 else 0
            rr_ratio2 = reward2 / risk if risk > 0 else 0
            
            # Calculate dollar values
            risk_dollars = risk * multiplier
            reward1_dollars = reward1 * multiplier
            reward2_dollars = reward2 * multiplier
            
            return {
                'ticker': ticker,
                'pair': asset_name,
                'signal': signal,
                'strategy': strategy,
                'confidence': confidence,
                
                # Price levels
                'price': round(price, 2),
                'entry': round(entry, 2),
                'stop': round(stop, 2),
                'target1': round(target1, 2),
                'target2': round(target2, 2) if target2 else round(target1 * 1.5, 2),
                
                # Risk metrics
                'risk_points': round(risk, 2),
                'reward1_points': round(reward1, 2),
                'reward2_points': round(reward2, 2),
                'rr_ratio1': round(rr_ratio1, 2),
                'rr_ratio2': round(rr_ratio2, 2),
                
                # Dollar values (1 contract)
                'risk_dollars': round(risk_dollars, 2),
                'reward1_dollars': round(reward1_dollars, 2),
                'reward2_dollars': round(reward2_dollars, 2),
                
                # Indicators
                'rsi': round(rsi, 1),
                'adx': round(adx, 1),
                'atr': round(atr, 2),
                'vol_ratio': round(vol_ratio, 2),
                
                'timestamp': datetime.now().strftime('%H:%M:%S')
            }
            
        return None

if __name__ == "__main__":
    # Test script
    import asyncio
    async def test():
        scalper = EveningScalper()
        signals = await scalper.scan_market()
        print(f"\n🌙 Evening Scalper - Signals Found: {len(signals)}\n")
        for s in signals:
            print(f"{'='*60}")
            print(f"{s['pair']} ({s['ticker']})")
            print(f"Signal: {s['signal']} | Strategy: {s['strategy']}")
            print(f"Entry: {s['entry']} | Stop: {s['stop']}")
            print(f"Target 1: {s['target1']} (R/R: {s['rr_ratio1']})")
            print(f"Target 2: {s['target2']} (R/R: {s['rr_ratio2']})")
            print(f"Risk: ${s['risk_dollars']:.0f} | Reward: ${s['reward1_dollars']:.0f} / ${s['reward2_dollars']:.0f}")
            print(f"RSI: {s['rsi']} | ADX: {s['adx']} | ATR: {s['atr']}")
            
    asyncio.run(test())
