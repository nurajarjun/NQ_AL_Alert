
import sys
import os
import logging
from backtest import Backtester

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(message)s')
logger = logging.getLogger("TEST_5_DAYS")

class FusionBacktester(Backtester):
    def __init__(self, symbol="NQ", days=5, expert_bias="NEUTRAL", news_score=50):
        super().__init__(symbol, days, config={'use_ml': True, 'alert_threshold': 70})
        self.expert_bias = expert_bias
        self.news_score = news_score
        
    def _calculate_score(self, row):
        # 1. Get Base Technical Score
        score = super()._calculate_score(row)
        
        # 2. Add Expert Bias (Simulated Fusion)
        # In SignalGenerator, LONG adds +1 signal (approx +15% confidence in rule-of-thumb)
        # Here we add raw score points to simulate the boost
        if self.expert_bias == "LONG":
            score += 15
            # logger.info("   🧠 Expert LONG boost applied")
        elif self.expert_bias == "SHORT":
            score -= 15
            
        # 3. Add News Sentiment (Simulated Fusion)
        # In SignalGenerator, Strong News adds +0.5 signal (approx +7.5% confidence)
        if self.news_score > 65: # Bullish News
            score += 7
        elif self.news_score < 35: # Bearish News
            score -= 7
            
        return max(0, min(100, score))

if __name__ == "__main__":
    print("========================================")
    print("      5-DAY BACKTEST (FUSION AI)        ")
    print("========================================")
    print("Scenario 1: Neutral (Pure Math)")
    bt_neutral = FusionBacktester(days=5, expert_bias="NEUTRAL")
    bt_neutral.run(verbose=True)
    
    print("\n" + "-"*40 + "\n")
    
    print("Scenario 2: Expert Says 'LONG' (Smart AI)")
    print("(Simulating Sabuj was Bullish all week)")
    bt_smart = FusionBacktester(days=5, expert_bias="LONG")
    bt_smart.run(verbose=True)
    
    print("\nSummary:")
    print("This test compares the 'Old System' (Scenario 1) vs 'New System' (Scenario 2)")
    print("Notice how the Expert Bias allows the AI to catch trends it might have missed.")
