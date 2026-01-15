"""
Alert Formatter - Creates detailed, actionable Telegram alerts
"""

from typing import Dict
from datetime import datetime


class AlertFormatter:
    """Formats comprehensive trade alerts for Telegram"""
    
    @staticmethod
    def format_detailed_alert(
        signal_data: Dict,
        ai_analysis: Dict,
        trade_plan: Dict,
        context: Dict
    ) -> str:
        """
        Format a comprehensive trade alert with full trade plan
        
        Returns:
            Formatted message string for Telegram
        """
        
        direction = signal_data['direction']
        emoji = AlertFormatter._get_emoji(ai_analysis['score'])
        
        # Build the alert message
        message = f"""{emoji} AI TRADE PLAN - NQ {direction}

═══════════════════════════════════
📊 SIGNAL QUALITY
═══════════════════════════════════
AI Score: {ai_analysis['score']}/100
Recommendation: {ai_analysis['recommendation']}
Risk Level: {ai_analysis['risk_level']}
Confidence: {ai_analysis['confidence']*100:.0f}%

═══════════════════════════════════
🎯 ENTRY STRATEGY
═══════════════════════════════════
"""
        
        # Entry zones
        entry_zones = trade_plan['entry_zones']
        message += f"""Aggressive Entry: {entry_zones['aggressive']['price']} (50% position)
  → {entry_zones['aggressive']['description']}

Optimal Entry: {entry_zones['optimal']['price']} (30% position)
  → {entry_zones['optimal']['description']}

Conservative Entry: {entry_zones['conservative']['price']} (20% position)
  → {entry_zones['conservative']['description']}

═══════════════════════════════════
🎯 PROFIT TARGETS (4 Levels)
═══════════════════════════════════
"""
        
        # Targets
        for target in trade_plan['targets']:
            message += f"""Target {target['level']}: {target['price']} (R/R: {target['rr_ratio']}:1)
  → Take {target['take_profit']} profit
  → Probability: {target['probability']}%
  → {target['description']}

"""
        
        # Stop loss strategy
        stop_strategy = trade_plan['stop_loss']
        message += f"""═══════════════════════════════════
🛡️ STOP LOSS STRATEGY
═══════════════════════════════════
Initial Stop: {stop_strategy['initial_stop']['price']}
  → {stop_strategy['initial_stop']['description']}

Breakeven Rule:
  → {stop_strategy['breakeven_rule']['action']}

Trailing Stops:
"""
        
        for ts in stop_strategy['trailing_stops']:
            message += f"  • At {ts['trigger']}: Move stop to {ts['stop_price']}\n"
        
        # Position sizing
        sizing = trade_plan['position_sizing']
        message += f"""
═══════════════════════════════════
💼 POSITION SIZING
═══════════════════════════════════
Account Size: ${sizing['account_balance']:,.0f}
Risk Per Trade: {sizing['risk_per_trade']}
Contracts: {sizing['contracts_rounded']}
Max Loss: {sizing['max_loss']}
Risk Points: {sizing['risk_points']} pts

"""
        
        # Scenarios
        scenarios = trade_plan['scenarios']
        message += f"""═══════════════════════════════════
📈 PROFIT SCENARIOS
═══════════════════════════════════
🟢 BEST CASE ({scenarios['best_case']['probability']} probability)
  → All 4 targets hit
  → Profit: ${scenarios['best_case']['profit_usd']} ({scenarios['best_case']['profit_points']:.1f} pts)
  → R/R: {scenarios['best_case']['rr_ratio']}:1

🔵 EXPECTED CASE ({scenarios['expected_case']['probability']} probability)
  → Targets 1-2 hit
  → Profit: ${scenarios['expected_case']['profit_usd']} ({scenarios['expected_case']['profit_points']:.1f} pts)
  → R/R: {scenarios['expected_case']['rr_ratio']}:1

🟡 BREAKEVEN CASE ({scenarios['breakeven_case']['probability']} probability)
  → Target 1 hit, then breakeven
  → Profit: ${scenarios['breakeven_case']['profit_usd']} ({scenarios['breakeven_case']['profit_points']:.1f} pts)

🔴 WORST CASE ({scenarios['worst_case']['probability']} probability)
  → Stop loss hit
  → Loss: ${scenarios['worst_case']['profit_usd']} ({scenarios['worst_case']['profit_points']:.1f} pts)

"""
        
        # AI Insights
        message += f"""═══════════════════════════════════
💡 AI INSIGHTS
═══════════════════════════════════
"""
        for insight in ai_analysis['reasoning']:
            message += f"• {insight}\n"
        
        # Market Context
        ctx = trade_plan['market_context']
        message += f"""
═══════════════════════════════════
🌍 MARKET CONTEXT
═══════════════════════════════════
Sentiment: {ctx['sentiment']} ({ctx['sentiment_score']})
SPY Trend: {ctx['spy_trend']}
Volatility: {ctx['volatility']}
Time Quality: {ctx['time_quality']}

"""
        
        # Trade Management
        mgmt = trade_plan['management_plan']
        message += f"""═══════════════════════════════════
⚙️ TRADE MANAGEMENT
═══════════════════════════════════
Entry: {mgmt['entry_execution']['method']}
Max Hold: {mgmt['risk_management']['max_hold_time']}
Breakeven: {mgmt['risk_management']['breakeven_rule']}
Monitor: {mgmt['monitoring']['check_frequency']}

"""
        
        # Risk/Reward Analysis
        rr = trade_plan['risk_reward']
        message += f"""═══════════════════════════════════
⚖️ RISK/REWARD ANALYSIS
═══════════════════════════════════
Risk: {rr['risk_points']} pts (${rr['risk_usd']})
Weighted Reward: {rr['weighted_avg_reward']:.1f} pts (${rr['weighted_avg_reward_usd']})
Overall R/R: {rr['overall_rr']}:1
Assessment: {rr['assessment']}

"""
        
        # Exit Strategy
        message += f"""═══════════════════════════════════
🚪 EXIT STRATEGY
═══════════════════════════════════
{ai_analysis.get('exit_strategy', 'Standard scaling out at targets')}

Time Exits:
• {mgmt['risk_management']['max_hold_time']}
• Close before major news events
• Avoid holding through lunch chop

"""
        
        # Timestamp
        message += f"""═══════════════════════════════════
⏰ {datetime.now().strftime('%I:%M:%S %p ET | %B %d, %Y')}
═══════════════════════════════════"""
        
        return message
    
    @staticmethod
    def _get_emoji(score: int) -> str:
        """Get emoji based on AI score"""
        if score >= 80:
            return "🟢"
        elif score >= 70:
            return "🔵"
        elif score >= 60:
            return "🟡"
        elif score >= 50:
            return "🟠"
        else:
            return "🔴"
    
    @staticmethod
    def format_simple_alert(signal_data: Dict, ai_analysis: Dict, context: Dict) -> str:
        """Format a simpler alert (backward compatible)"""
        
        direction = signal_data['direction']
        entry = signal_data['entry']
        stop = signal_data['stop']
        target1 = signal_data.get('target1', 0)
        target2 = signal_data.get('target2', 0)
        
        risk = abs(entry - stop)
        reward1 = abs(target1 - entry)
        reward2 = abs(target2 - entry)
        rr1 = round(reward1 / risk, 2) if risk > 0 else 0
        rr2 = round(reward2 / risk, 2) if risk > 0 else 0
        
        emoji = AlertFormatter._get_emoji(ai_analysis['score'])
        
        sentiment = context.get('sentiment', {})
        market = context.get('market_conditions', {})
        time_info = context.get('time_analysis', {})
        
        reasoning_text = "\n".join([f"• {r}" for r in ai_analysis.get('reasoning', [])])
        
        message = f"""{emoji} AI-ANALYZED NQ {direction} SETUP

📊 SIGNAL DETAILS
Entry: {entry:.2f}
Stop: {stop:.2f} ({-risk:.2f} pts)
Target 1: {target1:.2f} (+{reward1:.2f} pts, {rr1}:1)
Target 2: {target2:.2f} (+{reward2:.2f} pts, {rr2}:1)

🤖 AI ANALYSIS
{ai_analysis['recommendation']} - Score: {ai_analysis['score']}/100
Risk Level: {ai_analysis['risk_level']}
Position Size: {ai_analysis['position_size']}
Confidence: {ai_analysis['confidence']*100:.0f}%

💡 KEY INSIGHTS
{reasoning_text}

📈 MARKET CONTEXT
Sentiment: {sentiment.get('fear_greed_text', 'Unknown')} ({sentiment.get('fear_greed_index', 'N/A')})
SPY: {market.get('spy_trend', 'Unknown')} ({market.get('spy_change_pct', 0):+.2f}%)
Time: {time_info.get('current_time', 'Unknown')} - {time_info.get('time_quality', 'Unknown')}

⏰ {datetime.now().strftime('%H:%M:%S ET')}
"""
        
        return message
