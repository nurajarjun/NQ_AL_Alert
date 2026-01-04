"""
AI Analyzer - Core AI decision engine using OpenAI/Gemini
"""

import os
import json
import logging
from typing import Dict, Optional
import google.generativeai as genai
from openai import AsyncOpenAI

from .prompts import PromptTemplates

logger = logging.getLogger(__name__)


class AIAnalyzer:
    """AI-powered trade analysis using LLMs"""
    
    def __init__(self):
        self.openai_key = os.getenv("OPENAI_API_KEY")
        self.google_key = os.getenv("GOOGLE_API_KEY")
        self.prompts = PromptTemplates()
        
        # Initialize AI client based on available keys
        if self.google_key:
            genai.configure(api_key=self.google_key)
            self.model = genai.GenerativeModel('gemini-1.5-flash')
            self.provider = "gemini"
            logger.info("Using Google Gemini for AI analysis")
        elif self.openai_key:
            self.client = AsyncOpenAI(api_key=self.openai_key)
            self.provider = "openai"
            logger.info("Using OpenAI for AI analysis")
        else:
            self.provider = None
            logger.warning("No AI API key configured - using fallback analysis")
    
    async def analyze_trade(
        self, 
        signal_data: Dict, 
        context_data: Optional[Dict] = None
    ) -> Dict:
        """
        Analyze a trading signal using AI
        
        Args:
            signal_data: Trading signal details
            context_data: Market context (optional)
            
        Returns:
            AI analysis with recommendation, score, reasoning, etc.
        """
        try:
            # Use full analysis if context available, otherwise quick analysis
            if context_data:
                prompt = self.prompts.get_trade_analysis_prompt(signal_data, context_data)
            else:
                prompt = self.prompts.get_quick_analysis_prompt(signal_data)
            
            # Get AI response based on provider
            if self.provider == "gemini":
                analysis = await self._analyze_with_gemini(prompt)
            elif self.provider == "openai":
                analysis = await self._analyze_with_openai(prompt)
            else:
                analysis = self._fallback_analysis(signal_data)
            
            # Validate and enhance analysis
            analysis = self._validate_analysis(analysis, signal_data)
            
            logger.info(f"AI Analysis complete: {analysis['recommendation']} (Score: {analysis['score']})")
            return analysis
            
        except Exception as e:
            logger.error(f"Error in AI analysis: {str(e)}")
            return self._fallback_analysis(signal_data)
    
    async def _analyze_with_gemini(self, prompt: str) -> Dict:
        """Analyze using Google Gemini"""
        try:
            response = self.model.generate_content(prompt)
            response_text = response.text
            
            # Extract JSON from response
            analysis = self._extract_json(response_text)
            return analysis
            
        except Exception as e:
            logger.error(f"Gemini analysis error: {str(e)}")
            raise
    
    async def _analyze_with_openai(self, prompt: str) -> Dict:
        """Analyze using OpenAI"""
        try:
            response = await self.client.chat.completions.create(
                model="gpt-4o-mini",  # Cost-effective model
                messages=[
                    {
                        "role": "system",
                        "content": "You are an expert NQ futures trader. Respond ONLY with valid JSON."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=0.3,  # Lower temperature for more consistent analysis
                max_tokens=500
            )
            
            response_text = response.choices[0].message.content
            analysis = self._extract_json(response_text)
            return analysis
            
        except Exception as e:
            logger.error(f"OpenAI analysis error: {str(e)}")
            raise
    
    def _extract_json(self, text: str) -> Dict:
        """Extract JSON from AI response text"""
        try:
            # Try direct JSON parse
            return json.loads(text)
        except json.JSONDecodeError:
            # Try to find JSON in text (sometimes AI adds explanation)
            import re
            json_match = re.search(r'\{.*\}', text, re.DOTALL)
            if json_match:
                try:
                    return json.loads(json_match.group())
                except json.JSONDecodeError:
                    pass
            
            logger.error(f"Could not extract JSON from response: {text[:200]}")
            raise ValueError("Invalid JSON response from AI")
    
    def _fallback_analysis(self, signal_data: Dict) -> Dict:
        """
        Rule-based fallback analysis when AI is unavailable
        Simple but reliable logic
        """
        direction = signal_data.get('direction', 'N/A')
        entry = signal_data.get('entry', 0)
        stop = signal_data.get('stop', 0)
        target1 = signal_data.get('target1', 0)
        rsi = signal_data.get('rsi', 50)
        volume_ratio = signal_data.get('volume_ratio', 1.0)
        
        # Calculate R/R
        if direction == "LONG":
            risk = entry - stop
            reward = target1 - entry
        else:
            risk = stop - entry
            reward = entry - target1
        
        rr = round(reward / risk, 2) if risk > 0 else 0
        
        # Simple scoring logic
        score = 50  # Base score
        
        # R/R ratio scoring
        if rr >= 2.5:
            score += 20
        elif rr >= 2.0:
            score += 15
        elif rr >= 1.5:
            score += 10
        elif rr < 1.5:
            score -= 20
        
        # RSI scoring
        if direction == "LONG":
            if 40 <= rsi <= 60:
                score += 15
            elif rsi > 70:
                score -= 10  # Overbought
        else:  # SHORT
            if 40 <= rsi <= 60:
                score += 15
            elif rsi < 30:
                score -= 10  # Oversold
        
        # Volume scoring
        if volume_ratio >= 1.5:
            score += 10
        elif volume_ratio >= 1.2:
            score += 5
        elif volume_ratio < 0.8:
            score -= 10
        
        # Determine recommendation
        if score >= 75:
            recommendation = "YES"
            risk_level = "LOW"
            position_size = "1.5x"
        elif score >= 60:
            recommendation = "YES"
            risk_level = "MEDIUM"
            position_size = "1x"
        elif score >= 50:
            recommendation = "MAYBE"
            risk_level = "MEDIUM"
            position_size = "0.5x"
        else:
            recommendation = "NO"
            risk_level = "HIGH"
            position_size = "0x"
        
        return {
            "score": max(0, min(100, score)),
            "recommendation": recommendation,
            "risk_level": risk_level,
            "reasoning": [
                f"R/R ratio: {rr}:1",
                f"RSI: {rsi:.1f}",
                f"Volume: {volume_ratio:.2f}x average",
                "⚠️ AI unavailable - using rule-based analysis"
            ],
            "position_size": position_size,
            "confidence": 0.6,  # Lower confidence for fallback
            "key_risks": [
                "AI analysis unavailable",
                "Limited context awareness"
            ],
            "exit_strategy": f"Target 1 at {target1:.2f}, trail stop after +1R",
            "provider": "fallback"
        }
    
    def _validate_analysis(self, analysis: Dict, signal_data: Dict) -> Dict:
        """Validate and ensure analysis has all required fields"""
        
        # Required fields with defaults
        defaults = {
            "score": 50,
            "recommendation": "MAYBE",
            "risk_level": "MEDIUM",
            "reasoning": ["Analysis incomplete"],
            "position_size": "0.5x",
            "confidence": 0.5,
            "key_risks": ["Unknown"],
            "exit_strategy": "Standard exit",
            "provider": self.provider or "fallback"
        }
        
        # Merge with defaults
        for key, default_value in defaults.items():
            if key not in analysis or not analysis[key]:
                analysis[key] = default_value
        
        # Validate score range
        analysis['score'] = max(0, min(100, analysis['score']))
        
        # Validate confidence range
        if isinstance(analysis['confidence'], (int, float)):
            analysis['confidence'] = max(0.0, min(1.0, float(analysis['confidence'])))
        else:
            analysis['confidence'] = 0.5
        
        # Ensure reasoning is a list
        if isinstance(analysis['reasoning'], str):
            analysis['reasoning'] = [analysis['reasoning']]
        
        # Ensure key_risks is a list
        if 'key_risks' in analysis and isinstance(analysis['key_risks'], str):
            analysis['key_risks'] = [analysis['key_risks']]
        
        return analysis
    
    def should_send_alert(self, analysis: Dict) -> bool:
        """
        Determine if alert should be sent based on AI analysis
        
        Args:
            analysis: AI analysis result
            
        Returns:
            True if alert should be sent, False otherwise
        """
        score = analysis.get('score', 0)
        recommendation = analysis.get('recommendation', 'NO')
        
        # Send if score >= 60 OR recommendation is YES/MAYBE
        if score >= 60:
            return True
        
        if recommendation in ['YES', 'MAYBE']:
            return True
        
        return False
    
    def get_alert_emoji(self, analysis: Dict) -> str:
        """Get appropriate emoji based on analysis quality"""
        score = analysis.get('score', 0)
        
        if score >= 80:
            return "🟢"  # Green - Excellent
        elif score >= 70:
            return "🔵"  # Blue - Very Good
        elif score >= 60:
            return "🟡"  # Yellow - Good
        elif score >= 50:
            return "🟠"  # Orange - Caution
        else:
            return "🔴"  # Red - Poor
