import asyncio
import aiohttp
import xml.etree.ElementTree as ET
from datetime import datetime

async def test_ff_calendar():
    url = "https://nfs.faireconomy.media/ff_calendar_thisweek.xml"
    print(f"Fetching from {url}...")
    
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                if response.status == 200:
                    text = await response.text()
                    print(f"✅ Success! Received {len(text)} bytes")
                    
                    root = ET.fromstring(text)
                    count = 0
                    print("\n--- UPCOMING HIGH IMPACT EVENTS ---")
                    for event in root.findall('event'):
                        country = event.find('country').text
                        impact = event.find('impact').text
                        
                        if country == 'USD' and impact in ['High', 'Medium']:
                            title = event.find('title').text
                            date_str = event.find('date').text
                            time_str = event.find('time').text
                            
                            print(f"{date_str} {time_str}: {title} ({impact})")
                            count += 1
                            if count >= 10: break
                else:
                    print(f"❌ Failed with status: {response.status}")
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    if hasattr(asyncio, 'WindowsSelectorEventLoopPolicy'):
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    asyncio.run(test_ff_calendar())
