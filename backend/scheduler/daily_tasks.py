"""
Daily Scheduler for NQ AI Alert System
Handles automated tasks like Substack updates and model retraining
"""

import schedule
import time
import asyncio
import logging
from datetime import datetime
import sys
import os

# Setup paths
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def fetch_daily_plan():
    """Fetch Sabuj's daily trade plan from Substack at 6 AM ET"""
    try:
        logger.info("📋 Scheduled task: Fetching daily plan from Substack...")
        from knowledge.plan_feeder import PlanFeeder
        
        feeder = PlanFeeder()
        result = await feeder.fetch_latest_plan()
        
        if result['status'] == 'success':
            logger.info(f"✅ Daily plan updated: {result['title']}")
        else:
            logger.warning(f"⚠️ Daily plan fetch failed: {result['message']}")
            
    except Exception as e:
        logger.error(f"❌ Daily plan fetch error: {e}")

async def weekly_retrain():
    """Retrain ML models weekly on Sunday at 2 AM"""
    try:
        logger.info("🧠 Scheduled task: Weekly model retraining...")
        from auto_retrain import needs_retraining, run_retraining
        
        is_needed, reason = needs_retraining(days_threshold=7)
        
        if is_needed:
            logger.info(f"Retraining needed: {reason}")
            success, output = await run_retraining()
            
            if success:
                logger.info("✅ Weekly retrain completed successfully")
            else:
                logger.error(f"❌ Weekly retrain failed: {output[-500:]}")
        else:
            logger.info(f"✅ Models are fresh: {reason}")
            
    except Exception as e:
        logger.error(f"❌ Weekly retrain error: {e}")

def run_async_task(coro):
    """Helper to run async tasks in scheduler"""
    asyncio.run(coro)

def setup_scheduler():
    """Setup all scheduled tasks"""
    logger.info("⏰ Setting up daily scheduler...")
    
    # Daily plan fetch at 6:00 AM ET
    schedule.every().day.at("06:00").do(lambda: run_async_task(fetch_daily_plan()))
    logger.info("  ✅ Daily plan fetch scheduled for 6:00 AM ET")
    
    # Weekly model retraining on Sunday at 2:00 AM ET
    schedule.every().sunday.at("02:00").do(lambda: run_async_task(weekly_retrain()))
    logger.info("  ✅ Weekly retrain scheduled for Sunday 2:00 AM ET")
    
    logger.info("✅ Scheduler setup complete")

def run_scheduler():
    """Main scheduler loop - runs in background thread"""
    setup_scheduler()
    
    logger.info("🔄 Scheduler started - running in background")
    
    while True:
        schedule.run_pending()
        time.sleep(60)  # Check every minute

if __name__ == "__main__":
    # Test mode - run scheduler in foreground
    logger.info("Running scheduler in test mode...")
    run_scheduler()
