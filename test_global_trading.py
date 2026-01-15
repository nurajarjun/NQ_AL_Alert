import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

from ml.global_trading import GlobalMarketManager
from datetime import datetime, time
import pytz

def test_sessions():
    manager = GlobalMarketManager()
    
    print(f"Timezone: {manager.timezone}")
    
    # Test specific times
    test_times = [
        (time(10, 0), 'NY_AM'),
        (time(14, 0), 'NY_PM'),
        (time(4, 0), 'LONDON'),
        (time(20, 0), 'ASIA'),
        (time(16, 30), 'POST')
    ]
    
    for t, expected in test_times:
        result = manager.get_current_session(current_time=t)
        print(f"Time {t} => {result} (Expected: {expected})")
        assert result == expected, f"Expected {expected}, got {result}"
        
    print("\n✅ GlobalMarketManager Session Logic Verified!")

if __name__ == "__main__":
    test_sessions()
