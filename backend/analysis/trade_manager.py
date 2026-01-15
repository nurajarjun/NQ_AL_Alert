"""
Trade Manager
Tracks active trades and monitors continuously for targets/stops.
"""

import logging
from typing import Dict, List, Optional
import datetime
import pandas as pd
import os
import csv

logger = logging.getLogger(__name__)

class TradeManager:
    def __init__(self, history_file="backend/data/trade_history.csv"):
        self.active_trades: List[Dict] = []
        self.max_trades = 5 # Safety limit
        self.history_file = history_file
        
        # Ensure dir exists
        os.makedirs(os.path.dirname(self.history_file), exist_ok=True)
        # Init header if needed
        if not os.path.exists(self.history_file):
            with open(self.history_file, 'w', newline='') as f:
                writer = csv.writer(f)
                writer.writerow(['timestamp', 'symbol', 'direction', 'entry', 'exit', 'pnl', 'result', 'confluence'])
        
    def add_trade(self, trade_setup: Dict) -> bool:
        """Register a new trade to monitor"""
        try:
            # Check duplicates (simple entry price check)
            for trade in self.active_trades:
                if abs(trade['entry'] - trade_setup['entry']) < 2.0:
                    logger.info("Trade already active, skipping duplicate.")
                    return False
            
            # Create monitorable trade object
            trade = {
                'id': datetime.datetime.now().strftime("%H%M%S"),
                'symbol': 'NQ',
                'direction': trade_setup['direction'],
                'entry': trade_setup['entry'],
                'target1': trade_setup['target1'],
                'target2': trade_setup['target2'],
                'stop_loss': trade_setup['stop_loss'],
                't1_hit': False,
                't2_hit': False,
                'timestamp': datetime.datetime.now().isoformat(),
                'confluence': trade_setup.get('confluence', 'N/A')
            }
            
            self.active_trades.append(trade)
            
            # Keep list small
            if len(self.active_trades) > self.max_trades:
                self.active_trades.pop(0)
                
            logger.info(f"Added trade to monitor: {trade['direction']} @ {trade['entry']}")
            return True
            
        except Exception as e:
            logger.error(f"Error adding trade: {e}")
            return False

    def check_updates(self, current_price: float) -> List[str]:
        """
        Check all active trades against current price.
        Returns list of alert messages to send.
        """
        updates = []
        trades_to_remove = []
        
        for trade in self.active_trades:
            msg = None
            
            # --- LONG ---
            if trade['direction'] in ['LONG', 'UP']:
                # STOP LOSS HIT
                if current_price <= trade['stop_loss']:
                    msg = f"🛑 **STOP LOSS HIT** @ {current_price:.2f} (-{abs(trade['entry'] - current_price):.0f} pts)"
                    trades_to_remove.append(trade)
                    self._save_trade(trade, "LOSS", current_price, current_price - trade['entry'])
                
                # TARGET 1 HIT (First time only)
                elif current_price >= trade['target1'] and not trade['t1_hit']:
                    gain = current_price - trade['entry']
                    msg = (
                        f"💰 **TARGET 1 HIT!** @ {current_price:.2f} (+{gain:.0f} pts)\n\n"
                        f"🛡️ **ACTION:** Lock 50% Profit & Slide Stop to Entry!"
                    )
                    trade['t1_hit'] = True
                
                # TARGET 2 HIT
                elif current_price >= trade['target2'] and not trade['t2_hit']:
                    gain = current_price - trade['entry']
                    msg = f"🚀 **TARGET 2 HIT!** @ {current_price:.2f} (+{gain:.0f} pts)\n\n🥂 Crushed it! Close remaining."
                    trade['t2_hit'] = True
                    trades_to_remove.append(trade) # Close trade
                    self._save_trade(trade, "WIN_T2", current_price, current_price - trade['entry'])
                    
            # --- SHORT ---
            elif trade['direction'] in ['SHORT', 'DOWN']:
                # STOP LOSS HIT
                if current_price >= trade['stop_loss']:
                    msg = f"🛑 **STOP LOSS HIT** @ {current_price:.2f} (-{abs(current_price - trade['entry']):.0f} pts)"
                    trades_to_remove.append(trade)
                    self._save_trade(trade, "LOSS", current_price, trade['entry'] - current_price)
                
                # TARGET 1 HIT
                elif current_price <= trade['target1'] and not trade['t1_hit']:
                    gain = trade['entry'] - current_price
                    msg = (
                        f"💰 **TARGET 1 HIT!** @ {current_price:.2f} (+{gain:.0f} pts)\n\n"
                        f"🛡️ **ACTION:** Lock 50% Profit & Slide Stop to Entry!"
                    )
                    trade['t1_hit'] = True
                
                # TARGET 2 HIT
                elif current_price <= trade['target2'] and not trade['t2_hit']:
                    gain = trade['entry'] - current_price
                    msg = f"🚀 **TARGET 2 HIT!** @ {current_price:.2f} (+{gain:.0f} pts)\n\n🥂 Crushed it! Close remaining."
                    trade['t2_hit'] = True
                    trades_to_remove.append(trade)
                    self._save_trade(trade, "WIN_T2", current_price, trade['entry'] - current_price)
            
            if msg:
                updates.append(msg)
        
        # Cleanup closed trades
        for t in trades_to_remove:
            if t in self.active_trades:
                self.active_trades.remove(t)
                
        return updates

    def _save_trade(self, trade: Dict, result: str, exit_price: float, pnl: float):
        """Save closed trade to history CSV"""
        try:
            with open(self.history_file, 'a', newline='') as f:
                writer = csv.writer(f)
                writer.writerow([
                    datetime.datetime.now().isoformat(),
                    trade['symbol'],
                    trade['direction'],
                    trade['entry'],
                    exit_price,
                    f"{pnl:.2f}",
                    result,
                    trade.get('confluence', 'N/A')
                ])
            logger.info(f"Saved trade result: {result} ({pnl:.2f} pts)")
        except Exception as e:
            logger.error(f"Failed to save trade history: {e}")
