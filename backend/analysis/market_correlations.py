"""
Market Correlations Analyzer
Tracks QQQ, VIX, Bond Yields, SPY - Critical for NQ trading
"""

import yfinance as yf
import numpy as np
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)


class MarketCorrelations:
    """Analyzes market correlations critical for NQ"""
    
    def __init__(self):
        self.symbols = {
            'QQQ': 'QQQ',      # NQ tracks QQQ 99%!
            'SPY': 'SPY',       # Overall market
            'VIX': '^VIX',      # Volatility/Fear
            'TNX': '^TNX',      # 10-year Treasury yield
            'DXY': 'DX-Y.NYB'   # Dollar index
        }
    
    def analyze_correlations(self) -> dict:
        """
        Analyze all critical market correlations
        
        Returns:
            dict with correlation analysis
        """
        try:
            correlations = {}
            
            # Get QQQ (MOST IMPORTANT for NQ!)
            qqq_data = self._get_qqq_analysis()
            correlations['qqq'] = qqq_data
            
            # Get VIX (Fear gauge)
            vix_data = self._get_vix_analysis()
            correlations['vix'] = vix_data
            
            # Get Bond Yields (Inverse correlation with tech)
            yield_data = self._get_yield_analysis()
            correlations['yields'] = yield_data
            
            # Get SPY (Overall market)
            spy_data = self._get_spy_analysis()
            correlations['spy'] = spy_data
            
            # Calculate overall market direction
            correlations['overall'] = self._calculate_overall_direction(correlations)
            
            # Generate trading signals
            correlations['signals'] = self._generate_signals(correlations)
            
            return correlations
            
        except Exception as e:
            logger.error(f"Error analyzing correlations: {e}")
            return self._fallback_correlations()
    
    def _get_qqq_analysis(self) -> dict:
        """
        Analyze QQQ (CRITICAL - NQ tracks QQQ!)
        
        QQQ = Nasdaq-100 ETF
        NQ = Nasdaq-100 Futures
        Correlation: 99%+
        """
        try:
            qqq = yf.Ticker('QQQ')
            hist = qqq.history(period='5d', interval='1h')
            
            if hist.empty:
                return self._fallback_qqq()
            
            # Current price and change
            current = hist['Close'].iloc[-1]
            prev_close = hist['Close'].iloc[-24] if len(hist) >= 24 else hist['Close'].iloc[0]
            change = current - prev_close
            change_pct = (change / prev_close) * 100
            
            # Trend
            sma_10 = hist['Close'].rolling(10).mean().iloc[-1]
            sma_20 = hist['Close'].rolling(20).mean().iloc[-1]
            
            if current > sma_10 > sma_20:
                trend = 'STRONG BULLISH'
            elif current > sma_10:
                trend = 'BULLISH'
            elif current < sma_10 < sma_20:
                trend = 'STRONG BEARISH'
            elif current < sma_10:
                trend = 'BEARISH'
            else:
                trend = 'NEUTRAL'
            
            return {
                'price': float(current),
                'change': float(change),
                'change_pct': float(change_pct),
                'trend': trend,
                'signal': 'BULLISH' if change_pct > 0 else 'BEARISH',
                'strength': abs(change_pct),
                'note': 'NQ tracks QQQ 99% - CRITICAL indicator'
            }
            
        except Exception as e:
            logger.error(f"QQQ analysis failed: {e}")
            return self._fallback_qqq()
    
    def _get_vix_analysis(self) -> dict:
        """
        Analyze VIX (Fear/Volatility Index)
        
        VIX < 15: Low fear, bullish
        VIX 15-20: Normal
        VIX 20-30: Elevated fear
        VIX > 30: High fear, bearish
        """
        try:
            vix = yf.Ticker('^VIX')
            hist = vix.history(period='5d')
            
            if hist.empty:
                return self._fallback_vix()
            
            current = hist['Close'].iloc[-1]
            prev = hist['Close'].iloc[-2]
            change = current - prev
            change_pct = (change / prev) * 100
            
            # Interpret VIX level
            if current < 15:
                level = 'LOW FEAR'
                signal = 'BULLISH'
            elif current < 20:
                level = 'NORMAL'
                signal = 'NEUTRAL'
            elif current < 30:
                level = 'ELEVATED FEAR'
                signal = 'CAUTION'
            else:
                level = 'HIGH FEAR'
                signal = 'BEARISH'
            
            return {
                'value': float(current),
                'change': float(change),
                'change_pct': float(change_pct),
                'level': level,
                'signal': signal,
                'note': 'Rising VIX = Fear = Bearish for NQ'
            }
            
        except Exception as e:
            logger.error(f"VIX analysis failed: {e}")
            return self._fallback_vix()
    
    def _get_yield_analysis(self) -> dict:
        """
        Analyze 10-Year Treasury Yield
        
        Rising yields = Bearish for tech/NQ
        Falling yields = Bullish for tech/NQ
        """
        try:
            tnx = yf.Ticker('^TNX')
            hist = tnx.history(period='5d')
            
            if hist.empty:
                return self._fallback_yields()
            
            current = hist['Close'].iloc[-1]
            prev = hist['Close'].iloc[-2]
            change = current - prev
            change_pct = (change / prev) * 100
            
            # Interpret for tech stocks
            if change_pct > 2:
                signal = 'BEARISH'
                note = 'Rising yields = Tech sells off'
            elif change_pct > 0:
                signal = 'SLIGHTLY BEARISH'
                note = 'Yields up = Mild tech pressure'
            elif change_pct < -2:
                signal = 'BULLISH'
                note = 'Falling yields = Tech rallies'
            elif change_pct < 0:
                signal = 'SLIGHTLY BULLISH'
                note = 'Yields down = Mild tech support'
            else:
                signal = 'NEUTRAL'
                note = 'Yields stable'
            
            return {
                'yield': float(current),
                'change': float(change),
                'change_pct': float(change_pct),
                'signal': signal,
                'note': note
            }
            
        except Exception as e:
            logger.error(f"Yield analysis failed: {e}")
            return self._fallback_yields()
    
    def _get_spy_analysis(self) -> dict:
        """Analyze SPY (Overall market)"""
        try:
            spy = yf.Ticker('SPY')
            hist = spy.history(period='5d', interval='1h')
            
            if hist.empty:
                return self._fallback_spy()
            
            current = hist['Close'].iloc[-1]
            prev_close = hist['Close'].iloc[-24] if len(hist) >= 24 else hist['Close'].iloc[0]
            change_pct = ((current - prev_close) / prev_close) * 100
            
            return {
                'price': float(current),
                'change_pct': float(change_pct),
                'signal': 'BULLISH' if change_pct > 0 else 'BEARISH'
            }
            
        except Exception as e:
            logger.error(f"SPY analysis failed: {e}")
            return self._fallback_spy()
    
    def _calculate_overall_direction(self, correlations: dict) -> dict:
        """Calculate overall market direction"""
        bullish_signals = 0
        bearish_signals = 0
        
        # QQQ (weight: 3 - most important!)
        if correlations['qqq']['signal'] == 'BULLISH':
            bullish_signals += 3
        else:
            bearish_signals += 3
        
        # VIX (weight: 2)
        if correlations['vix']['signal'] == 'BULLISH':
            bullish_signals += 2
        elif correlations['vix']['signal'] == 'BEARISH':
            bearish_signals += 2
        
        # Yields (weight: 2)
        if 'BULLISH' in correlations['yields']['signal']:
            bullish_signals += 2
        elif 'BEARISH' in correlations['yields']['signal']:
            bearish_signals += 2
        
        # SPY (weight: 1)
        if correlations['spy']['signal'] == 'BULLISH':
            bullish_signals += 1
        else:
            bearish_signals += 1
        
        total = bullish_signals + bearish_signals
        bullish_pct = (bullish_signals / total) * 100 if total > 0 else 50
        
        if bullish_pct >= 70:
            direction = 'STRONG BULLISH'
        elif bullish_pct >= 55:
            direction = 'BULLISH'
        elif bullish_pct >= 45:
            direction = 'NEUTRAL'
        elif bullish_pct >= 30:
            direction = 'BEARISH'
        else:
            direction = 'STRONG BEARISH'
        
        return {
            'direction': direction,
            'bullish_pct': bullish_pct,
            'confidence': 'HIGH' if bullish_pct > 70 or bullish_pct < 30 else 'MEDIUM'
        }
    
    def _generate_signals(self, correlations: dict) -> dict:
        """Generate trading signals"""
        overall = correlations['overall']
        qqq = correlations['qqq']
        vix = correlations['vix']
        
        signals = {
            'recommendation': '',
            'score_adjustment': 0,
            'warnings': []
        }
        
        # QQQ is king for NQ
        if qqq['change_pct'] > 1:
            signals['recommendation'] = 'STRONG BUY - QQQ rallying'
            signals['score_adjustment'] = +15
        elif qqq['change_pct'] > 0.5:
            signals['recommendation'] = 'BUY - QQQ positive'
            signals['score_adjustment'] = +10
        elif qqq['change_pct'] < -1:
            signals['recommendation'] = 'AVOID - QQQ falling'
            signals['score_adjustment'] = -15
        elif qqq['change_pct'] < -0.5:
            signals['recommendation'] = 'CAUTION - QQQ negative'
            signals['score_adjustment'] = -10
        
        # VIX warnings
        if vix['value'] > 25:
            signals['warnings'].append('⚠️ High VIX - Reduce position size')
        
        # Yield warnings
        if correlations['yields']['change_pct'] > 3:
            signals['warnings'].append('⚠️ Yields spiking - Tech under pressure')
        
        return signals
    
    def _fallback_qqq(self):
        return {'price': 0, 'change_pct': 0, 'trend': 'UNKNOWN', 'signal': 'NEUTRAL', 'strength': 0, 'note': 'Data unavailable'}
    
    def _fallback_vix(self):
        return {'value': 20, 'change_pct': 0, 'level': 'UNKNOWN', 'signal': 'NEUTRAL', 'note': 'Data unavailable'}
    
    def _fallback_yields(self):
        return {'yield': 4.0, 'change_pct': 0, 'signal': 'NEUTRAL', 'note': 'Data unavailable'}
    
    def _fallback_spy(self):
        return {'price': 0, 'change_pct': 0, 'signal': 'NEUTRAL'}
    
    def _fallback_correlations(self):
        return {
            'qqq': self._fallback_qqq(),
            'vix': self._fallback_vix(),
            'yields': self._fallback_yields(),
            'spy': self._fallback_spy(),
            'overall': {'direction': 'UNKNOWN', 'bullish_pct': 50, 'confidence': 'NONE'},
            'signals': {'recommendation': 'USE CAUTION - Data unavailable', 'score_adjustment': 0, 'warnings': []}
        }


if __name__ == "__main__":
    # Test market correlations
    logging.basicConfig(level=logging.INFO)
    
    print("="*60)
    print("MARKET CORRELATIONS TEST")
    print("="*60)
    
    analyzer = MarketCorrelations()
    correlations = analyzer.analyze_correlations()
    
    print("\n📊 QQQ (NQ tracks this!):")
    print(f"   Price: ${correlations['qqq']['price']:.2f}")
    print(f"   Change: {correlations['qqq']['change_pct']:+.2f}%")
    print(f"   Trend: {correlations['qqq']['trend']}")
    
    print("\n📊 VIX (Fear Index):")
    print(f"   Level: {correlations['vix']['value']:.2f}")
    print(f"   Status: {correlations['vix']['level']}")
    print(f"   Signal: {correlations['vix']['signal']}")
    
    print("\n📊 10Y Yields:")
    print(f"   Yield: {correlations['yields']['yield']:.2f}%")
    print(f"   Change: {correlations['yields']['change_pct']:+.2f}%")
    print(f"   Signal: {correlations['yields']['signal']}")
    
    print("\n📊 OVERALL:")
    print(f"   Direction: {correlations['overall']['direction']}")
    print(f"   Bullish: {correlations['overall']['bullish_pct']:.0f}%")
    print(f"   Recommendation: {correlations['signals']['recommendation']}")
    print(f"   Score Adjustment: {correlations['signals']['score_adjustment']:+d}")
    
    print("\n" + "="*60)
