"""
AI Prompt Templates for NQ Alert Analysis
"""

class PromptTemplates:
    """Collection of AI prompts for different analysis tasks"""
    
    @staticmethod
    def get_trade_analysis_prompt(signal_data: dict, context_data: dict) -> str:
        """
        Generate prompt for AI to analyze a trading signal
        
        Args:
            signal_data: Trading signal details (entry, stop, targets, indicators)
            context_data: Market context (news, sentiment, conditions)
            
        Returns:
            Formatted prompt string for AI
        """
        
        # Extract signal details
        direction = signal_data.get('direction', 'N/A')
        entry = signal_data.get('entry', 0)
        stop = signal_data.get('stop', 0)
        target1 = signal_data.get('target1', 0)
        target2 = signal_data.get('target2', 0)
        rsi = signal_data.get('rsi', 0)
        atr = signal_data.get('atr', 0)
        volume_ratio = signal_data.get('volume_ratio', 1.0)
        
        # Calculate R/R
        if direction == "LONG":
            risk = entry - stop
            reward1 = target1 - entry
            reward2 = target2 - entry
        else:
            risk = stop - entry
            reward1 = entry - target1
            reward2 = entry - target2
        
        rr1 = round(reward1 / risk, 2) if risk > 0 else 0
        rr2 = round(reward2 / risk, 2) if risk > 0 else 0
        
        # Extract context
        sentiment = context_data.get('sentiment', {})
        market = context_data.get('market_conditions', {})
        time_info = context_data.get('time_analysis', {})
        news = context_data.get('news', [])
        econ = context_data.get('economic_events', {})
        
        # Build news summary with categories
        news_summary = ""
        if news:
            news_summary = "Recent Headlines:\n"
            for i, article in enumerate(news[:5], 1):
                category_tag = f"[{article.get('category', 'Market')}]"
                news_summary += f"{i}. {category_tag} {article['title']} ({article['sentiment']})\n"
        else:
            news_summary = "No recent significant news"

        # Economic Event Info
        next_event = econ.get('next_major_event')
        if next_event:
            econ_str = f"Next Event: {next_event['name']} in {next_event.get('days_away')} days (Impact: {next_event.get('impact')})"
        else:
            econ_str = "No major upcoming economic events"
        
        prompt = f"""You are an expert NQ (Nasdaq-100 E-mini) futures trader with 10+ years of experience. Analyze this trading setup and provide actionable guidance.

📊 TRADING SIGNAL
Direction: {direction}
Entry Price: {entry:.2f}
Stop Loss: {stop:.2f} (Risk: {risk:.2f} points)
Target 1: {target1:.2f} (Reward: {reward1:.2f} points, R/R: {rr1}:1)
Target 2: {target2:.2f} (Reward: {reward2:.2f} points, R/R: {rr2}:1)

📈 TECHNICAL INDICATORS
RSI: {rsi:.1f}
ATR: {atr:.1f} points
Volume: {volume_ratio:.2f}x average

🌍 MARKET CONTEXT
Market Sentiment: {sentiment.get('fear_greed_text', 'Unknown')} (Index: {sentiment.get('fear_greed_index', 'N/A')})
SPY Trend: {market.get('spy_trend', 'Unknown')} ({market.get('spy_change_pct', 0):+.2f}%)
Volatility: {market.get('volatility_estimate', 'Unknown')}
Time of Day: {time_info.get('current_time', 'Unknown')} - {time_info.get('session', 'Unknown')} ({time_info.get('time_quality', 'Unknown')})
Economic Calendar: {econ_str}

📰 NEWS & GEOPOLITIS
{news_summary}

PROVIDE YOUR ANALYSIS IN THIS EXACT JSON FORMAT:
{{
  "score": <0-100, overall trade quality>,
  "recommendation": "<YES|NO|MAYBE>",
  "risk_level": "<LOW|MEDIUM|HIGH>",
  "entry_zone": "<precise entry area>",
  "duration_expectation": "<Scalp (min)|Session (hrs)|Swing (days)>",
  "reasoning": [
    "<key point 1>",
    "<key point 2>",
    "<key point 3>"
  ],
  "position_size": "<0.5x|1x|1.5x|2x>",
  "confidence": <0.0-1.0>,
  "key_risks": [
    "<risk 1>",
    "<risk 2>"
  ],
  "exit_strategy": "<brief exit plan>"
}}

ANALYSIS GUIDELINES:
1. Score 80+ = Excellent setup, all factors align
2. Score 60-79 = Good setup, some concerns
3. Score <60 = Poor setup, skip or reduce size
4. CRITICAL: Check News/Geopolitics. If there is WAR or HIGH IMPACT NEWS, reduce score drastically.
5. Check Economic Calendar. Do NOT trade ahead of Fed/CPI events.
6. SESSION MATTERS:
   - London/US Open: Trend trades allowed.
   - Asian Session: Prefer Scalps/Mean Reversion.
   - Lunch/Overnight: Strict filtering.
7. Be conservative - it's better to skip than force a bad trade
8. Focus on risk management and capital preservation

Provide ONLY the JSON response, no additional text."""

        return prompt
    
    @staticmethod
    def get_quick_analysis_prompt(signal_data: dict) -> str:
        """
        Simplified prompt for quick analysis without full context
        Used as fallback when context APIs fail
        """
        
        direction = signal_data.get('direction', 'N/A')
        entry = signal_data.get('entry', 0)
        stop = signal_data.get('stop', 0)
        target1 = signal_data.get('target1', 0)
        rsi = signal_data.get('rsi', 0)
        
        if direction == "LONG":
            risk = entry - stop
            reward = target1 - entry
        else:
            risk = stop - entry
            reward = entry - target1
        
        rr = round(reward / risk, 2) if risk > 0 else 0
        
        prompt = f"""Quick NQ {direction} setup analysis:
Entry: {entry}, Stop: {stop}, Target: {target1}
R/R: {rr}:1, RSI: {rsi}

Respond in JSON:
{{
  "score": <0-100>,
  "recommendation": "<YES|NO|MAYBE>",
  "risk_level": "<LOW|MEDIUM|HIGH>",
  "reasoning": ["<brief reason>"],
  "position_size": "<0.5x|1x|1.5x|2x>",
  "confidence": <0.0-1.0>
}}"""
        
        return prompt
    
    @staticmethod
    def get_market_summary_prompt(context_data: dict) -> str:
        """Generate prompt for overall market summary"""
        
        sentiment = context_data.get('sentiment', {})
        market = context_data.get('market_conditions', {})
        
        prompt = f"""Provide a brief market summary (2-3 sentences):

Sentiment: {sentiment.get('fear_greed_text', 'Unknown')}
SPY: {market.get('spy_trend', 'Unknown')} ({market.get('spy_change_pct', 0):+.2f}%)

What's the overall market environment for NQ trading today?"""
        
        return prompt
