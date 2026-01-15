"""
End-to-End System Test
Tests the complete prediction pipeline
"""

import asyncio
import sys
import os

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

from ml.data_collector import HistoricalDataCollector
from ml.feature_engineer import FeatureEngineer
from ml.transformer_predictor import TransformerPredictor
from analysis.trade_calculator import TradeCalculator
from analysis.economic_news import EconomicCalendar, NewsAnalyzer

print("="*70)
print("🧪 NQ AI ALERT SYSTEM - FULL INTEGRATION TEST")
print("="*70)

async def test_complete_pipeline():
    """Test the complete prediction pipeline"""
    
    # 1. Data Collection
    print("\n📊 Step 1: Data Collection")
    print("-" * 70)
    data_collector = HistoricalDataCollector()
    df = data_collector.download_nq_data(symbol="NQ")
    print(f"✅ Downloaded {len(df)} candles")
    print(f"   Latest price: ${df['Close'].iloc[-1]:,.2f}")
    print(f"   Date range: {df.index[0]} to {df.index[-1]}")
    
    # 2. Feature Engineering
    print("\n🔧 Step 2: Feature Engineering")
    print("-" * 70)
    feature_engineer = FeatureEngineer()
    df_features = feature_engineer.calculate_all_features(df)
    print(f"✅ Calculated {len(feature_engineer.feature_names)} features")
    print(f"   Features: RSI, MACD, EMA, ATR, Bollinger Bands, etc.")
    
    # 3. AI Prediction
    print("\n🤖 Step 3: Deep Learning Prediction")
    print("-" * 70)
    transformer_predictor = TransformerPredictor()
    prediction = transformer_predictor.predict(df_features)
    
    print(f"✅ Prediction Complete")
    print(f"   Direction: {prediction['direction']}")
    print(f"   Confidence: {prediction['confidence']*100:.1f}%")
    print(f"   Score: {prediction['score']}/100")
    print(f"   Probabilities:")
    print(f"     - UP: {prediction['probabilities']['up']*100:.1f}%")
    print(f"     - DOWN: {prediction['probabilities']['down']*100:.1f}%")
    print(f"     - SIDEWAYS: {prediction['probabilities']['sideways']*100:.1f}%")
    
    # 4. Trade Setup Calculation
    print("\n🎯 Step 4: Trade Setup Calculation")
    print("-" * 70)
    trade_calculator = TradeCalculator()
    trade_setup = trade_calculator.calculate_trade_setup(
        df_features,
        prediction['direction'],
        prediction['confidence']
    )
    
    print(f"✅ Trade Setup Complete")
    print(f"   Entry: ${trade_setup['entry']:,.2f}")
    print(f"   Stop Loss: ${trade_setup['stop_loss']:,.2f} ({trade_setup['stop_distance']:+.0f} pts)")
    print(f"   Target 1: ${trade_setup['target1']:,.2f} ({trade_setup['target1_distance']:+.0f} pts) [{trade_setup['risk_reward_t1']}R]")
    print(f"   Target 2: ${trade_setup['target2']:,.2f} ({trade_setup['target2_distance']:+.0f} pts) [{trade_setup['risk_reward_t2']}R]")
    print(f"   Support: {' | '.join([f'${s:,.0f}' for s in trade_setup['support_levels']])}")
    print(f"   Resistance: {' | '.join([f'${r:,.0f}' for r in trade_setup['resistance_levels']])}")
    print(f"   Risk/Contract: ${trade_setup['risk_per_contract']:,.0f}")
    print(f"   ATR: {trade_setup['atr']:.1f} pts")
    
    # 5. Economic Context
    print("\n📅 Step 5: Economic Calendar Check")
    print("-" * 70)
    economic_calendar = EconomicCalendar()
    events = economic_calendar.get_todays_events()
    
    print(f"✅ Economic Analysis Complete")
    print(f"   Risk Level: {events['risk_level']}")
    print(f"   Recommendation: {events['trading_recommendation']}")
    
    if events['high_impact']:
        print(f"   High Impact Events:")
        for event in events['high_impact']:
            print(f"     - {event['event']} at {event['time']}")
    
    if events['tech_earnings']:
        print(f"   Tech Earnings:")
        for earning in events['tech_earnings']:
            print(f"     - {earning['ticker']} {earning['time']}")
    
    if not events['high_impact'] and not events['tech_earnings']:
        print(f"   No major events today")
    
    # 6. News Sentiment
    print("\n📰 Step 6: News Sentiment Analysis")
    print("-" * 70)
    news_analyzer = NewsAnalyzer()  # No API key = fallback mode
    news = news_analyzer.get_market_news()
    
    print(f"✅ News Analysis Complete")
    print(f"   Sentiment: {news['sentiment']['direction']}")
    print(f"   Score: {news['sentiment']['score']}/100")
    print(f"   Confidence: {news['sentiment']['confidence']}")
    print(f"   (Running in fallback mode - no API key)")
    
    # 7. Market Session
    print("\n⏰ Step 7: Market Session Analysis")
    print("-" * 70)
    from analysis.market_session import MarketSessionAnalyzer
    session_analyzer = MarketSessionAnalyzer()
    session_info = session_analyzer.get_current_session()
    
    print(f"✅ Session Analysis Complete")
    print(f"   Time (ET): {session_info['current_time_et']}")
    print(f"   Session: {session_info['session'].replace('_', ' ').title()}")
    print(f"   Quality: {session_info['quality']}")
    print(f"   Volume: {session_info['volume_expectation']}")
    print(f"   Recommendation: {session_info['recommendation']}")
    
    # Final Summary
    print("\n" + "="*70)
    print("📱 FINAL TELEGRAM MESSAGE PREVIEW")
    print("="*70)
    
    direction_emoji = "🟢" if prediction['direction'] == 'UP' else "🔴" if prediction['direction'] == 'DOWN' else "⚪"
    
    # Trade type emoji
    type_emoji = {
        'SCALP': '⚡',
        'DAY TRADE': '📊',
        'SWING TRADE': '📈'
    }.get(trade_setup.get('trade_type', 'UNKNOWN'), '❓')
    
    message = f"""
🧠 **NQ Analysis**

{direction_emoji} **PREDICTION: {prediction['direction']}**
💪 Confidence: {prediction['confidence']*100:.1f}%
🎯 AI Score: {prediction['score']}
📊 Method: Deep Learning (Transformer)

💰 **TRADE SETUP** {type_emoji} {trade_setup.get('trade_type', 'UNKNOWN')}
⏱️ Duration: {trade_setup.get('expected_duration', 'Unknown')}
📍 Entry: {trade_setup['entry']:,.2f}
🛑 Stop: {trade_setup['stop_loss']:,.2f} ({trade_setup['stop_distance']:+.0f} pts)
🎯 T1: {trade_setup['target1']:,.2f} ({trade_setup['target1_distance']:+.0f} pts) [{trade_setup['risk_reward_t1']}R]
🎯 T2: {trade_setup['target2']:,.2f} ({trade_setup['target2_distance']:+.0f} pts) [{trade_setup['risk_reward_t2']}R]

📊 **KEY LEVELS**
Support: {' | '.join([f'{s:,.0f}' for s in trade_setup['support_levels']])}
Resistance: {' | '.join([f'{r:,.0f}' for r in trade_setup['resistance_levels']])}

💰 Risk: ${trade_setup['risk_per_contract']:,.0f}/contract
📈 ATR: {trade_setup['atr']:.1f} pts

⏰ **MARKET SESSION**
Time: {session_info.get('current_time_et', 'Unknown')}
Session: {session_info.get('session', 'unknown').replace('_', ' ').title()}
Quality: {session_info.get('quality', 'UNKNOWN')}
Volume: {session_info.get('volume_expectation', 'UNKNOWN')}
💡 {session_info.get('recommendation', 'Unknown')}

📅 **ECONOMIC CONTEXT**
Risk Level: {events['risk_level']}
💡 {events['trading_recommendation']}

📊 **TECHNICAL**
Price: {df['Close'].iloc[-1]:,.2f}
RSI: {df_features['RSI'].iloc[-1]:.1f}
Trend: {'UP' if df['Close'].iloc[-1] > df['Open'].iloc[-1] else 'DOWN'}
"""
    
    print(message)
    
    print("\n" + "="*70)
    print("✅ ALL SYSTEMS OPERATIONAL!")
    print("="*70)
    print("\n💡 Next Step: Send /check to your Telegram bot to see this live!")
    

if __name__ == "__main__":
    asyncio.run(test_complete_pipeline())
