
import sys
import os
import logging

# Setup paths
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from utils.config import ConfigManager
from analysis.signal_generator import SignalGenerator

# Configure logging to stdout
logging.basicConfig(level=logging.INFO, format='%(message)s')
logger = logging.getLogger("THRESHOLD_TEST")

def test_threshold_impact():
    config = ConfigManager()
    generator = SignalGenerator()
    
    print("\n========================================")
    print("      THRESHOLD CONTROL TEST            ")
    print("========================================")
    
    # 1. Simulate User setting strict threshold (e.g. /threshold 99)
    print("\n[TEST 1] User sets /threshold 99 (Impossible Mode)")
    config.set('alert_threshold', 99)
    config.set('adx_threshold', 0) # Disable Chop Filter for this test
    print("   -> Config updated. Generating signal...")
    
    signal_strict = generator.generate_signal()
    
    if signal_strict is None:
        print("   [OK] SUCCESS: Signal BLOCKED by high threshold.")
    else:
        print(f"   [FAIL] FAILURE: Signal generated despite 99 threshold! (Score: {signal_strict.get('score')})")

    # 2. Simulate User setting loose threshold (e.g. /threshold 10)
    print("\n[TEST 2] User sets /threshold 10 (Loose Mode)")
    config.set('alert_threshold', 10)
    print("   -> Config updated. Generating signal...")
    
    signal_loose = generator.generate_signal()
    
    signal_loose = generator.generate_signal()
    
    if signal_loose:
        print(f"   [OK] SUCCESS: Signal ALLOWED by low threshold.")
        print(f"      Direction: {signal_loose['direction']}")
    else:
        print("   [FAIL] FAILURE: No signal even with 10 threshold (Market might be completely dead 0/0).")

    # Reset to default
    print("\n[CLEANUP] Resetting threshold to 70 and chop to 25")
    config.set('alert_threshold', 70)
    config.set('adx_threshold', 25)

if __name__ == "__main__":
    try:
        test_threshold_impact()
    except Exception as e:
        print(f"Test crashed: {e}")
