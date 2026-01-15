# 🚀 QUICK NGROK SETUP GUIDE

## ✅ Your Server is Running!

Your FastAPI server is already running on port 8000! ✅

---

## 📥 DOWNLOAD NGROK (Manual - 2 minutes)

### Option 1: Direct Download (Easiest)

1. **Go to:** https://ngrok.com/download
2. **Click:** "Download for Windows" (ZIP file)
3. **Extract** the ZIP file
4. **You'll get:** `ngrok.exe`
5. **Move it to:** `d:\Google\.gemini\antigravity\scratch\NQ-AI-Alerts\`

### Option 2: Already Downloaded?

If ngrok is already installed, find `ngrok.exe` and copy it to your project folder.

---

## 🚀 RUN NGROK (30 seconds)

Once you have `ngrok.exe` in your folder:

### Step 1: Open a NEW PowerShell window

```powershell
cd d:\Google\.gemini\antigravity\scratch\NQ-AI-Alerts
```

### Step 2: Run ngrok

```powershell
.\ngrok.exe http 8000
```

### Step 3: Copy the URL

You'll see something like:
```
Forwarding  https://abc123.ngrok.io -> http://localhost:8000
```

**Copy that HTTPS URL!** (e.g., `https://abc123.ngrok.io`)

---

## 🧪 TEST IT (30 seconds)

### Step 1: Test in browser

Open: `https://your-ngrok-url.ngrok.io/test`

### Step 2: Check Telegram

You should get a test message! ✅

---

## 📊 CONFIGURE TRADINGVIEW (2 minutes)

### Step 1: Open TradingView

1. Go to your NQ futures chart
2. Add the Pine Script from `tradingview/nq_strategy.pine`

### Step 2: Create Alert

1. Click "Create Alert"
2. **Condition:** Your strategy
3. **Webhook URL:** `https://your-ngrok-url.ngrok.io/webhook/tradingview`
4. **Message:** Copy the JSON from the Pine Script
5. **Save**

---

## 🎉 DONE!

You'll now get NQ alerts on your Telegram!

---

## ⚠️ IMPORTANT NOTES

### Free ngrok Limitations:
- URL changes every time you restart ngrok
- Need to update TradingView webhook when URL changes
- For permanent URL, upgrade to ngrok paid ($8/month) or use Render.com

### Keep Running:
- Keep the PowerShell window with ngrok open
- Keep the server running
- Don't close either window!

---

## 🔄 ALTERNATIVE: Use Render.com

For a permanent solution that doesn't require keeping your computer on:
- Follow `DEPLOY_TO_RENDER.md`
- Get permanent URL
- No need to run anything locally

---

## 📞 NEED HELP?

If you get stuck:
1. Make sure server is running (check PowerShell)
2. Make sure ngrok is running (check PowerShell)
3. Test the `/test` endpoint first
4. Check Telegram for messages

---

**You're almost there!** Just download ngrok and run it! 🚀
