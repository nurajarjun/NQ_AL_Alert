import asyncio
import sys
import os
from datetime import datetime, timedelta

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

from ai.context import ContextAnalyzer
from utils.economic_calendar import EconomicCalendar

async def simulate_time_checks():
    analyzer = ContextAnalyzer()
    calendar = EconomicCalendar()
    
    # Define test scenarios
    # "Tomorrow" = Monday Jan 12, 2026
    # "Friday" = Friday Jan 16, 2026 (Next Friday) 
    
    test_days = [
        ("Monday (Tomorrow)", datetime(2026, 1, 12)),
        ("Friday (Next)", datetime(2026, 1, 16))
    ]
    
    # 5 Times to test per day
    times_of_day = [
        (3, 30, "London Open (Odd)"),
        (8, 30, "Pre-Market / CPI Time"),
        (9, 45, "Market Open (Prime)"),
        (12, 30, "Lunch (Avoid)"),
        (14, 15, "Afternoon (Prime)"),
        (16, 5, "After Close"),
        (19, 30, "Asian Open (Odd)")
    ]
    
    print(f"{'DAY':<20} | {'TIME':<20} | {'SAFE?':<10} | {'QUALITY':<10} | {'REASON':<30}")
    print("-" * 100)
    
    for day_name, day_date in test_days:
        for hour, minute, desc in times_of_day:
            # Construct test time
            test_time = day_date.replace(hour=hour, minute=minute)
            
            # Check Economic Calendar
            is_safe, event_name = await calendar.is_safe_to_trade(test_time)
            
            # Check Time Quality (using new refactored method)
            time_analysis = analyzer._analyze_time_of_day(test_time)
            quality = time_analysis['time_quality']
            
            # Format Output
            safe_str = "✅ YES" if is_safe else "❌ NO"
            reason_str = event_name if event_name else time_analysis['reason']
            time_str = test_time.strftime("%Y-%m-%d %H:%M")
            
            print(f"{day_name:<20} | {time_str:<20} | {safe_str:<10} | {quality:<10} | {reason_str:<30}")

if __name__ == "__main__":
    if sys.platform == 'win32':
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    asyncio.run(simulate_time_checks())
