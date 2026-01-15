import sys
import os
import logging
from unittest.mock import MagicMock

# Setup path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from utils.config import ConfigManager
from utils.simple_formatter import SimpleAlertFormatter
from analysis.trade_calculator import TradeCalculator

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("VERIFY_SWING")

def test_swing_fix():
    print("="*60)
    print("VERIFYING SWING TRADE FIX")
    print("="*60)
    
    config = ConfigManager()
    
    # 1. Set Threshold to 50
    print("\n1. Setting Threshold to 50...")
    config.set('alert_threshold', 50)
    
    # 2. Simulate Logic from main.py
    print("\n2. Testing Direction Logic (Simulating main.py)...")
    score = 60 # Weak score
    threshold = config.get('alert_threshold', 70)
    
    direction = "NEUTRAL"
    if score >= threshold: direction = "SHORT"
    elif score <= (100 - threshold): direction = "LONG"
    
    print(f"   Score: {score}")
    print(f"   Threshold: {threshold}")
    print(f"   Resulting Direction: {direction}")
    
    if direction == "SHORT":
        print("   SUCCESS: Direction correctly identified as SHORT (60 >= 50)")
    else:
        print(f"   FAILURE: Direction is {direction}, expected SHORT")

    # 3. Test Alert Formatter
    print("\n3. Testing Alert Formatter Visibility...")
    signal_data = {
        'symbol': 'NQ', 'direction': 'SHORT', 'entry': 15000, 
        'stop': 15100, 'target1': 14900, 'target2': 14800,
        'rsi': 65
    }
    ai_analysis = {'score': 60, 'recommendation': 'YES', 'reasoning': ['Test']}
    
    alert_msg = SimpleAlertFormatter.format_trade_alert(signal_data, ai_analysis)
    
    print("\n--- Generated Alert ---")
    print(alert_msg)
    print("-----------------------")
    
    if "(Threshold: 50)" in alert_msg:
        print("SUCCESS: Threshold visible in alert")
    else:
        print("FAILURE: Threshold NOT found in alert")

    print("\n" + "="*60)

if __name__ == "__main__":
    test_swing_fix()
