import sys
import os
import logging
from typing import Dict

# Setup path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("VERIFY_EXPERT")

def test_expert_integration():
    print("="*60)
    print("VERIFYING EXPERT CONTEXT INTEGRATION")
    print("="*60)
    
    # 1. Verify Daily Plan Loading
    from analysis.expert_input import ExpertContext
    expert = ExpertContext()
    
    context_str = expert.get_context_string()
    magnet = expert.get_magnet_level()
    
    print("\n1. Expert Context Loaded:")
    print(f"   Date: {expert.data.get('date')}")
    print(f"   Magnet: {magnet}")
    print(f"   Context String Length: {len(context_str)}")
    
    if magnet == 6940:
        print("SUCCESS: Magnet level 6940 correctly loaded")
    else:
        print(f"FAILURE: Magnet level incorrect: {magnet}")

    # 2. Verify Score Adjustment (Analyzer)
    from ai.analyzer import AIAnalyzer
    analyzer = AIAnalyzer()
    
    print("\n2. Testing Score Adjustment (Magnet Logic)...")
    
    # Scene: Price at 6970 (Above Magnet), Signal SHORT -> Should be Boosted
    signal_aligned = {'entry': 6970, 'direction': 'SHORT'}
    analysis_aligned = {'score': 50, 'reasoning': []}
    
    print("   [Case A] Price 6970, Short (Aligned with Mean Reversion to 6940)")
    res_aligned = analyzer._validate_analysis(analysis_aligned, signal_aligned)
    print(f"   Score: {res_aligned['score']} (Expected 60)")
    if res_aligned['score'] == 60:
         print("SUCCESS: Score boosted (+10)")
    else:
         print(f"FAILURE: Score not boosted properly (Got {res_aligned['score']})")

    # Scene: Price at 6970 (Above Magnet), Signal LONG -> Should be Penalized
    signal_fighting = {'entry': 6970, 'direction': 'LONG'}
    analysis_fighting = {'score': 50, 'reasoning': []}
    
    print("   [Case B] Price 6970, Long (Fighting Mean Reversion)")
    res_fighting = analyzer._validate_analysis(analysis_fighting, signal_fighting)
    print(f"   Score: {res_fighting['score']} (Expected 40)")
    if res_fighting['score'] == 40:
         print("SUCCESS: Score penalized (-10)")
    else:
         print(f"FAILURE: Score not penalized properly (Got {res_fighting['score']})")

    # 3. Verify Key Levels (Calculator)
    from analysis.trade_calculator import TradeCalculator
    import pandas as pd
    
    print("\n3. Testing Key Levels Injection...")
    calc = TradeCalculator()
    
    # Create dummy dataframe with price near 6930
    df = pd.DataFrame({'Low': [6900]*50, 'Close': [6930]*50}) 
    
    levels = calc._calculate_support_levels(df, 6935)
    print(f"    calculated Levels: {levels}")
    
    if 6927 in levels:
        print("SUCCESS: Expert Level 6927 found in support levels")
    else:
        print("FAILURE: Expert Level 6927 MISSING")

    print("\n" + "="*60)

if __name__ == "__main__":
    test_expert_integration()
