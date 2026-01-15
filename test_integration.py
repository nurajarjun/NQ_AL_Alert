
import asyncio
import logging
import sys
import os
from unittest.mock import MagicMock

# Add backend to path
sys.path.append(os.path.abspath("backend"))

# Mock Telegram Bot to avoid sending real messages during test
sys.modules['telegram'] = MagicMock()
sys.modules['telegram.Bot'] = MagicMock()

from main import receive_tradingview_alert, app
from fastapi import Request

# Configure Mock Request
class MockRequest:
    async def json(self):
        return {
            "symbol": "NQ",
            "direction": "LONG",
            "entry": 17000.0,
            "stop": 16950.0,
            "target1": 17100.0,
            "target2": 17200.0,
            "rsi": 60,
            "atr": 50,
            "volume_ratio": 1.2
        }

async def run_test():
    print("Simulating TradingView Webhook...")
    
    # Mock the request
    mock_request = MockRequest()
    
    # Call the endpoint function directly
    try:
        response = await receive_tradingview_alert(mock_request)
        
        print("\n--- RESPONSE ---")
        print(response)
        
        if "score" in response and response["score"] > 0:
            print("\nAlert Processed Successfully")
        else:
            print("\nAlert Processing Failed or Score is 0")
            
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    loop = asyncio.new_event_loop()
    loop.run_until_complete(run_test())
