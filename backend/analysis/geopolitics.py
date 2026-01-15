"""
Geopolitical Risk Analyzer
Tracks war, conflict, and global instability risks
"""

import logging
from typing import Dict, List

logger = logging.getLogger(__name__)

class GeopoliticsAnalyzer:
    """Analyzes geopolitical risks based on news keywords"""
    
    def __init__(self):
        # Weighted keywords for risk scoring
        self.risk_keywords = {
            # CRISIS LEVEL (Weight 3)
            'war': 3,
            'invasion': 3,
            'nuclear': 3,
            'missile': 3,
            'attack': 3,
            'conflict': 3,
            'military action': 3,
            
            # ELEVATED LEVEL (Weight 2)
            'sanctions': 2,
            'tension': 2,
            'hostage': 2,
            'crisis': 2,
            'threat': 2,
            'escalation': 2,
            
            # WATCH LEVEL (Weight 1)
            'protest': 1,
            'dispute': 1,
            'warning': 1,
            'diplomatic': 1,
            'trade ban': 1
        }
    
    def analyze_risk(self, headlines: List[str]) -> Dict:
        """
        Analyze list of headlines for geopolitical risk
        
        Returns:
            Dict with score (0-10) and risk level
        """
        total_score = 0
        detected_triggers = []
        
        for headline in headlines:
            headline_lower = headline.lower()
            
            # Scan for keywords
            for keyword, weight in self.risk_keywords.items():
                if keyword in headline_lower:
                    # Context check: Ensure it's not "Trade War" if we just want "War"
                    # (Simple check for now, can be enhanced)
                    total_score += weight
                    detected_triggers.append(f"{keyword} ({weight})")
        
        # Normalize Score (Cap at 10)
        # We expect ~5 headlines. If 3 have "War", score is 9.
        final_score = min(10, total_score)
        
        # Determine Risk Level
        if final_score >= 7:
            level = "CRITICAL"
            action = "HALT TRADING / HEDGE"
        elif final_score >= 4:
            level = "ELEVATED"
            action = "REDUCE SIZE"
        elif final_score >= 1:
            level = "LOW"
            action = "MONITOR"
        else:
            level = "NEUTRAL"
            action = "NORMAL"
            
        return {
            "score": final_score,
            "level": level,
            "action": action,
            "triggers": list(set(detected_triggers))[:5] # Unique top triggers
        }

if __name__ == "__main__":
    # Test
    analyzer = GeopoliticsAnalyzer()
    
    test_headlines = [
        "Oil prices surge as tensions rise in Middle East",
        "Diplomatic warning issued over trade dispute",
        "Market rallies on strong tech earnings"
    ]
    
    print(f"Testing headlines: {test_headlines}")
    result = analyzer.analyze_risk(test_headlines)
    print(f"Result: {result}")
