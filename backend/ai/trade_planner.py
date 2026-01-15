"""
Advanced Trade Planner - Provides detailed trade plans with multiple scenarios
Uses AI analysis + historical patterns to generate comprehensive trading strategies
"""

import os
from typing import Dict, List, Optional
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)


class TradePlanner:
    """Generates detailed trade plans with multiple targets and scenarios"""
    
    def __init__(self):
        self.risk_per_trade = 0.01  # 1% default risk
        
    def generate_trade_plan(
        self, 
        signal_data: Dict, 
        ai_analysis: Dict,
        context: Dict,
        account_balance: float = 10000
    ) -> Dict:
        """
        Generate comprehensive trade plan with multiple scenarios
        
        Args:
            signal_data: Original signal from TradingView
            ai_analysis: AI analysis results
            context: Market context
            account_balance: Account size for position sizing
            
        Returns:
            Detailed trade plan with entries, exits, scenarios
        """
        
        direction = signal_data['direction']
        entry = signal_data['entry']
        stop = signal_data['stop']
        atr = signal_data.get('atr', 40)
        
        # Calculate risk
        risk_points = abs(entry - stop)
        
        # Generate entry zones
        entry_zones = self._calculate_entry_zones(entry, direction, atr)
        
        # Generate multiple take-profit targets
        targets = self._calculate_targets(entry, stop, direction, atr, ai_analysis)
        
        # Calculate position sizing
        position_sizing = self._calculate_position_sizing(
            account_balance, 
            risk_points, 
            ai_analysis
        )
        
        # Generate stop-loss strategy
        stop_strategy = self._generate_stop_strategy(entry, stop, targets, direction)
        
        # Create trade management plan
        management_plan = self._create_management_plan(targets, ai_analysis)
        
        # Generate scenarios
        scenarios = self._generate_scenarios(entry, targets, stop, ai_analysis)
        
        # Time-based exit rules
        time_exits = self._calculate_time_exits(context)
        
        # Risk/reward analysis
        rr_analysis = self._analyze_risk_reward(entry, stop, targets)
        
        return {
            "timestamp": datetime.now().isoformat(),
            "direction": direction,
            "ai_score": ai_analysis['score'],
            "ai_recommendation": ai_analysis['recommendation'],
            "entry_zones": entry_zones,
            "targets": targets,
            "stop_loss": stop_strategy,
            "position_sizing": position_sizing,
            "management_plan": management_plan,
            "scenarios": scenarios,
            "time_exits": time_exits,
            "risk_reward": rr_analysis,
            "market_context": self._summarize_context(context)
        }
    
    def _calculate_entry_zones(self, entry: float, direction: str, atr: float) -> Dict:
        """Calculate optimal entry zones"""
        
        if direction == "LONG":
            # Best entry (aggressive)
            best_entry = entry
            # Good entry (wait for pullback)
            good_entry = entry - (atr * 0.25)
            # Conservative entry (deeper pullback)
            conservative_entry = entry - (atr * 0.5)
            
        else:  # SHORT
            best_entry = entry
            good_entry = entry + (atr * 0.25)
            conservative_entry = entry + (atr * 0.5)
        
        return {
            "aggressive": {
                "price": round(best_entry, 2),
                "description": "Enter immediately at market",
                "allocation": "50% of position"
            },
            "optimal": {
                "price": round(good_entry, 2),
                "description": "Wait for small pullback",
                "allocation": "30% of position"
            },
            "conservative": {
                "price": round(conservative_entry, 2),
                "description": "Wait for deeper pullback",
                "allocation": "20% of position"
            }
        }
    
    def _calculate_targets(
        self, 
        entry: float, 
        stop: float, 
        direction: str, 
        atr: float,
        ai_analysis: Dict
    ) -> List[Dict]:
        """Calculate multiple take-profit targets"""
        
        risk = abs(entry - stop)
        
        # Base targets on R multiples and ATR
        if direction == "LONG":
            targets = [
                {
                    "level": 1,
                    "price": round(entry + (risk * 1.5), 2),
                    "rr_ratio": 1.5,
                    "take_profit": "50%",
                    "probability": 70,
                    "description": "Quick profit, secure 50% of position"
                },
                {
                    "level": 2,
                    "price": round(entry + (risk * 2.5), 2),
                    "rr_ratio": 2.5,
                    "take_profit": "30%",
                    "probability": 50,
                    "description": "Main target, take 30% more"
                },
                {
                    "level": 3,
                    "price": round(entry + (risk * 4), 2),
                    "rr_ratio": 4.0,
                    "take_profit": "15%",
                    "probability": 30,
                    "description": "Extended target, let it run"
                },
                {
                    "level": 4,
                    "price": round(entry + (atr * 4), 2),
                    "rr_ratio": round((atr * 4) / risk, 2),
                    "take_profit": "5%",
                    "probability": 15,
                    "description": "Moon shot, trail remaining position"
                }
            ]
        else:  # SHORT
            targets = [
                {
                    "level": 1,
                    "price": round(entry - (risk * 1.5), 2),
                    "rr_ratio": 1.5,
                    "take_profit": "50%",
                    "probability": 70,
                    "description": "Quick profit, secure 50% of position"
                },
                {
                    "level": 2,
                    "price": round(entry - (risk * 2.5), 2),
                    "rr_ratio": 2.5,
                    "take_profit": "30%",
                    "probability": 50,
                    "description": "Main target, take 30% more"
                },
                {
                    "level": 3,
                    "price": round(entry - (risk * 4), 2),
                    "rr_ratio": 4.0,
                    "take_profit": "15%",
                    "probability": 30,
                    "description": "Extended target, let it run"
                },
                {
                    "level": 4,
                    "price": round(entry - (atr * 4), 2),
                    "rr_ratio": round((atr * 4) / risk, 2),
                    "take_profit": "5%",
                    "probability": 15,
                    "description": "Moon shot, trail remaining position"
                }
            ]
        
        # Adjust probabilities based on AI score
        score = ai_analysis.get('score', 50)
        adjustment = (score - 50) / 100  # -0.5 to +0.5
        
        for target in targets:
            target['probability'] = max(5, min(95, int(target['probability'] * (1 + adjustment))))
        
        return targets
    
    def _calculate_position_sizing(
        self, 
        account_balance: float, 
        risk_points: float,
        ai_analysis: Dict
    ) -> Dict:
        """Calculate position size based on risk and AI confidence"""
        
        # Base position size (1% risk)
        base_risk_amount = account_balance * self.risk_per_trade
        
        # Adjust based on AI confidence
        confidence = ai_analysis.get('confidence', 0.5)
        score = ai_analysis.get('score', 50)
        
        # Risk multiplier based on AI analysis
        if score >= 80 and confidence >= 0.75:
            risk_multiplier = 1.5  # Increase risk for high-quality setups
        elif score >= 70:
            risk_multiplier = 1.0  # Standard risk
        elif score >= 60:
            risk_multiplier = 0.5  # Reduce risk for marginal setups
        else:
            risk_multiplier = 0.25  # Minimal risk for low-quality
        
        adjusted_risk = base_risk_amount * risk_multiplier
        
        # Calculate contracts (NQ = $20 per point)
        point_value = 20
        contracts = adjusted_risk / (risk_points * point_value)
        
        return {
            "account_balance": account_balance,
            "risk_per_trade": f"{self.risk_per_trade * 100}%",
            "base_risk_amount": round(base_risk_amount, 2),
            "risk_multiplier": risk_multiplier,
            "adjusted_risk_amount": round(adjusted_risk, 2),
            "risk_points": round(risk_points, 2),
            "contracts": round(contracts, 2),
            "contracts_rounded": max(1, round(contracts)),
            "actual_risk": round(max(1, round(contracts)) * risk_points * point_value, 2),
            "max_loss": f"${round(max(1, round(contracts)) * risk_points * point_value, 2)}"
        }
    
    def _generate_stop_strategy(
        self, 
        entry: float, 
        initial_stop: float, 
        targets: List[Dict],
        direction: str
    ) -> Dict:
        """Generate dynamic stop-loss strategy"""
        
        return {
            "initial_stop": {
                "price": round(initial_stop, 2),
                "description": "Hard stop, do not move wider"
            },
            "breakeven_rule": {
                "trigger": targets[0]['price'],
                "action": f"Move stop to breakeven (entry: {entry}) when Target 1 hit",
                "description": "Protect capital, ensure no loss"
            },
            "trailing_stops": [
                {
                    "trigger": targets[0]['price'],
                    "stop_price": round(entry, 2),
                    "description": "Move to breakeven after Target 1"
                },
                {
                    "trigger": targets[1]['price'],
                    "stop_price": targets[0]['price'],
                    "description": "Move to Target 1 after Target 2 hit"
                },
                {
                    "trigger": targets[2]['price'],
                    "stop_price": targets[1]['price'],
                    "description": "Move to Target 2 after Target 3 hit"
                }
            ],
            "time_stop": {
                "rule": "Close position if no movement toward Target 1 within 2 hours",
                "reason": "Avoid dead trades, capital efficiency"
            }
        }
    
    def _create_management_plan(self, targets: List[Dict], ai_analysis: Dict) -> Dict:
        """Create detailed trade management plan"""
        
        return {
            "entry_execution": {
                "method": "Scale in over 3 entries",
                "allocation": "50% aggressive, 30% optimal, 20% conservative",
                "max_time": "30 minutes to complete all entries"
            },
            "profit_taking": {
                "target_1": {
                    "action": "Take 50% profit",
                    "reason": "Lock in gains, reduce risk"
                },
                "target_2": {
                    "action": "Take 30% profit",
                    "reason": "Secure majority of position"
                },
                "target_3": {
                    "action": "Take 15% profit",
                    "reason": "Bank extended gains"
                },
                "target_4": {
                    "action": "Trail remaining 5%",
                    "reason": "Let winners run with trailing stop"
                }
            },
            "risk_management": {
                "max_hold_time": "4 hours (day trade)",
                "breakeven_rule": "Move stop to breakeven at Target 1",
                "scale_out": "Reduce position size at each target",
                "emergency_exit": "Close all if AI score drops or major news"
            },
            "monitoring": {
                "check_frequency": "Every 15 minutes",
                "watch_for": [
                    "Price action at targets",
                    "Volume changes",
                    "News releases",
                    "Market sentiment shifts"
                ]
            }
        }
    
    def _generate_scenarios(
        self, 
        entry: float, 
        targets: List[Dict], 
        stop: float,
        ai_analysis: Dict
    ) -> Dict:
        """Generate best/worst/expected case scenarios"""
        
        # Calculate P&L for each scenario (assuming 1 contract)
        point_value = 20
        risk_points = abs(entry - stop)
        
        return {
            "best_case": {
                "description": "All targets hit, perfect execution",
                "targets_hit": 4,
                "profit_points": sum([
                    abs(targets[0]['price'] - entry) * 0.5,
                    abs(targets[1]['price'] - entry) * 0.3,
                    abs(targets[2]['price'] - entry) * 0.15,
                    abs(targets[3]['price'] - entry) * 0.05
                ]),
                "profit_usd": round(sum([
                    abs(targets[0]['price'] - entry) * 0.5,
                    abs(targets[1]['price'] - entry) * 0.3,
                    abs(targets[2]['price'] - entry) * 0.15,
                    abs(targets[3]['price'] - entry) * 0.05
                ]) * point_value, 2),
                "probability": "15%",
                "rr_ratio": round(sum([
                    abs(targets[0]['price'] - entry) * 0.5,
                    abs(targets[1]['price'] - entry) * 0.3,
                    abs(targets[2]['price'] - entry) * 0.15,
                    abs(targets[3]['price'] - entry) * 0.05
                ]) / risk_points, 2)
            },
            "expected_case": {
                "description": "Target 1 and 2 hit, typical outcome",
                "targets_hit": 2,
                "profit_points": sum([
                    abs(targets[0]['price'] - entry) * 0.5,
                    abs(targets[1]['price'] - entry) * 0.3,
                    0  # Remaining 20% at breakeven
                ]),
                "profit_usd": round(sum([
                    abs(targets[0]['price'] - entry) * 0.5,
                    abs(targets[1]['price'] - entry) * 0.3
                ]) * point_value, 2),
                "probability": "50%",
                "rr_ratio": round(sum([
                    abs(targets[0]['price'] - entry) * 0.5,
                    abs(targets[1]['price'] - entry) * 0.3
                ]) / risk_points, 2)
            },
            "worst_case": {
                "description": "Stop loss hit, full loss",
                "targets_hit": 0,
                "profit_points": -risk_points,
                "profit_usd": round(-risk_points * point_value, 2),
                "probability": f"{100 - ai_analysis.get('confidence', 0.5) * 100:.0f}%",
                "rr_ratio": -1.0
            },
            "breakeven_case": {
                "description": "Target 1 hit, then stopped at breakeven",
                "targets_hit": 1,
                "profit_points": abs(targets[0]['price'] - entry) * 0.5,
                "profit_usd": round(abs(targets[0]['price'] - entry) * 0.5 * point_value, 2),
                "probability": "25%",
                "rr_ratio": round((abs(targets[0]['price'] - entry) * 0.5) / risk_points, 2)
            }
        }
    
    def _calculate_time_exits(self, context: Dict) -> Dict:
        """Calculate time-based exit rules"""
        
        time_info = context.get('time_analysis', {})
        current_time = time_info.get('current_time', 'Unknown')
        
        return {
            "max_hold": "4 hours for day trades",
            "avoid_holding": [
                "Through major news events (NFP, FOMC)",
                "Overnight (close before 4:00 PM ET)",
                "During lunch chop (11:30 AM - 2:00 PM ET)"
            ],
            "optimal_exit_times": [
                "Before 11:30 AM ET (morning session)",
                "Before 3:30 PM ET (avoid close volatility)"
            ],
            "current_time": current_time,
            "time_quality": time_info.get('time_quality', 'Unknown')
        }
    
    def _analyze_risk_reward(
        self, 
        entry: float, 
        stop: float, 
        targets: List[Dict]
    ) -> Dict:
        """Analyze overall risk/reward profile"""
        
        risk = abs(entry - stop)
        
        # Weighted average reward
        weighted_reward = sum([
            abs(t['price'] - entry) * (int(t['take_profit'].rstrip('%')) / 100)
            for t in targets
        ])
        
        return {
            "risk_points": round(risk, 2),
            "risk_usd": round(risk * 20, 2),  # NQ point value
            "weighted_avg_reward": round(weighted_reward, 2),
            "weighted_avg_reward_usd": round(weighted_reward * 20, 2),
            "overall_rr": round(weighted_reward / risk, 2),
            "assessment": self._assess_rr(weighted_reward / risk)
        }
    
    def _assess_rr(self, rr: float) -> str:
        """Assess risk/reward ratio quality"""
        if rr >= 3:
            return "Excellent - High reward potential"
        elif rr >= 2:
            return "Good - Favorable risk/reward"
        elif rr >= 1.5:
            return "Acceptable - Minimum threshold"
        else:
            return "Poor - Risk too high for reward"
    
    def _summarize_context(self, context: Dict) -> Dict:
        """Summarize market context"""
        sentiment = context.get('sentiment', {})
        market = context.get('market_conditions', {})
        time_info = context.get('time_analysis', {})
        
        return {
            "sentiment": sentiment.get('fear_greed_text', 'Unknown'),
            "sentiment_score": sentiment.get('fear_greed_index', 'N/A'),
            "spy_trend": market.get('spy_trend', 'Unknown'),
            "volatility": market.get('volatility_estimate', 'Unknown'),
            "time_quality": time_info.get('time_quality', 'Unknown')
        }
