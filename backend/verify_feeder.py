import sys
import os
import logging
import asyncio
from dotenv import load_dotenv

# Load env vars first
load_dotenv()

# Setup path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.knowledge.plan_feeder import PlanFeeder

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("VERIFY_FEEDER")

async def test_feeder():
    print("="*60)
    print("VERIFYING PLAN FEEDER")
    print("="*60)
    
    feeder = PlanFeeder()
    
    # Check if we have an API key (warn if not)
    if not feeder.analyzer.provider:
        print("WARNING: No AI Provider configured (OPENAI/GOOGLE API KEY missing).")
        print("Scraping will work, but AI parsing will rely on mock/fail.")
        # But we can still test the scraping part? 
        # PlanFeeder fetches then parses. If parse fails, it returns error.
        
    print("\n1. Fetching Latest Plan (Live Substack)...")
    result = await feeder.fetch_latest_plan()
    
    print(f"\nResult Status: {result.get('status')}")
    print(f"Message: {result.get('message', 'N/A')}")
    
    if result.get('status') == 'success':
        print("\nSUCCESS: Downloaded and parsed plan!")
        print(f"Title: {result.get('title')}")
        print(f"Date: {result.get('date')}")
        print(f"Regime: {result.get('regime')}")
    else:
        print("\nFAILURE or PARTIAL: See message above.")
        
    print("\n" + "="*60)

if __name__ == "__main__":
    asyncio.run(test_feeder())
