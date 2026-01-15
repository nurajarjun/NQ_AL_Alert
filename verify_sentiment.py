from backend.ai.context import ContextAnalyzer
import logging

# Setup logging
logging.basicConfig(level=logging.INFO)

analyzer = ContextAnalyzer()

print("🧪 Testing VADER Sentiment Analysis...")

headlines = [
    "NQ futures rally on strong tech earnings",
    "Market crashes as fear grows over inflation",
    "Fed keeps rates unchanged, signaling stability",
    "Not bad at all, earnings were okay" # Tricky one for simple keywords!
]

for h in headlines:
    sentiment = analyzer._analyze_headline_sentiment(h)
    print(f"Headline: '{h}'")
    print(f"Sentiment: {sentiment}")
    print("-" * 30)

print("\n✅ VADER Verification Complete")
