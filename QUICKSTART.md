# Quick Start Guide - NQ AI Alert System

## 🚀 GET STARTED IN 30 MINUTES

This guide will get you up and running with basic alerts today!

---

## ✅ PREREQUISITES

- [ ] TradingView Premium account (you have this ✅)
- [ ] Python 3.10+ installed
- [ ] Telegram account (for alerts)
- [ ] Basic Python knowledge

---

## 📱 STEP 1: CREATE TELEGRAM BOT (5 minutes)

### 1.1 Open Telegram and find BotFather
- Search for `@BotFather` in Telegram
- Start a chat

### 1.2 Create your bot
```
/newbot
```
- Choose a name: `NQ AI Alerts`
- Choose a username: `your_nq_alerts_bot` (must be unique)
- **Save the API token** - you'll need this!

### 1.3 Get your Chat ID
- Search for `@userinfobot` in Telegram
- Start a chat
- **Save your Chat ID** - you'll need this!

---

## 💻 STEP 2: SET UP PROJECT (10 minutes)

### 2.1 Create project folder
```bash
cd d:\Google\.gemini\antigravity\scratch\NQ-AI-Alerts
mkdir backend
cd backend
```

### 2.2 Create virtual environment
```bash
python -m venv venv
venv\Scripts\activate  # On Windows
# source venv/bin/activate  # On Mac/Linux
```

### 2.3 Install dependencies
```bash
pip install fastapi uvicorn python-telegram-bot python-dotenv requests aiohttp
```

### 2.4 Create .env file
Create a file named `.env`:
```env
TELEGRAM_BOT_TOKEN=your_bot_token_here
TELEGRAM_CHAT_ID=your_chat_id_here
OPENAI_API_KEY=your_openai_key_here  # Optional for now
```

---

## 🔧 STEP 3: CREATE BASIC ALERT SERVER (10 minutes)

### 3.1 Create `main.py`

```python
from fastapi import FastAPI, Request
from telegram import Bot
import os
from dotenv import load_dotenv
import asyncio

load_dotenv()

app = FastAPI()
bot = Bot(token=os.getenv("TELEGRAM_BOT_TOKEN"))
chat_id = os.getenv("TELEGRAM_CHAT_ID")

@app.post("/webhook/tradingview")
async def receive_alert(request: Request):
    """Receive alerts from TradingView"""
    try:
        data = await request.json()
        
        # Format alert message
        message = f"""
🚨 NQ ALERT

Direction: {data.get('direction', 'N/A')}
Entry: {data.get('entry', 'N/A')}
Stop Loss: {data.get('stop', 'N/A')}
Target 1: {data.get('target1', 'N/A')}
Target 2: {data.get('target2', 'N/A')}

RSI: {data.get('rsi', 'N/A')}
ATR: {data.get('atr', 'N/A')}
        """
        
        # Send to Telegram
        await bot.send_message(chat_id=chat_id, text=message)
        
        return {"status": "success", "message": "Alert sent"}
    
    except Exception as e:
        return {"status": "error", "message": str(e)}

@app.get("/")
async def root():
    return {"message": "NQ AI Alert System is running!"}

@app.get("/test")
async def test_alert():
    """Test endpoint to verify Telegram works"""
    try:
        await bot.send_message(
            chat_id=chat_id, 
            text="✅ Test alert - System is working!"
        )
        return {"status": "success"}
    except Exception as e:
        return {"status": "error", "message": str(e)}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
```

### 3.2 Test the server

```bash
python main.py
```

Open browser: `http://localhost:8000/test`

**You should receive a test message on Telegram!** ✅

---

## 📊 STEP 4: SET UP TRADINGVIEW (5 minutes)

### 4.1 Make your server publicly accessible

**Option A: Use ngrok (easiest for testing)**
```bash
# Download ngrok from ngrok.com
ngrok http 8000
```
Copy the HTTPS URL (e.g., `https://abc123.ngrok.io`)

**Option B: Deploy to Render.com (for production)**
- Create account on render.com
- Deploy your FastAPI app
- Get your public URL

### 4.2 Configure TradingView Alert

1. Open TradingView
2. Go to NQ futures chart
3. Add the Pine Script from README.md
4. Create an alert:
   - **Condition:** Your strategy
   - **Alert name:** NQ AI Alert
   - **Webhook URL:** `https://your-url.ngrok.io/webhook/tradingview`
   - **Message:** (Use the JSON from Pine Script)

### 4.3 Test the alert

Trigger an alert manually in TradingView.

**You should receive an alert on Telegram!** 🎉

---

## 🎯 YOU'RE DONE!

You now have:
- ✅ Basic alert system running
- ✅ TradingView → Server → Telegram flow working
- ✅ Foundation to build on

---

## 🚀 NEXT STEPS

### Enhance Your Alerts (Week 2)

Add AI context to your alerts:

```python
import openai
import os

openai.api_key = os.getenv("OPENAI_API_KEY")

async def get_ai_context(direction, entry):
    """Get AI analysis of the setup"""
    
    prompt = f"""
    Analyze this NQ futures trading setup:
    Direction: {direction}
    Entry: {entry}
    
    Provide:
    1. Current market sentiment for tech/Nasdaq
    2. Any relevant news in the last 2 hours
    3. Risk assessment (1-10)
    4. Brief insight (2 sentences)
    
    Be concise and actionable.
    """
    
    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[{"role": "user", "content": prompt}],
        max_tokens=200
    )
    
    return response.choices[0].message.content

# In your webhook handler:
@app.post("/webhook/tradingview")
async def receive_alert(request: Request):
    data = await request.json()
    
    # Get AI context
    ai_context = await get_ai_context(
        data.get('direction'), 
        data.get('entry')
    )
    
    message = f"""
🚨 NQ {data.get('direction')} ALERT

Entry: {data.get('entry')}
Stop: {data.get('stop')}
Target 1: {data.get('target1')}
Target 2: {data.get('target2')}

🧠 AI ANALYSIS:
{ai_context}
    """
    
    await bot.send_message(chat_id=chat_id, text=message)
    return {"status": "success"}
```

### Add News Sentiment (Week 3)

```python
import requests

def get_news_sentiment():
    """Fetch recent news about Nasdaq/tech"""
    
    # Using NewsAPI (free tier)
    api_key = os.getenv("NEWS_API_KEY")
    url = f"https://newsapi.org/v2/everything?q=nasdaq OR technology&apiKey={api_key}&pageSize=5&sortBy=publishedAt"
    
    response = requests.get(url)
    articles = response.json().get('articles', [])
    
    # Simple sentiment (you can enhance this)
    headlines = [a['title'] for a in articles[:3]]
    
    return headlines
```

### Add Pattern Recognition (Week 4)

Train a simple ML model to recognize patterns and add win probability to your alerts.

---

## 📚 FOLDER STRUCTURE

```
NQ-AI-Alerts/
├── README.md
├── QUICKSTART.md (this file)
├── backend/
│   ├── main.py
│   ├── .env
│   ├── requirements.txt
│   └── venv/
├── tradingview/
│   └── nq_strategy.pine
└── docs/
    └── setup_guide.md
```

---

## 🐛 TROUBLESHOOTING

### Telegram bot not sending messages
- Check your bot token is correct
- Check your chat ID is correct
- Make sure you've started a chat with your bot

### TradingView webhook not working
- Verify your webhook URL is correct
- Check ngrok is running
- Test with `/test` endpoint first
- Check server logs for errors

### Server not starting
- Check Python version (3.10+)
- Verify all dependencies installed
- Check port 8000 is not in use

---

## 💡 TIPS

1. **Start Simple:** Get basic alerts working first
2. **Test Thoroughly:** Use `/test` endpoint frequently
3. **Monitor Logs:** Watch server output for errors
4. **Iterate:** Add features one at a time
5. **Paper Trade:** Test alerts before using real money

---

## 📞 WHAT'S NEXT?

Once basic alerts are working:

**Week 2:** Add AI context (news, sentiment)
**Week 3:** Add ML pattern recognition
**Week 4:** Build dashboard for monitoring

---

## 🎯 SUCCESS!

If you've completed this guide, you now have:
- ✅ Working alert system
- ✅ TradingView integration
- ✅ Telegram notifications
- ✅ Foundation for AI enhancements

**Ready to add AI features?** Let me know and I'll help you build the next layer! 🚀
