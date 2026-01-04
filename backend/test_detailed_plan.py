"""
TEST: Detailed Trade Plan for NQ at Current Price
This demonstrates the comprehensive trade planning system
"""

import requests
import json

print("\n" + "="*70)
print("🎯 NQ DETAILED TRADE PLAN GENERATOR")
print("="*70)
print("\n📊 Current NQ Price: 21880")
print("Testing LONG setup with comprehensive trade plan...\n")

# Example NQ LONG setup
alert_data = {
    "direction": "LONG",
    "entry": 21880.0,
    "stop": 21850.0,      # 30 points risk
    "target1": 21940.0,   # 60 points reward
    "target2": 22000.0,   # 120 points reward
    "rsi": 55.0,
    "atr": 35.0,
    "volume_ratio": 1.3
}

print("📋 SIGNAL SUBMITTED:")
print(f"  Entry: {alert_data['entry']}")
print(f"  Stop: {alert_data['stop']} (Risk: {alert_data['entry'] - alert_data['stop']} pts)")
print(f"  Target 1: {alert_data['target1']} (Reward: {alert_data['target1'] - alert_data['entry']} pts)")
print(f"  Target 2: {alert_data['target2']} (Reward: {alert_data['target2'] - alert_data['entry']} pts)")

print("\n" + "="*70)
print("🤖 AI ANALYZING & GENERATING TRADE PLAN...")
print("="*70)
print("\nThis will generate:")
print("  ✓ 3 Entry Zones (Aggressive, Optimal, Conservative)")
print("  ✓ 4 Profit Targets with probabilities")
print("  ✓ Dynamic Stop-Loss Strategy")
print("  ✓ Position Sizing (based on $10,000 account)")
print("  ✓ 4 Scenarios (Best, Expected, Breakeven, Worst)")
print("  ✓ Complete Trade Management Plan")
print("  ✓ Risk/Reward Analysis")

try:
    response = requests.post(
        "http://localhost:8000/webhook/tradingview",
        json=alert_data,
        timeout=30
    )
    
    if response.status_code == 200:
        result = response.json()
        
        print("\n" + "="*70)
        print("✅ TRADE PLAN GENERATED SUCCESSFULLY!")
        print("="*70)
        
        print("\n📊 API Response:")
        print(json.dumps(result, indent=2))
        
        if result.get('status') == 'success':
            plan_summary = result.get('trade_plan_summary', {})
            
            print("\n" + "="*70)
            print("📱 CHECK YOUR TELEGRAM FOR DETAILED TRADE PLAN!")
            print("="*70)
            
            print("\n📈 Trade Plan Summary:")
            print(f"  • Targets: {plan_summary.get('targets', 'N/A')}")
            print(f"  • Overall R/R: {plan_summary.get('overall_rr', 'N/A')}:1")
            print(f"  • Expected Profit: ${plan_summary.get('expected_profit', 'N/A')}")
            
            print("\n" + "="*70)
            print("📋 YOUR TELEGRAM ALERT INCLUDES:")
            print("="*70)
            print("""
  📊 SIGNAL QUALITY
    • AI Score (0-100)
    • Recommendation (YES/NO/MAYBE)
    • Risk Level & Confidence
  
  🎯 ENTRY STRATEGY
    • Aggressive Entry (50% position)
    • Optimal Entry (30% position)
    • Conservative Entry (20% position)
  
  🎯 PROFIT TARGETS (4 Levels)
    • Target 1: 1.5R (70% probability)
    • Target 2: 2.5R (50% probability)
    • Target 3: 4.0R (30% probability)
    • Target 4: Extended (15% probability)
  
  🛡️ STOP LOSS STRATEGY
    • Initial stop
    • Breakeven rules
    • Trailing stops
  
  💼 POSITION SIZING
    • Account size
    • Contracts to trade
    • Max loss amount
  
  📈 PROFIT SCENARIOS
    • Best Case (all targets hit)
    • Expected Case (typical outcome)
    • Breakeven Case
    • Worst Case (stop hit)
  
  💡 AI INSIGHTS
    • Key reasoning points
    • Market context
    • Risk factors
  
  ⚙️ TRADE MANAGEMENT
    • Entry execution plan
    • Profit-taking strategy
    • Time-based exits
    • Monitoring guidelines
  
  ⚖️ RISK/REWARD ANALYSIS
    • Risk vs Reward breakdown
    • Overall R/R ratio
    • Assessment
            """)
            
            print("="*70)
            print("🎯 NEXT STEPS:")
            print("="*70)
            print("""
  1. Check your Telegram for the full trade plan
  2. Review all entry zones and targets
  3. Understand the scenarios
  4. Follow the management plan
  5. Execute according to AI recommendations
            """)
            
        elif result.get('status') == 'filtered':
            print("\n" + "="*70)
            print("🔴 ALERT FILTERED BY AI")
            print("="*70)
            print(f"\n  AI Score: {result.get('score')}/100")
            print(f"  Recommendation: {result.get('recommendation')}")
            print("\n  This setup did not meet quality threshold.")
            print("  AI is protecting you from a potentially bad trade!")
            
    else:
        print(f"\n❌ Error: Server returned {response.status_code}")
        print(response.text)
        
except requests.exceptions.ConnectionError:
    print("\n" + "="*70)
    print("❌ ERROR: Cannot connect to server")
    print("="*70)
    print("\nThe server is not running. Please:")
    print("  1. Open terminal")
    print("  2. cd d:\\Google\\.gemini\\antigravity\\scratch\\NQ-AI-Alerts\\backend")
    print("  3. python main.py")
    print("\nThen run this test again!")
    
except Exception as e:
    print(f"\n❌ ERROR: {str(e)}")

print("\n" + "="*70)
