"""
Verification script to test all 3 features
"""
import sys
sys.path.insert(0, 'backend')

print("="*60)
print("VERIFICATION TEST - 3 Features")
print("="*60)

# Test 1: Check if models loaded
print("\n1. Testing Multi-Symbol Model Loading...")
try:
    from ml.xgboost_model import XGBoostPredictor
    
    symbols = ["NQ", "ES", "TQQQ", "SQQQ", "SOXL", "SOXS"]
    loaded = []
    
    for symbol in symbols:
        model = XGBoostPredictor(symbol=symbol)
        if model.is_trained:
            loaded.append(symbol)
            print(f"   ✅ {symbol} model loaded")
        else:
            print(f"   ❌ {symbol} model NOT trained")
    
    print(f"\n   Result: {len(loaded)}/6 models loaded")
    
except Exception as e:
    print(f"   ❌ Error: {e}")

# Test 2: Check Bitcoin Correlation
print("\n2. Testing Bitcoin Correlation...")
try:
    from analysis.market_correlations import MarketCorrelations
    
    analyzer = MarketCorrelations()
    # Check if BTC method exists
    if hasattr(analyzer, '_get_btc_analysis'):
        print("   ✅ Bitcoin correlation method exists")
        # Try to run it
        import asyncio
        result = analyzer._get_btc_analysis()
        if result and 'price' in result:
            print(f"   ✅ BTC analysis works: ${result['price']:.2f}")
        else:
            print("   ⚠️ BTC method exists but returned no data")
    else:
        print("   ❌ Bitcoin correlation method NOT found")
        
except Exception as e:
    print(f"   ❌ Error: {e}")

# Test 3: Check Earnings Calendar
print("\n3. Testing Earnings Calendar Integration...")
try:
    from analysis.enhanced_scanner import EnhancedStockScanner
    
    scanner = EnhancedStockScanner()
    print("   ✅ Enhanced scanner imports successfully")
    
    # Check if earnings_warning is in the analysis
    import asyncio
    result = asyncio.run(scanner._analyze_stock_enhanced('AAPL'))
    
    if result and 'earnings_warning' in result:
        print("   ✅ Earnings calendar field exists")
        if result['earnings_warning']:
            print(f"   ✅ AAPL: {result['earnings_warning']}")
        else:
            print("   ✅ AAPL: No earnings in next 7 days")
    else:
        print("   ❌ Earnings calendar field NOT in results")
        
except Exception as e:
    print(f"   ❌ Error: {e}")

print("\n" + "="*60)
print("VERIFICATION COMPLETE")
print("="*60)
