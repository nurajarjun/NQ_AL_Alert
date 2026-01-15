"""
Comprehensive System Test
Tests all major components and features
"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

import asyncio
from datetime import datetime

print("\n" + "="*80)
print("COMPREHENSIVE SYSTEM TEST")
print("="*80 + "\n")

test_results = []

# Test 1: ML Models
print("TEST 1: ML Models")
print("-" * 80)
try:
    from ml.xgboost_model import XGBoostPredictor
    
    symbols = ["NQ", "ES", "TQQQ", "SQQQ", "SOXL", "SOXS"]
    for symbol in symbols:
        model = XGBoostPredictor(symbol=symbol)
        status = "✅ TRAINED" if model.is_trained else "❌ NOT TRAINED"
        features = len(model.feature_names) if model.feature_names else 0
        print(f"  {symbol:6} {status:15} Features: {features}")
        test_results.append(("ML Model " + symbol, model.is_trained))
except Exception as e:
    print(f"  ❌ ERROR: {e}")
    test_results.append(("ML Models", False))

# Test 2: Geopolitics Analyzer
print("\nTEST 2: Geopolitics Analyzer")
print("-" * 80)
try:
    from analysis.geopolitics import GeopoliticsAnalyzer
    
    geo = GeopoliticsAnalyzer()
    test_headlines = ["Market rallies on tech earnings", "Tensions rise in Middle East"]
    result = geo.analyze_risk(test_headlines)
    print(f"  ✅ Geopolitics: {result['level']} risk (score: {result['score']})")
    test_results.append(("Geopolitics", True))
except Exception as e:
    print(f"  ❌ ERROR: {e}")
    test_results.append(("Geopolitics", False))

# Test 3: Evening Scalper
print("\nTEST 3: Evening Scalper")
print("-" * 80)
try:
    from analysis.evening_scalper import EveningScalper
    
    scalper = EveningScalper()
    print(f"  Assets: {len(scalper.assets)}")
    for ticker, info in scalper.assets.items():
        print(f"    • {ticker:4} - {info['name']}")
    print(f"  ✅ Evening Scalper initialized")
    test_results.append(("Evening Scalper", True))
except Exception as e:
    print(f"  ❌ ERROR: {e}")
    test_results.append(("Evening Scalper", False))

# Test 4: Substack Plan Feeder
print("\nTEST 4: Substack Plan Feeder")
print("-" * 80)
try:
    import json
    plan_file = os.path.join(os.path.dirname(__file__), 'backend', 'knowledge', 'daily_plan.json')
    
    if os.path.exists(plan_file):
        with open(plan_file, 'r') as f:
            plan = json.load(f)
        print(f"  ✅ Daily Plan Found")
        print(f"    Date: {plan.get('date')}")
        print(f"    Regime: {plan.get('regime')}")
        print(f"    Bias: {plan.get('bias')}")
        test_results.append(("Substack Plan", True))
    else:
        print(f"  ❌ No daily plan found")
        test_results.append(("Substack Plan", False))
except Exception as e:
    print(f"  ❌ ERROR: {e}")
    test_results.append(("Substack Plan", False))

# Test 5: Performance Reporter
print("\nTEST 5: Performance Reporter")
print("-" * 80)
try:
    from reports.performance_reporter import PerformanceReporter
    
    reporter = PerformanceReporter()
    print(f"  ✅ Performance Reporter initialized")
    print(f"    Reports dir: {reporter.reports_dir}")
    test_results.append(("Performance Reporter", True))
except Exception as e:
    print(f"  ❌ ERROR: {e}")
    test_results.append(("Performance Reporter", False))

# Test 6: Economic Calendar
print("\nTEST 6: Economic Calendar")
print("-" * 80)
try:
    from utils.economic_calendar import EconomicCalendar
    
    calendar = EconomicCalendar()
    print(f"  ✅ Economic Calendar initialized")
    test_results.append(("Economic Calendar", True))
except Exception as e:
    print(f"  ❌ ERROR: {e}")
    test_results.append(("Economic Calendar", False))

# Test 7: Earnings Calendar
print("\nTEST 7: Earnings Calendar")
print("-" * 80)
try:
    from utils.earnings_calendar import EarningsCalendar
    
    earnings = EarningsCalendar()
    print(f"  ✅ Earnings Calendar initialized")
    test_results.append(("Earnings Calendar", True))
except Exception as e:
    print(f"  ❌ ERROR: {e}")
    test_results.append(("Earnings Calendar", False))

# Summary
print("\n" + "="*80)
print("TEST SUMMARY")
print("="*80 + "\n")

passed = sum(1 for _, result in test_results if result)
total = len(test_results)
pass_rate = passed / total * 100 if total > 0 else 0

for test_name, result in test_results:
    status = "✅ PASS" if result else "❌ FAIL"
    print(f"{test_name:25} {status}")

print(f"\nTotal: {passed}/{total} tests passed ({pass_rate:.1f}%)")

if pass_rate == 100:
    print("\n🎉 ALL TESTS PASSED - SYSTEM READY!")
elif pass_rate >= 80:
    print("\n✅ SYSTEM MOSTLY READY - Minor issues to fix")
else:
    print("\n⚠️ SYSTEM NEEDS ATTENTION - Multiple failures")

print("\n" + "="*80 + "\n")
