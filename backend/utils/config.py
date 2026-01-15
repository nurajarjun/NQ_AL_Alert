import json
import os
import logging
from typing import Dict, Any

logger = logging.getLogger(__name__)

class ConfigManager:
    """Manages persistent configuration settings"""
    
    _instance = None
    _config_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "config.json")
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(ConfigManager, cls).__new__(cls)
            cls._instance._load_config()
        return cls._instance
    
    def _load_config(self):
        """Load config from file"""
        self.config = {
            "alert_threshold": 60,  # Default
            "autonomous_enabled": False,
            "symbols": ["NQ", "ES"],
            "risk_per_trade": 0.01
        }
        
        if os.path.exists(self._config_path):
            try:
                with open(self._config_path, 'r') as f:
                    saved_config = json.load(f)
                    self.config.update(saved_config)
                logger.info(f"Config loaded from {self._config_path}")
            except Exception as e:
                logger.error(f"Failed to load config: {e}")
    
    def save_config(self):
        """Save config to file"""
        try:
            with open(self._config_path, 'w') as f:
                json.dump(self.config, f, indent=4)
            logger.info(f"Config saved to {self._config_path}")
        except Exception as e:
            logger.error(f"Failed to save config: {e}")
            
    def get(self, key: str, default: Any = None) -> Any:
        """Get config value"""
        return self.config.get(key, default)
        
    def set(self, key: str, value: Any):
        """Set config value and save"""
        self.config[key] = value
        self.save_config()
