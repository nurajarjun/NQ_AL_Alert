# 🚀 AI-Enhanced NQ Alert System - Setup Guide

## 🎉 What's New in v2.0

Your NQ Alert System now has **AI superpowers**! Every alert is now:
- ✅ **AI-Analyzed** - Gemini/GPT evaluates each setup
- ✅ **Context-Aware** - Considers news, sentiment, market conditions
- ✅ **Smart Filtered** - Only sends high-quality setups (score ≥60)
- ✅ **Risk-Scored** - Clear LOW/MEDIUM/HIGH risk levels
- ✅ **Position-Sized** - AI suggests 0.5x, 1x, 1.5x, or 2x sizing

---

## 📋 Prerequisites

1. **Python 3.11+** installed
2. **Telegram Bot** (already configured ✅)
3. **API Keys** (see below)

---

## 🔑 Step 1: Get Your API Keys

### Required: AI Analysis (Choose ONE)

#### Option A: Google Gemini (Recommended - FREE!)
1. Go to: https://makersuite.google.com/app/apikey
2. Click "Create API Key"
3. Copy your key
4. **Cost:** FREE (15 requests/min, perfect for trading alerts)

#### Option B: OpenAI (Paid)
1. Go to: https://platform.openai.com/api-keys
2. Create new secret key
3. Add $5-10 credit
4. **Cost:** ~$0.001 per alert (~$3/month for 100 alerts/day)

### Optional: Market Data (Enhances AI analysis)

#### Alpha Vantage (Market Data)
1. Go to: https://www.alphavantage.co/support/#api-key
2. Get free API key
3. **Free tier:** 25 requests/day (enough for context)

#### NewsAPI (Financial News)
1. Go to: https://newsapi.org/register
2. Get free API key
3. **Free tier:** 100 requests/day

---

## ⚙️ Step 2: Configure Environment Variables

1. **Navigate to backend folder:**
   ```bash
   cd d:\Google\.gemini\antigravity\scratch\NQ-AI-Alerts\backend
   ```

2. **Copy the example file:**
   ```bash
   copy .env.example .env
   ```

3. **Edit `.env` file** with your keys:
   ```env
   # Telegram (Already configured ✅)
   TELEGRAM_BOT_TOKEN=YOUR_BOT_TOKEN_HERE
   TELEGRAM_CHAT_ID=YOUR_CHAT_ID_HERE

   # AI - Add your Gemini key here
   GOOGLE_API_KEY=your_actual_gemini_key_here

   # Market Data (Optional)
   ALPHA_VANTAGE_KEY=your_key_here
   NEWS_API_KEY=your_key_here
   ```

---

## 📦 Step 3: Install Dependencies

```bash
cd d:\Google\.gemini\antigravity\scratch\NQ-AI-Alerts\backend
pip install -r requirements.txt
```

This installs:
- FastAPI (web framework)
- Telegram Bot SDK
- Google Generative AI (Gemini)
- OpenAI (optional)
- aiohttp (async HTTP)
- All other dependencies

---

## 🧪 Step 4: Test the AI System

### Test 1: Basic Server Test
```bash
python main.py
```

You should see:
```
INFO:     Telegram bot initialized successfully
INFO:     AI components initialized
INFO:     Using Google Gemini for AI analysis
INFO:     Application startup complete.
```

### Test 2: Send Test Alert
Open another terminal and run:
```bash
curl -X POST http://localhost:8000/test
```

You should receive a test message on Telegram!

### Test 3: Test AI Analysis
Create a file `test_ai_alert.py`:
```python
import requests
import json

# Sample NQ LONG setup
alert_data = {
    "direction": "LONG",
    "entry": 16850.5,
    "stop": 16820.0,
    "target1": 16920.0,
    "target2": 16980.0,
    "rsi": 58.5,
    "atr": 45.2,
    "volume_ratio": 1.4
}

response = requests.post(
    "http://localhost:8000/webhook/tradingview",
    json=alert_data
)

print(json.dumps(response.json(), indent=2))
```

Run it:
```bash
python test_ai_alert.py
```

Check your Telegram - you should receive an **AI-analyzed alert**! 🎉

---

## 🌐 Step 5: Deploy to Cloud (Render.com)

### Why Deploy?
- TradingView webhooks need a public URL
- Your system runs 24/7
- Free tier available

### Deployment Steps:

1. **Update root requirements.txt:**
   ```bash
   cd d:\Google\.gemini\antigravity\scratch\NQ-AI-Alerts
   copy backend\requirements.txt requirements.txt
   ```

2. **Push to GitHub:**
   ```bash
   git init
   git add .
   git commit -m "AI-enhanced NQ Alert System v2.0"
   git remote add origin your_github_repo_url
   git push -u origin main
   ```

3. **Deploy on Render.com:**
   - Go to https://render.com
   - Click "New +" → "Web Service"
   - Connect your GitHub repo
   - Configure:
     - **Name:** nq-ai-alerts
     - **Environment:** Python 3
     - **Build Command:** `pip install -r requirements.txt`
     - **Start Command:** `uvicorn app:app --host 0.0.0.0 --port $PORT`
   
4. **Add Environment Variables in Render:**
   - `TELEGRAM_BOT_TOKEN`
   - `TELEGRAM_CHAT_ID`
   - `GOOGLE_API_KEY`
   - `ALPHA_VANTAGE_KEY` (optional)
   - `NEWS_API_KEY` (optional)

5. **Get your webhook URL:**
   ```
   https://your-app-name.onrender.com/webhook/tradingview
   ```

---

## 📊 Step 6: Configure TradingView

### Create Pine Script Strategy

```pinescript
//@version=5
strategy("NQ AI Alert System", overlay=true)

// Your strategy logic here
// Example: Simple EMA crossover
ema_fast = ta.ema(close, 9)
ema_slow = ta.ema(close, 21)

long_condition = ta.crossover(ema_fast, ema_slow)
short_condition = ta.crossunder(ema_fast, ema_slow)

// Calculate indicators
rsi_value = ta.rsi(close, 14)
atr_value = ta.atr(14)
volume_ratio = volume / ta.sma(volume, 20)

// Entry logic
if long_condition
    stop_loss = close - (atr_value * 2)
    target1 = close + (atr_value * 3)
    target2 = close + (atr_value * 5)
    
    // Send webhook alert
    alert_message = '{"direction":"LONG","entry":' + str.tostring(close) + 
                    ',"stop":' + str.tostring(stop_loss) + 
                    ',"target1":' + str.tostring(target1) + 
                    ',"target2":' + str.tostring(target2) + 
                    ',"rsi":' + str.tostring(rsi_value) + 
                    ',"atr":' + str.tostring(atr_value) + 
                    ',"volume_ratio":' + str.tostring(volume_ratio) + '}'
    
    alert(alert_message, alert.freq_once_per_bar_close)
    strategy.entry("Long", strategy.long)

if short_condition
    stop_loss = close + (atr_value * 2)
    target1 = close - (atr_value * 3)
    target2 = close - (atr_value * 5)
    
    alert_message = '{"direction":"SHORT","entry":' + str.tostring(close) + 
                    ',"stop":' + str.tostring(stop_loss) + 
                    ',"target1":' + str.tostring(target1) + 
                    ',"target2":' + str.tostring(target2) + 
                    ',"rsi":' + str.tostring(rsi_value) + 
                    ',"atr":' + str.tostring(atr_value) + 
                    ',"volume_ratio":' + str.tostring(volume_ratio) + '}'
    
    alert(alert_message, alert.freq_once_per_bar_close)
    strategy.entry("Short", strategy.short)
```

### Set Up Webhook Alert

1. Add strategy to your NQ chart
2. Right-click chart → "Add Alert"
3. **Condition:** Your strategy name
4. **Webhook URL:** `https://your-app.onrender.com/webhook/tradingview`
5. **Message:** `{{strategy.order.alert_message}}`
6. Click "Create"

---

## 🎯 Step 7: Start Receiving AI Alerts!

That's it! Now when your TradingView strategy triggers:

1. **Signal sent** → Your webhook receives it
2. **AI analyzes** → Gemini evaluates the setup
3. **Context gathered** → News, sentiment, market data
4. **Smart filtering** → Only quality setups sent
5. **Enhanced alert** → You receive detailed analysis on Telegram!

---

## 📱 What Your Alerts Look Like Now

### Before (v1.0):
```
🚨 NQ LONG SETUP
Entry: 16850.50
Stop: 16820.00
Target: 16920.00
```

### After (v2.0 with AI):
```
🟢 AI-ANALYZED NQ LONG SETUP

📊 SIGNAL DETAILS
Entry: 16850.50
Stop: 16820.00 (-30.5 pts)
Target 1: 16920.00 (+69.5 pts, 2.3:1)

🤖 AI ANALYSIS
YES - Score: 78/100
Risk Level: MEDIUM
Position Size: 1x
Confidence: 78%

💡 KEY INSIGHTS
• Strong bullish context with tech sector strength
• Good R/R ratio supports the setup
• Time of day favorable for trending moves

📈 MARKET CONTEXT
Sentiment: Neutral (50)
SPY: Bullish (+0.45%)
Time: 10:35 AM ET - Excellent

💼 EXIT STRATEGY
Take 50% at Target 1, trail stop to breakeven
```

---

## 🔧 Troubleshooting

### "AI components initialized" but no AI provider
**Problem:** No API key configured
**Solution:** Add `GOOGLE_API_KEY` or `OPENAI_API_KEY` to `.env`

### "Alert filtered out by AI"
**Problem:** AI score < 60 (low quality setup)
**Solution:** This is working correctly! AI is protecting you from bad trades

### "Error getting market context"
**Problem:** Market data APIs not configured
**Solution:** Add `ALPHA_VANTAGE_KEY` and `NEWS_API_KEY` (optional but recommended)

### Alerts not arriving
**Problem:** Webhook URL incorrect or server not running
**Solution:** 
1. Check server is running: `curl http://localhost:8000/`
2. Test webhook: `curl -X POST http://localhost:8000/test`
3. Verify TradingView webhook URL

---

## 📊 Monitoring Your AI Performance

### Check Alert History
```bash
curl http://localhost:8000/alerts/history
```

### Check Statistics
```bash
curl http://localhost:8000/alerts/stats
```

---

## 🚀 Next Steps

1. ✅ **Get API keys** (Gemini recommended)
2. ✅ **Configure .env file**
3. ✅ **Test locally**
4. ✅ **Deploy to Render**
5. ✅ **Configure TradingView**
6. ✅ **Start receiving AI-powered alerts!**

---

## 💰 Cost Summary

### Free Option (Recommended):
- Telegram: FREE
- Google Gemini: FREE (15 req/min)
- Alpha Vantage: FREE (25 req/day)
- NewsAPI: FREE (100 req/day)
- Render.com: FREE tier available
- **Total: $0/month** 🎉

### Paid Option (Better quality):
- OpenAI GPT-4o-mini: ~$3/month
- Render.com Pro: $7/month
- **Total: ~$10/month**

---

## 📞 Support

If you run into issues:
1. Check the logs: Look for ERROR messages
2. Test each component individually
3. Verify all API keys are correct
4. Make sure dependencies are installed

---

**You're all set! Let's make some profitable trades with AI assistance! 🚀📈**
