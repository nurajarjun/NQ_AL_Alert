import requests
from bs4 import BeautifulSoup
import logging
import json
import os
import re
from datetime import datetime
import asyncio
from typing import Dict, Any, List, Optional

# Adjust import based on where this file is located
if __name__ == "__main__":
    import sys
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from backend.ai.analyzer import AIAnalyzer
from backend.analysis.expert_input import ExpertContext

logger = logging.getLogger(__name__)

class PlanFeeder:
    """Automated feeder for daily trade plans"""
    
    ARCHIVE_URL = "https://sabujsengupta.substack.com/archive"
    
    def __init__(self):
        self.analyzer = AIAnalyzer()
        self.expert = ExpertContext()
        
    async def fetch_latest_plan(self) -> Dict[str, Any]:
        """Fetch and parse the latest trade plan"""
        try:
            logger.info("Checking Substack archive for new plans...")
            
            # 1. Fetch Archive
            response = requests.get(self.ARCHIVE_URL, headers={'User-Agent': 'Mozilla/5.0'})
            if response.status_code != 200:
                raise Exception(f"Failed to fetch archive: {response.status_code}")
                
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # 2. Find latest "Trade Plan" post
            latest_url = None
            latest_title = None
            
            # Look for links containing "Trade Plan" or "SPX"
            for link in soup.find_all('a'):
                title = link.get_text().strip()
                href = link.get('href')
                
                # logger.info(f"Checking link: {title} -> {href}")
                
                if title and href:
                    if ("Trade Plan" in title or "SPX" in title) and ("/p/" in href or "/post/" in href):
                        latest_url = href
                        latest_title = title
                        logger.info(f"Match found: {title} ({href})")
                        break # Take the first one (newest)
            
            if not latest_url:
                return {"status": "error", "message": "No trade plan found in archive"}
                
            logger.info(f"Found potential plan: {latest_title}")
            
            # 3. Fetch Article Content
            article_resp = requests.get(latest_url, headers={'User-Agent': 'Mozilla/5.0'})
            article_soup = BeautifulSoup(article_resp.text, 'html.parser')
            
            # Extract text (simple approach)
            content_text = article_soup.get_text(separator='\n')
            
            # Truncate if too long to save tokens, keep first 5000 chars which usually has the plan
            content_sample = content_text[:6000]
            
            # 4. AI Parse
            parsed_plan = await self._parse_with_ai(content_sample, latest_title)
            
            # 5. Save if valid
            if parsed_plan:
                self._save_plan(parsed_plan)
                return {
                    "status": "success", 
                    "title": latest_title, 
                    "date": parsed_plan.get('date'),
                    "regime": parsed_plan.get('regime')
                }
            else:
                return {"status": "error", "message": "AI failed to parse plan"}
                
        except Exception as e:
            logger.error(f"PlanFeeder error: {e}")
            return {"status": "error", "message": str(e)}
            
    async def _parse_with_ai(self, text: str, title: str) -> Dict:
        """Use Gemini/OpenAI to extract JSON plan"""
        prompt = f"""
        Analyze this trading blog post title and content. Extract the daily trading plan for SPX/ES.
        
        Title: {title}
        Content:
        {text}
        
        Return a JSON object ONLY with this structure:
        {{
            "date": "YYYY-MM-DD",
            "regime": "Pin/Range" or "Trend" or "Balanced",
            "bias": "LONG" or "SHORT" or "NEUTRAL",
            "sentiment": "Brief summary",
            "key_levels": {{
                "magnet": float (Max Pain or Pivot),
                "support": [list of floats],
                "resistance": [list of floats]
            }},
            "strategy": {{
                "focus": "Mean Reversion" or "Trend Following",
                "notes": ["Key point 1", "Key point 2"]
            }}
        }}
        """
        
        try:
            # We can reuse the analyzer's internal LLM methods if we expose them or just use a new prompt method
            # For simplicity, let's assume we can access the internal model wrapper or just standard generation
            if hasattr(self.analyzer, 'model'): # Gemini
                response = self.analyzer.model.generate_content(prompt)
                return self.analyzer._extract_json(response.text)
            elif hasattr(self.analyzer, 'client'): # OpenAI
                # Re-implement simple call or refactor analyzer to expose generic 'generate'
                # Let's try to verify what AIAnalyzer has. It has _analyze_with_gemini but it takes a prompt.
                # Yes, we can just use _analyze_with_gemini(prompt) directly? 
                # No, that method calls self.model.generate_content.
                
                # Hack: Just use `analyze_trade`? No, that expects signal data.
                # Let's use the underlying model directly if possible.
                
                if self.analyzer.provider == "gemini":
                    return await self.analyzer._analyze_with_gemini(prompt)
                elif self.analyzer.provider == "openai":
                    return await self.analyzer._analyze_with_openai(prompt)
                    
            return None
            
        except Exception as e:
            logger.error(f"AI Parse failed: {e}")
            return None

    def _save_plan(self, plan: Dict):
        """Save to daily_plan.json"""
        path = os.path.join(os.path.dirname(__file__), "daily_plan.json")
        with open(path, 'w') as f:
            json.dump(plan, f, indent=4)
        logger.info(f"Saved new plan to {path}")
        
        # Refresh singleton
        self.expert.refresh()
