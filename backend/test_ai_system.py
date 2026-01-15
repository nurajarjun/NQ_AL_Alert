"""
Test script for AI-enhanced NQ Alert System
Run this to verify your AI integration is working
"""

import asyncio
import sys
import os

# Add backend to path
sys.path.insert(0, os.path.dirname(__file__))

from ai.context import ContextAnalyzer
from ai.analyzer import AIAnalyzer


async def test_context_analyzer():
    """Test market context retrieval"""
    print("\n" + "="*60)
    print("TEST 1: Market Context Analyzer")
    print("="*60)
    
    analyzer = ContextAnalyzer()
    context = await analyzer.get_market_context("NQ")
    
    print("\n✅ Context Retrieved:")
    print(f"  Sentiment: {context['sentiment']['fear_greed_text']} ({context['sentiment']['fear_greed_index']})")
    print(f"  SPY Trend: {context['market_conditions']['spy_trend']}")
    print(f"  Time Quality: {context['time_analysis']['time_quality']}")
    print(f"  News Articles: {len(context['news'])}")
    
    if context['news']:
        print("\n  Recent Headlines:")
        for i, article in enumerate(context['news'][:3], 1):
            print(f"    {i}. {article['title'][:60]}...")
    
    return context


async def test_ai_analyzer(context):
    """Test AI trade analysis"""
    print("\n" + "="*60)
    print("TEST 2: AI Trade Analyzer")
    print("="*60)
    
    # Sample NQ LONG setup
    signal_data = {
        "direction": "LONG",
        "entry": 16850.5,
        "stop": 16820.0,
        "target1": 16920.0,
        "target2": 16980.0,
        "rsi": 58.5,
        "atr": 45.2,
        "volume_ratio": 1.4
    }
    
    print("\n📊 Testing Signal:")
    print(f"  Direction: {signal_data['direction']}")
    print(f"  Entry: {signal_data['entry']}")
    print(f"  Stop: {signal_data['stop']}")
    print(f"  Target: {signal_data['target1']}")
    print(f"  RSI: {signal_data['rsi']}")
    
    analyzer = AIAnalyzer()
    
    print("\n🤖 Running AI Analysis...")
    analysis = await analyzer.analyze_trade(signal_data, context)
    
    print("\n✅ AI Analysis Complete:")
    print(f"  Provider: {analysis.get('provider', 'Unknown')}")
    print(f"  Recommendation: {analysis['recommendation']}")
    print(f"  Score: {analysis['score']}/100")
    print(f"  Risk Level: {analysis['risk_level']}")
    print(f"  Position Size: {analysis['position_size']}")
    print(f"  Confidence: {analysis['confidence']*100:.0f}%")
    
    print("\n  Reasoning:")
    for reason in analysis['reasoning']:
        print(f"    • {reason}")
    
    if 'key_risks' in analysis:
        print("\n  Key Risks:")
        for risk in analysis['key_risks']:
            print(f"    ⚠️ {risk}")
    
    print(f"\n  Exit Strategy: {analysis.get('exit_strategy', 'N/A')}")
    
    should_send = analyzer.should_send_alert(analysis)
    emoji = analyzer.get_alert_emoji(analysis)
    
    print(f"\n  Should Send Alert: {'YES ✅' if should_send else 'NO ❌'}")
    print(f"  Alert Emoji: {emoji}")
    
    return analysis


async def test_full_flow():
    """Test complete alert flow"""
    print("\n" + "="*60)
    print("TEST 3: Full Alert Flow")
    print("="*60)
    
    # Get context
    print("\n📡 Fetching market context...")
    analyzer = ContextAnalyzer()
    context = await analyzer.get_market_context("NQ")
    
    # Sample signal
    signal_data = {
        "direction": "SHORT",
        "entry": 16900.0,
        "stop": 16930.0,
        "target1": 16830.0,
        "target2": 16770.0,
        "rsi": 72.5,
        "atr": 48.0,
        "volume_ratio": 1.8
    }
    
    print(f"📊 Signal: {signal_data['direction']} at {signal_data['entry']}")
    
    # AI analysis
    print("🤖 Running AI analysis...")
    ai = AIAnalyzer()
    analysis = await ai.analyze_trade(signal_data, context)
    
    # Format alert (simplified)
    emoji = ai.get_alert_emoji(analysis)
    
    print("\n" + "="*60)
    print(f"{emoji} SAMPLE ALERT (as it would appear on Telegram)")
    print("="*60)
    
    print(f"""
{emoji} AI-ANALYZED NQ {signal_data['direction']} SETUP

📊 SIGNAL DETAILS
Entry: {signal_data['entry']:.2f}
Stop: {signal_data['stop']:.2f}
Target 1: {signal_data['target1']:.2f}

🤖 AI ANALYSIS
{analysis['recommendation']} - Score: {analysis['score']}/100
Risk Level: {analysis['risk_level']}
Position Size: {analysis['position_size']}
Confidence: {analysis['confidence']*100:.0f}%

💡 KEY INSIGHTS
{chr(10).join(['• ' + r for r in analysis['reasoning']])}

📈 MARKET CONTEXT
Sentiment: {context['sentiment']['fear_greed_text']} ({context['sentiment']['fear_greed_index']})
SPY: {context['market_conditions']['spy_trend']}
Time: {context['time_analysis']['current_time']} - {context['time_analysis']['time_quality']}
""")


async def main():
    """Run all tests"""
    print("\n" + "="*60)
    print("🚀 NQ AI ALERT SYSTEM - COMPONENT TESTS")
    print("="*60)
    print("\nThis will test:")
    print("  1. Market Context Retrieval (News, Sentiment, Market Data)")
    print("  2. AI Trade Analysis (Gemini/OpenAI)")
    print("  3. Full Alert Flow")
    print("\n" + "="*60)
    
    try:
        # Test 1: Context
        context = await test_context_analyzer()
        
        # Test 2: AI Analysis
        await test_ai_analyzer(context)
        
        # Test 3: Full Flow
        await test_full_flow()
        
        print("\n" + "="*60)
        print("✅ ALL TESTS PASSED!")
        print("="*60)
        print("\nYour AI system is working correctly! 🎉")
        print("\nNext steps:")
        print("  1. Start the server: python main.py")
        print("  2. Test webhook: curl -X POST http://localhost:8000/test")
        print("  3. Deploy to Render.com")
        print("  4. Configure TradingView webhooks")
        print("\n" + "="*60)
        
    except Exception as e:
        print("\n" + "="*60)
        print("❌ TEST FAILED")
        print("="*60)
        print(f"\nError: {str(e)}")
        print("\nPossible issues:")
        print("  • Missing API keys in .env file")
        print("  • Internet connection required for API calls")
        print("  • Check that all dependencies are installed")
        print("\nRun: pip install -r requirements.txt")
        print("\n" + "="*60)
        raise


if __name__ == "__main__":
    asyncio.run(main())
