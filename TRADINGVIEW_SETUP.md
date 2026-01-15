# 🔗 TRADINGVIEW CONNECTION GUIDE

## ❌ IMPORTANT: I Cannot Connect Directly

**I cannot:**
- Access your TradingView account
- Create strategies in your account
- Set up webhooks for you

**You must:**
- Set up the connection yourself
- Create the Pine Script strategy
- Configure the webhook

---

## ✅ HOW TO CONNECT TRADINGVIEW

### **Step 1: Deploy Your Backend (Required!)**

**Current Status:** Running locally on `localhost:8000`

**Problem:** TradingView can't reach localhost!

**Solution:** Deploy to cloud (FREE options):

#### **Option A: Render.com (Recommended - FREE)**
1. Create account at render.com
2. Connect your GitHub repo
3. Deploy as Web Service
4. Get public URL: `https://your-app.onrender.com`

#### **Option B: Railway.app (FREE)**
1. Create account at railway.app
2. Deploy from GitHub
3. Get public URL: `https://your-app.railway.app`

#### **Option C: ngrok (Quick Test - FREE)**
1. Download ngrok
2. Run: `ngrok http 8000`
3. Get temporary URL: `https://abc123.ngrok.io`
4. **Note:** URL changes each time!

---

### **Step 2: Create Pine Script Strategy**

**I'll create the strategy for you!** (See below)

---

### **Step 3: Add Webhook to TradingView**

1. Open your strategy in TradingView
2. Click "Add Alert"
3. Set conditions
4. In "Webhook URL" field, paste:
   ```
   https://your-server.com/webhook/tradingview
   ```
5. In "Message" field, paste:
   ```json
   {
     "symbol": "{{ticker}}",
     "direction": "LONG",
     "entry": {{close}},
     "stop": {{low}},
     "target1": {{high}},
     "target2": {{high}} + 60,
     "rsi": {{rsi}},
     "atr": {{atr}},
     "volume_ratio": {{volume}} / {{sma(volume, 20)}}
   }
   ```

---

## 📊 PINE SCRIPT STRATEGY

Here's a complete strategy I created for you:

```pinescript
//@version=5
strategy("NQ AI Alert System", overlay=true)

// ===== INPUTS =====
rsiLength = input.int(14, "RSI Length")
rsiOverbought = input.int(70, "RSI Overbought")
rsiOversold = input.int(30, "RSI Oversold")
atrLength = input.int(14, "ATR Length")
atrMultiplier = input.float(2.0, "ATR Multiplier for Stops")

// Webhook URL (replace with your deployed URL)
webhookUrl = input.string("https://your-server.com/webhook/tradingview", "Webhook URL")

// ===== INDICATORS =====
rsi = ta.rsi(close, rsiLength)
atr = ta.atr(atrLength)
volumeRatio = volume / ta.sma(volume, 20)

// Moving averages
ema20 = ta.ema(close, 20)
ema50 = ta.ema(close, 50)

// ===== LONG CONDITIONS =====
longCondition = ta.crossover(ema20, ema50) and rsi < rsiOverbought and close > ema20

if longCondition
    // Calculate levels
    entryPrice = close
    stopPrice = entryPrice - (atr * atrMultiplier)
    target1Price = entryPrice + (atr * atrMultiplier * 2)
    target2Price = entryPrice + (atr * atrMultiplier * 4)
    
    // Enter trade
    strategy.entry("Long", strategy.long)
    
    // Set stops and targets
    strategy.exit("Exit Long", "Long", stop=stopPrice, limit=target1Price)
    
    // Send webhook alert
    alert('{"symbol":"NQ", "direction":"LONG", "entry":' + str.tostring(entryPrice) + 
          ', "stop":' + str.tostring(stopPrice) + 
          ', "target1":' + str.tostring(target1Price) + 
          ', "target2":' + str.tostring(target2Price) + 
          ', "rsi":' + str.tostring(rsi) + 
          ', "atr":' + str.tostring(atr) + 
          ', "volume_ratio":' + str.tostring(volumeRatio) + '}', 
          alert.freq_once_per_bar_close)

// ===== SHORT CONDITIONS =====
shortCondition = ta.crossunder(ema20, ema50) and rsi > rsiOversold and close < ema20

if shortCondition
    // Calculate levels
    entryPrice = close
    stopPrice = entryPrice + (atr * atrMultiplier)
    target1Price = entryPrice - (atr * atrMultiplier * 2)
    target2Price = entryPrice - (atr * atrMultiplier * 4)
    
    // Enter trade
    strategy.entry("Short", strategy.short)
    
    // Set stops and targets
    strategy.exit("Exit Short", "Short", stop=stopPrice, limit=target1Price)
    
    // Send webhook alert
    alert('{"symbol":"NQ", "direction":"SHORT", "entry":' + str.tostring(entryPrice) + 
          ', "stop":' + str.tostring(stopPrice) + 
          ', "target1":' + str.tostring(target1Price) + 
          ', "target2":' + str.tostring(target2Price) + 
          ', "rsi":' + str.tostring(rsi) + 
          ', "atr":' + str.tostring(atr) + 
          ', "volume_ratio":' + str.tostring(volumeRatio) + '}', 
          alert.freq_once_per_bar_close)

// ===== PLOT =====
plot(ema20, "EMA 20", color=color.blue)
plot(ema50, "EMA 50", color=color.red)
```

---

## 🚀 DEPLOYMENT GUIDE (Render.com - RECOMMENDED)

### **Step 1: Prepare for Deployment**

Create `render.yaml` in your project root:

```yaml
services:
  - type: web
    name: nq-ai-alerts
    env: python
    buildCommand: "pip install -r backend/requirements.txt"
    startCommand: "cd backend && uvicorn main:app --host 0.0.0.0 --port $PORT"
    envVars:
      - key: TELEGRAM_BOT_TOKEN
        sync: false
      - key: TELEGRAM_CHAT_ID
        sync: false
      - key: GOOGLE_API_KEY
        sync: false
```

### **Step 2: Deploy to Render**

1. Go to render.com
2. Sign up (free)
3. Click "New +" → "Web Service"
4. Connect your GitHub repo
5. Configure:
   - Name: `nq-ai-alerts`
   - Environment: `Python 3`
   - Build Command: `pip install -r backend/requirements.txt`
   - Start Command: `cd backend && uvicorn main:app --host 0.0.0.0 --port $PORT`
6. Add environment variables:
   - `TELEGRAM_BOT_TOKEN`
   - `TELEGRAM_CHAT_ID`
   - `GOOGLE_API_KEY`
7. Click "Create Web Service"

### **Step 3: Get Your URL**

After deployment, you'll get:
```
https://nq-ai-alerts.onrender.com
```

Use this in TradingView webhook:
```
https://nq-ai-alerts.onrender.com/webhook/tradingview
```

---

## 🎯 QUICK START (3 Steps)

### **1. Deploy Backend (Choose One):**
- ✅ **Render.com** (Recommended - Always on, FREE)
- ⏰ **ngrok** (Quick test - Temporary URL)
- 🚀 **Railway.app** (Alternative - FREE)

### **2. Copy Pine Script:**
- Copy the strategy above
- Paste in TradingView
- Update webhook URL

### **3. Create Alert:**
- Set alert on strategy
- Add webhook URL
- Done!

---

## ⚠️ IMPORTANT NOTES

### **TradingView Premium Required:**
- Webhooks require TradingView Premium ($60/month)
- You mentioned you have this ✅

### **Deployment is FREE:**
- Render.com: FREE tier (enough for this)
- Railway.app: FREE tier
- ngrok: FREE tier (temporary URLs)

### **Test First:**
- Use ngrok for quick testing
- Deploy to Render for production

---

## 🆘 NEED HELP?

**I can help you with:**
1. ✅ Creating deployment files
2. ✅ Writing Pine Script strategies
3. ✅ Debugging webhook issues
4. ✅ Optimizing the strategy

**You need to do:**
1. ❌ Deploy to cloud (I can't access your accounts)
2. ❌ Add webhook in TradingView (I can't access TradingView)
3. ❌ Create alerts (You must do this)

---

## 🚀 WANT ME TO:

**A)** Create deployment files for Render.com?  
**B)** Create more Pine Script strategies?  
**C)** Help with ngrok setup for quick testing?  
**D)** All of the above?  

**Let me know and I'll help!** 🎯
