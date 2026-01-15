"""
Simple Alert Formatter - Short, actionable alerts
"""

from datetime import datetime
import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config.symbols import format_symbol_header, get_symbol_warning, flip_direction_if_inverse


class SimpleAlertFormatter:
    """Creates short, actionable trading alerts"""
    
    @staticmethod
    def format_simple_alert(signal_data, ai_analysis, ml_prediction=None):
        """
        Format a SHORT, actionable alert
        
        Args:
            signal_data: Signal from TradingView
            ai_analysis: AI analysis results
            ml_prediction: ML prediction (optional)
            
        Returns:
            Short, clear alert message
        """
        direction = signal_data['direction']
        entry = signal_data['entry']
        stop = signal_data['stop']
        target1 = signal_data.get('target1', 0)
        target2 = signal_data.get('target2', 0)
        
        # Calculate R/R
        risk = abs(entry - stop)
        reward1 = abs(target1 - entry)
        rr = round(reward1 / risk, 1) if risk > 0 else 0
        
        # Get scores
        ai_score = ai_analysis.get('score', 50)
        ml_score = ml_prediction.get('combined_score', None) if ml_prediction else None
        
        # Combined score
        if ml_score:
            combined = int((ai_score + ml_score) / 2)
            score_text = f"AI:{ai_score} ML:{ml_score} = {combined}/100"
        else:
            combined = ai_score
            score_text = f"{ai_score}/100"
        
        # Emoji based on score
        if combined >= 80:
            emoji = "🟢"
            action = "STRONG BUY"
        elif combined >= 70:
            emoji = "🔵"
            action = "BUY"
        elif combined >= 60:
            emoji = "🟡"
            action = "CONSIDER"
        else:
            emoji = "🔴"
            action = "SKIP"
        
        # Build SHORT message
        message = f"""{emoji} NQ {direction} - {action}

💰 ENTRY: {entry}
🛑 STOP: {stop} (-{risk:.0f} pts)
🎯 TARGET: {target1} (+{reward1:.0f} pts)
📊 R/R: {rr}:1

🤖 SCORE: {score_text}
✅ {ai_analysis.get('recommendation', 'N/A')}

⏰ {datetime.now().strftime('%I:%M %p')}"""

        return message
    
    @staticmethod
    def format_trade_alert(signal_data, ai_analysis, ml_prediction=None):
        """
        Format REAL-TIME alert with PRECISE execution timing
        """
        # Get symbol (default to NQ)
        symbol = signal_data.get('symbol', 'NQ').upper()
        direction = signal_data['direction']
        entry = signal_data['entry']
        stop = signal_data['stop']
        target1 = signal_data.get('target1', 0)
        target2 = signal_data.get('target2', 0)
        rsi = signal_data.get('rsi', 50)
        
        risk = abs(entry - stop)
        reward1 = abs(target1 - entry)
        reward2 = abs(target2 - entry)
        rr1 = round(reward1 / risk, 1) if risk > 0 else 0
        rr2 = round(reward2 / risk, 1) if risk > 0 else 0
        
        # Scores
        ai_score = ai_analysis.get('score', 50)
        ml_score = ml_prediction.get('combined_score', None) if ml_prediction else None
        combined = int((ai_score + ml_score) / 2) if ml_score else ai_score
        
        # Action based on score
        if combined >= 80:
            emoji = "🟢"
            action = "EXECUTE NOW"
            urgency = "⚡ IMMEDIATE"
        elif combined >= 70:
            emoji = "🔵"
            action = "ENTER NOW"
            urgency = "🔥 HIGH PRIORITY"
        elif combined >= 60:
            emoji = "🟡"
            action = "WATCH & ENTER"
            urgency = "⏰ MONITOR"
        else:
            emoji = "🔴"
            action = "SKIP"
            urgency = "❌ AVOID"
        
        # Current time
        now = datetime.now()
        time_str = now.strftime('%I:%M:%S %p')
        
        # Symbol-specific header
        header = format_symbol_header(symbol, direction)
        
        # Entry instructions
        if direction == "LONG":
            entry_instruction = f"BUY at {entry} or BETTER (lower)"
            stop_instruction = f"STOP at {stop} (below entry)"
        else:
            entry_instruction = f"SELL at {entry} or BETTER (higher)"
            stop_instruction = f"STOP at {stop} (above entry)"
        

        # Get active threshold
        try:
            from utils.config import ConfigManager
            config = ConfigManager()
            threshold = config.get('alert_threshold', 'N/A')
        except:
            threshold = 'N/A'

        # Build message
        message = f"""{emoji} {urgency} - {header}

⚡ ACTION: {action}
🎯 {entry_instruction}
🛑 {stop_instruction}

📊 TARGETS
T1: {target1} ({rr1}:1) - Take 50%
T2: {target2} ({rr2}:1) - Take 50%

🤖 AI SCORE: {combined}/100 (Threshold: {threshold})"""

        if ml_score:
            message += f" (AI:{ai_score} ML:{ml_score})"
        
        message += f"""
✅ {ai_analysis.get('recommendation', 'N/A')}
⚠️ Risk: {ai_analysis.get('risk_level', 'MEDIUM')}
"""
        
        # Add symbol warning if exists
        warning = get_symbol_warning(symbol)
        if warning:
            message += f"\n{warning}\n"
        
        message += "\n💡 WHY NOW:\n"
        
        # Add top 2 insights
        reasoning = ai_analysis.get('reasoning', [])
        for i, insight in enumerate(reasoning[:2], 1):
            message += f"{i}. {insight}\n"
        
        message += f"""
📈 RSI: {rsi:.0f} | R/R: {rr1}:1

⏰ SIGNAL TIME: {time_str} ET
🚀 EXECUTE IMMEDIATELY"""
        
        return message
