"""
Logic Verification Test
Validates all classification and decision logic
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

from analysis.trade_calculator import TradeCalculator
from analysis.market_session import MarketSessionAnalyzer
from analysis.economic_news import EconomicCalendar
import pandas as pd
import numpy as np

print("="*70)
print("🔍 LOGIC VERIFICATION TEST - NO GUESSING!")
print("="*70)

# Test 1: Trade Type Classification Logic
print("\n📊 TEST 1: TRADE TYPE CLASSIFICATION")
print("-" * 70)

calculator = TradeCalculator()

# Create test scenarios with known ATR
test_cases = [
    {"atr": 50, "t1_dist": 30, "t2_dist": 60, "expected": "SCALP"},
    {"atr": 50, "t1_dist": 75, "t2_dist": 150, "expected": "DAY TRADE"},
    {"atr": 50, "t1_dist": 120, "t2_dist": 250, "expected": "SWING TRADE"},
]

print("\nLogic: Target Distance ÷ ATR = Type")
print("  < 1.0 ATR → SCALP")
print("  1.0-2.0 ATR → DAY TRADE")
print("  > 2.0 ATR → SWING TRADE\n")

all_passed = True
for i, case in enumerate(test_cases, 1):
    atr = case['atr']
    t1_dist = case['t1_dist']
    t2_dist = case['t2_dist']
    expected = case['expected']
    
    # Calculate ratio
    t1_ratio = t1_dist / atr
    t2_ratio = t2_dist / atr
    
    # Get actual result
    result = calculator._determine_trade_type(0, t1_dist, t2_dist, atr)
    
    passed = result == expected
    all_passed = all_passed and passed
    
    status = "✅ PASS" if passed else "❌ FAIL"
    print(f"Case {i}: {status}")
    print(f"  ATR: {atr} pts")
    print(f"  T1: {t1_dist} pts ({t1_ratio:.2f}x ATR)")
    print(f"  T2: {t2_dist} pts ({t2_ratio:.2f}x ATR)")
    print(f"  Expected: {expected}")
    print(f"  Got: {result}")
    print()

if all_passed:
    print("✅ Trade Type Logic: VERIFIED")
else:
    print("❌ Trade Type Logic: FAILED")

# Test 2: Market Session Detection
print("\n" + "="*70)
print("⏰ TEST 2: MARKET SESSION DETECTION")
print("-" * 70)

session_analyzer = MarketSessionAnalyzer()
current_session = session_analyzer.get_current_session()

print(f"\nCurrent Time (ET): {current_session['current_time_et']}")
print(f"Detected Session: {current_session['session']}")
print(f"Quality: {current_session['quality']}")
print(f"Volume Expectation: {current_session['volume_expectation']}")
print(f"Is Market Open: {current_session['is_market_open']}")
print(f"Is Weekend: {current_session['is_weekend']}")
print(f"\nRecommendation: {current_session['recommendation']}")

# Verify session logic makes sense
session_valid = True
if current_session['is_weekend'] and current_session['is_market_open']:
    print("❌ ERROR: Market cannot be open on weekend!")
    session_valid = False

if current_session['session'] == 'market_open' and current_session['quality'] != 'EXCELLENT':
    print("❌ ERROR: Market open should be EXCELLENT quality!")
    session_valid = False

if current_session['session'] == 'asian_session' and current_session['volume_expectation'] != 'VERY LOW':
    print("❌ ERROR: Asian session should have VERY LOW volume!")
    session_valid = False

if session_valid:
    print("\n✅ Market Session Logic: VERIFIED")
else:
    print("\n❌ Market Session Logic: FAILED")

# Test 3: Economic Calendar Logic
print("\n" + "="*70)
print("📅 TEST 3: ECONOMIC CALENDAR LOGIC")
print("-" * 70)

economic_calendar = EconomicCalendar()
events = economic_calendar.get_todays_events()

print(f"\nRisk Level: {events['risk_level']}")
print(f"High Impact Events: {len(events['high_impact'])}")
print(f"Tech Earnings: {len(events['tech_earnings'])}")
print(f"Recommendation: {events['trading_recommendation']}")

# Verify risk level logic
risk_valid = True

if events['high_impact'] and events['risk_level'] == 'NORMAL':
    print("❌ ERROR: High impact events should increase risk level!")
    risk_valid = False

if events['risk_level'] == 'VERY HIGH' and events['trading_recommendation'] != 'REDUCE POSITION SIZE - Wait for event':
    print("❌ ERROR: Very high risk should recommend reducing position!")
    risk_valid = False

if risk_valid:
    print("\n✅ Economic Calendar Logic: VERIFIED")
else:
    print("\n❌ Economic Calendar Logic: FAILED")

# Test 4: Support/Resistance Logic
print("\n" + "="*70)
print("📊 TEST 4: SUPPORT/RESISTANCE LOGIC")
print("-" * 70)

# Create synthetic price data
dates = pd.date_range('2024-01-01', periods=100, freq='1H')
# Create price with clear swing highs and lows
prices = 17000 + 100 * np.sin(np.linspace(0, 4*np.pi, 100)) + np.random.randn(100) * 10

df = pd.DataFrame({
    'Open': prices,
    'High': prices + np.random.rand(100) * 5,
    'Low': prices - np.random.rand(100) * 5,
    'Close': prices,
    'Volume': np.random.randint(1000, 10000, 100)
}, index=dates)

current_price = df['Close'].iloc[-1]

support_levels = calculator._calculate_support_levels(df, current_price)
resistance_levels = calculator._calculate_resistance_levels(df, current_price)

print(f"\nCurrent Price: ${current_price:,.2f}")
print(f"Support Levels: {[f'${s:,.2f}' for s in support_levels]}")
print(f"Resistance Levels: {[f'${r:,.2f}' for r in resistance_levels]}")

# Verify logic
levels_valid = True

# All support should be below current price
for s in support_levels:
    if s >= current_price:
        print(f"❌ ERROR: Support ${s:,.2f} is not below current price ${current_price:,.2f}!")
        levels_valid = False

# All resistance should be above current price
for r in resistance_levels:
    if r <= current_price:
        print(f"❌ ERROR: Resistance ${r:,.2f} is not above current price ${current_price:,.2f}!")
        levels_valid = False

# Should have 3 levels each
if len(support_levels) != 3:
    print(f"❌ ERROR: Should have 3 support levels, got {len(support_levels)}!")
    levels_valid = False

if len(resistance_levels) != 3:
    print(f"❌ ERROR: Should have 3 resistance levels, got {len(resistance_levels)}!")
    levels_valid = False

if levels_valid:
    print("\n✅ Support/Resistance Logic: VERIFIED")
else:
    print("\n❌ Support/Resistance Logic: FAILED")

# Final Summary
print("\n" + "="*70)
print("📋 FINAL VERIFICATION SUMMARY")
print("="*70)

total_tests = 4
passed_tests = sum([all_passed, session_valid, risk_valid, levels_valid])

print(f"\nTests Passed: {passed_tests}/{total_tests}")
print(f"Success Rate: {(passed_tests/total_tests)*100:.0f}%")

if passed_tests == total_tests:
    print("\n🎉 ALL LOGIC VERIFIED - NO GUESSING!")
    print("✅ System is making intelligent, rule-based decisions")
else:
    print("\n⚠️ SOME TESTS FAILED - REVIEW NEEDED")

print("\n" + "="*70)
