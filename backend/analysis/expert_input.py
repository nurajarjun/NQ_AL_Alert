import json
import os
import logging
from typing import Dict, List, Optional
from datetime import datetime

logger = logging.getLogger(__name__)

class ExpertContext:
    """Provides expert market context from daily trading plan"""
    
    _instance = None
    _file_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "knowledge", "daily_plan.json")
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(ExpertContext, cls).__new__(cls)
            cls._instance._load_data()
        return cls._instance
    
    def _load_data(self):
        """Load daily plan from JSON"""
        try:
            if os.path.exists(self._file_path):
                with open(self._file_path, 'r') as f:
                    self.data = json.load(f)
                logger.info(f"Loaded Expert Context for {self.data.get('date', 'Unknown')}")
            else:
                self.data = {}
                logger.warning("No daily plan found")
        except Exception as e:
            logger.error(f"Failed to load daily plan: {e}")
            self.data = {}

    def refresh(self):
        """Force reload of data"""
        self._load_data()

    def get_context_string(self) -> str:
        """Get formatted context string for LLM prompt"""
        if not self.data:
            return ""
            
        try:
            levels = self.data.get('key_levels', {})
            support = ", ".join([str(x) for x in levels.get('support', [])])
            resistance = ", ".join([str(x) for x in levels.get('resistance', [])])
            magnet = levels.get('magnet', 'N/A')
            
            return f"""
EXPERT DAILY PLAN ({self.data.get('date')}):
- Regime: {self.data.get('regime')}
- Bias: {self.data.get('bias')}
- Strategy: {self.data.get('strategy', {}).get('focus')}
- Key Levels: Support [{support}] | Resistance [{resistance}] | Magnet [{magnet}]
- Notes: {'; '.join(self.data.get('strategy', {}).get('notes', []))}
"""
        except Exception as e:
            logger.error(f"Error formatting context: {e}")
            return ""

    def get_magnet_level(self) -> Optional[float]:
        """Get the magnet/max pain level if available"""
        return self.data.get('key_levels', {}).get('magnet')

    def get_nq_context(self) -> Dict:
        """
        Derive NQ context from SPX/ES plan
        Rationale: NQ and ES are highly correlated (0.9+). 
        If ES is in 'Mean Reversion' (Pin), NQ likely is too.
        """
        if not self.data:
            return {}
            
        regime = self.data.get('regime', 'Unknown')
        strategy = self.data.get('strategy', {}).get('focus', 'Neutral')
        
        return {
            "source_market": "SPX/ES",
            "implied_regime": regime,
            "implied_strategy": strategy,
            "note": f"Applying {regime} logic from SPX to NQ due to high correlation."
        }
