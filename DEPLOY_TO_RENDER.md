# Deploying NQ AI Alert System to Render.com

## 📋 Prerequisites
- GitHub account (free)
- Render.com account (free)

---

## 🚀 DEPLOYMENT STEPS

### Step 1: Create GitHub Repository (5 minutes)

1. **Go to GitHub:** https://github.com
2. **Sign in** (or create free account)
3. **Click "New Repository"** (green button)
4. **Repository settings:**
   - Name: `nq-ai-alerts`
   - Description: `AI-powered NQ futures alert system`
   - **Public** (required for free Render)
   - ✅ Add README
   - Click "Create repository"

### Step 2: Upload Your Code to GitHub

**Option A: Using GitHub Web Interface (Easiest)**

1. In your new repository, click **"uploading an existing file"**
2. **Drag and drop these files:**
   - `app.py`
   - `requirements.txt`
   - `Procfile`
   - `runtime.txt`
   - The entire `backend` folder
3. **Commit message:** "Initial commit - NQ AI Alert System"
4. Click **"Commit changes"**

**Option B: Using Git Command Line**

```bash
cd d:\Google\.gemini\antigravity\scratch\NQ-AI-Alerts

# Initialize git
git init

# Add all files
git add .

# Commit
git commit -m "Initial commit - NQ AI Alert System"

# Add remote (replace YOUR_USERNAME with your GitHub username)
git remote add origin https://github.com/YOUR_USERNAME/nq-ai-alerts.git

# Push to GitHub
git branch -M main
git push -u origin main
```

### Step 3: Deploy to Render.com (5 minutes)

1. **Go to Render:** https://render.com
2. **Sign up** with your GitHub account (easiest)
3. **Click "New +"** → **"Web Service"**
4. **Connect your GitHub repository:**
   - Find `nq-ai-alerts`
   - Click "Connect"

5. **Configure the service:**
   - **Name:** `nq-ai-alerts` (or anything you like)
   - **Region:** Choose closest to you
   - **Branch:** `main`
   - **Root Directory:** Leave blank
   - **Runtime:** `Python 3`
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `uvicorn app:app --host 0.0.0.0 --port $PORT`

6. **Environment Variables** (IMPORTANT!):
   Click "Advanced" → "Add Environment Variable"
   
   Add these:
   ```
   TELEGRAM_BOT_TOKEN = YOUR_BOT_TOKEN_HERE
   TELEGRAM_CHAT_ID = 1979620652
   ```

7. **Plan:** Select **"Free"** (0$/month)

8. **Click "Create Web Service"**

### Step 4: Wait for Deployment (2-3 minutes)

Render will:
- Clone your code
- Install dependencies
- Start your server
- Give you a public URL

**Your URL will look like:**
```
https://nq-ai-alerts.onrender.com
```

### Step 5: Test Your Deployment

1. **Copy your Render URL**
2. **Open in browser:** `https://your-app.onrender.com/test`
3. **Check your Telegram** - you should get a test message!

---

## 🎯 CONFIGURE TRADINGVIEW

Now that you have a public URL, you can set up TradingView:

1. **Open TradingView**
2. **Go to your NQ chart**
3. **Add the Pine Script** from `tradingview/nq_strategy.pine`
4. **Create Alert:**
   - Condition: Your strategy
   - Webhook URL: `https://your-app.onrender.com/webhook/tradingview`
   - Message: (The JSON from the Pine Script)

5. **Save Alert**

**Done!** You'll now get NQ alerts on your phone! 📱

---

## ⚠️ IMPORTANT NOTES

### Free Tier Limitations:
- **Sleeps after 15 min of inactivity**
- **First request after sleep takes ~30 seconds** to wake up
- **750 hours/month free** (plenty for alerts)

### To Keep It Always Awake (Optional):
Use a service like **UptimeRobot** (free) to ping your app every 5 minutes.

---

## 🐛 TROUBLESHOOTING

### If deployment fails:
1. Check the logs in Render dashboard
2. Verify all environment variables are set
3. Make sure all files are uploaded to GitHub

### If alerts don't work:
1. Test the `/test` endpoint first
2. Check Render logs for errors
3. Verify webhook URL in TradingView

---

## ✅ SUCCESS CHECKLIST

- [ ] GitHub repository created
- [ ] Code uploaded to GitHub
- [ ] Render.com account created
- [ ] Web service deployed
- [ ] Environment variables set
- [ ] Test endpoint works
- [ ] TradingView configured
- [ ] Receiving alerts on Telegram

---

## 🎉 YOU'RE DONE!

Once deployed, your NQ AI Alert System will:
- Run 24/7 in the cloud
- Receive TradingView webhooks
- Send smart alerts to your Telegram
- Track all your setups

**No need to keep your computer on!** 🚀

---

## 📞 NEED HELP?

If you get stuck at any step, just let me know which step and I'll help you through it!

Good luck! 🍀
