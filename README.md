# NQ AI Alert System 🚀

**AI-powered real-time alerts for NQ (Nasdaq-100 E-mini) futures trading**

## ✨ Version 2.0 - Now with AI Intelligence!

Every alert is now analyzed by artificial intelligence before reaching you. Get smarter, filtered, context-aware trading signals.

## 🤖 AI Features

- **🧠 Intelligent Analysis** - Google Gemini/OpenAI evaluates every setup
- **📊 Quality Scoring** - 0-100 score for each trade setup
- **🎯 Smart Filtering** - Only sends high-quality alerts (score ≥60)
- **📰 Context-Aware** - Considers news, sentiment, market conditions
- **⚖️ Risk Assessment** - Clear LOW/MEDIUM/HIGH risk levels
- **💼 Position Sizing** - AI suggests 0.5x, 1x, 1.5x, or 2x sizing
- **💡 Key Insights** - Explains reasoning behind each recommendation

## Features

- 📊 **Smart Alerts** - AI-analyzed trading setups with quality scores
- 📱 **Telegram Notifications** - Instant enhanced alerts on your phone
- 🎯 **Risk Management** - AI-calculated risk levels and position sizing
- 📈 **TradingView Integration** - Seamless webhook support
- 🌍 **Market Context** - News, sentiment, and market condition analysis
- ☁️ **Cloud-Hosted** - Always-on, no local server needed
- 🆓 **Free Tier Available** - Use Google Gemini for $0/month

## Quick Start

### Option 1: Full AI Setup (Recommended)
See **[AI_SETUP_GUIDE.md](AI_SETUP_GUIDE.md)** for complete instructions.

### Option 2: Quick Test
1. Get Google Gemini API key (free): https://makersuite.google.com/app/apikey
2. Configure `.env` file with your keys
3. Install: `pip install -r backend/requirements.txt`
4. Test: `python backend/test_ai_system.py`
5. Run: `python backend/main.py`

## Environment Variables

Required in `.env` file:

```env
# Telegram (Required)
TELEGRAM_BOT_TOKEN=your_bot_token_here
TELEGRAM_CHAT_ID=your_chat_id_here

# AI Analysis (Choose one - Gemini recommended)
GOOGLE_API_KEY=your_gemini_key_here
# OR
OPENAI_API_KEY=your_openai_key_here

# Market Data (Optional but recommended)
ALPHA_VANTAGE_KEY=your_key_here
NEWS_API_KEY=your_key_here
```

## API Endpoints

- `GET /` - Health check
- `GET /test` - Send test alert to Telegram
- `POST /webhook/tradingview` - Receive TradingView alerts
- `GET /alerts/history` - View alert history
- `GET /alerts/stats` - View statistics

## Tech Stack

- **Backend:** FastAPI (Python)
- **Notifications:** Telegram Bot API
- **Deployment:** Render.com
- **Signals:** TradingView Premium

## License

Private - For personal use only

## Support

For issues or questions, check the documentation in the repo.
