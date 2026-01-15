import asyncio
import sys
import os
from pprint import pprint

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

from ai.context import ContextAnalyzer

async def test_context():
    print("Initializing ContextAnalyzer...")
    analyzer = ContextAnalyzer()
    
    print("\nFetching Market Context...")
    context = await analyzer.get_market_context(symbol="NQ")
    
    print("\n✅ Context Keys:", context.keys())
    
    print("\n--- 📅 ECONOMIC EVENTS ---")
    pprint(context.get('economic_events'))
    
    print("\n--- 📰 NEWS (First 3) ---")
    news = context.get('news', [])
    for i, article in enumerate(news[:3]):
        print(f"{i+1}. [{article.get('category', 'N/A')}] {article['title']}")
        
    print("\n--- 🌍 MARKET CONDITIONS ---")
    pprint(context.get('market_conditions'))
    
    print("\n--- 📝 PROMPT PREVIEW ---")
    from ai.prompts import PromptTemplates
    dummy_signal = {'direction': 'LONG', 'entry': 15000, 'stop': 14900, 'target1': 15100, 'rsi': 55}
    prompt = PromptTemplates.get_trade_analysis_prompt(dummy_signal, context)
    print(prompt[:500] + "...\n[TRUNCATED]")

if __name__ == "__main__":
    if sys.platform == 'win32':
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    asyncio.run(test_context())
