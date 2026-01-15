
import sys
import os
import asyncio
from datetime import datetime

# Setup paths
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from analysis.signal_generator import SignalGenerator

# Mocking the formatting logic from TelegramBotHandler
def format_alert(result):
    if not isinstance(result, dict):
        return str(result)

    lines = [f"🧠 **{result.get('symbol', 'NQ')} Analysis**", ""]
    
    # Prediction
    direction = result.get('direction', 'NEUTRAL')
    direction_emoji = "🟢" if direction in ['LONG', 'UP'] else "🔴" if direction in ['SHORT', 'DOWN'] else "⚪"
    lines.append(f"{direction_emoji} **PREDICTION: {direction}**")
    
    # ... (simplified common fields) ...
    lines.append(f"💪 Confidence: {result.get('confidence', 0):.1f}%")
    lines.append("")

    # EXPERT BIAS (The New Feature)
    bias = result.get('expert_bias', 'NEUTRAL')
    if bias and bias != "NEUTRAL":
        lines.append(f"🧠 **EXPERT: {bias}**")
        lines.append("")

    # NEWS (The New Feature)
    news = result.get('news_sentiment', {})
    if news and news.get('direction'):
        sentiment_emoji = "📈" if news['direction'] == 'BULLISH' else "📉"
        lines.append(f"{sentiment_emoji} **NEWS: {news['direction']} ({news.get('score', 0)}%)**")
        lines.append("")

    # Trade Setup
    lines.append(f"💰 **TRADE SETUP** {direction}")
    lines.append(f"📍 Entry: {result.get('entry', 0):,.2f}")
    lines.append(f"🛑 Stop: {result.get('stop', 0):,.2f}")
    lines.append(f"🎯 T1: {result.get('target1', 0):,.2f}")
    lines.append(f"🎯 T2: {result.get('target2', 0):,.2f}")
    lines.append("")
    
    # Economic
    econ = result.get('economic_context', {})
    if econ.get('risk_level') != 'NORMAL':
        lines.append(f"📅 **ECONOMIC RISK: {econ.get('risk_level')}**")
        lines.append("")

    return "\n".join(lines)

if __name__ == "__main__":
    if sys.platform == "win32":
        sys.stdout.reconfigure(encoding='utf-8')
        
    print("--- GENERATING LIVE SIGNAL ---")
    gen = SignalGenerator()
    signal = gen.generate_signal()
    
    if signal:
        print("\n--- TELEGRAM MESSAGE PREVIEW ---")
        print(format_alert(signal))
        print("--------------------------------")
    else:
        print("No signal generated.")
