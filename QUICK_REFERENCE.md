# 🎯 NQ AI Alert System - Quick Reference

## 📱 Understanding Your AI Alerts

### Alert Quality Indicators

| Emoji | Score | Meaning | Action |
|-------|-------|---------|--------|
| 🟢 | 80-100 | Excellent setup | Take with full size (1.5x) |
| 🔵 | 70-79 | Very good setup | Take with standard size (1x) |
| 🟡 | 60-69 | Good setup | Take with reduced size (0.5x) |
| 🟠 | 50-59 | Caution | Consider skipping |
| 🔴 | 0-49 | Poor setup | Skip (won't be sent) |

### AI Recommendations

- **YES** - High confidence, take the trade
- **MAYBE** - Moderate confidence, reduce size or skip
- **NO** - Low confidence, skip (alert filtered out)

### Risk Levels

- **LOW** - Favorable conditions, minimal concerns
- **MEDIUM** - Some risks present, standard caution
- **HIGH** - Significant risks, reduce size or skip

---

## 🔧 Common Commands

### Local Testing
```bash
# Start server
cd backend
python main.py

# Test AI system
python test_ai_system.py

# Send test alert
curl -X POST http://localhost:8000/test

# Check alert history
curl http://localhost:8000/alerts/history

# Check statistics
curl http://localhost:8000/alerts/stats
```

### Simulate TradingView Alert
```bash
curl -X POST http://localhost:8000/webhook/tradingview \
  -H "Content-Type: application/json" \
  -d '{
    "direction": "LONG",
    "entry": 16850.5,
    "stop": 16820.0,
    "target1": 16920.0,
    "target2": 16980.0,
    "rsi": 58.5,
    "atr": 45.2,
    "volume_ratio": 1.4
  }'
```

---

## 📊 Reading Your Alerts

### Sample Alert Breakdown

```
🟢 AI-ANALYZED NQ LONG SETUP
    ↑ Quality indicator (Green = Excellent)

📊 SIGNAL DETAILS
Entry: 16850.50          ← Your entry price
Stop: 16820.00 (-30.5 pts)  ← Stop loss (risk)
Target 1: 16920.00 (+69.5 pts, 2.3:1)  ← First target (R/R ratio)

🤖 AI ANALYSIS
YES - Score: 78/100      ← AI recommendation & quality score
Risk Level: MEDIUM       ← Risk assessment
Position Size: 1x        ← Suggested position size
Confidence: 78%          ← AI confidence level

💡 KEY INSIGHTS
• Strong bullish context   ← AI reasoning
• Good R/R ratio
• Prime trading hour

📈 MARKET CONTEXT
Sentiment: Neutral (52)   ← Fear & Greed Index
SPY: Bullish (+0.45%)    ← Market trend
Time: 10:35 AM ET - Excellent  ← Time quality

💼 EXIT STRATEGY
Take 50% at Target 1...   ← AI exit recommendation
```

---

## 🎯 Position Sizing Guide

| AI Suggestion | Your Account | Position Size |
|---------------|--------------|---------------|
| 0.5x | $10,000 | 0.5 contracts |
| 1x | $10,000 | 1 contract |
| 1.5x | $10,000 | 1.5 contracts |
| 2x | $10,000 | 2 contracts |

**Adjust based on your risk tolerance and account size**

---

## ⚙️ Configuration Quick Reference

### Required API Keys

1. **Telegram** (Required)
   - Bot Token: Already configured ✅
   - Chat ID: Already configured ✅

2. **AI Provider** (Choose ONE)
   - **Gemini** (FREE): https://makersuite.google.com/app/apikey
   - **OpenAI** (Paid): https://platform.openai.com/api-keys

3. **Market Data** (Optional)
   - **Alpha Vantage**: https://www.alphavantage.co/support/#api-key
   - **NewsAPI**: https://newsapi.org/register

### .env File Template
```env
TELEGRAM_BOT_TOKEN=YOUR_BOT_TOKEN_HERE
TELEGRAM_CHAT_ID=YOUR_CHAT_ID_HERE
GOOGLE_API_KEY=your_gemini_key_here
ALPHA_VANTAGE_KEY=your_key_here
NEWS_API_KEY=your_key_here
```

---

## 🚨 Troubleshooting

### Alert Not Received
1. Check server is running: `curl http://localhost:8000/`
2. Check logs for errors
3. Verify Telegram credentials
4. Test with: `curl -X POST http://localhost:8000/test`

### "Alert Filtered Out"
- **This is normal!** AI rejected a low-quality setup
- Check logs to see the score
- Only alerts with score ≥60 are sent

### AI Not Working
1. Check API key in `.env` file
2. Verify internet connection
3. Check API quota/limits
4. Look for "Using fallback analysis" in logs

### Slow Responses
- First request may be slow (cold start)
- Subsequent requests faster
- Normal latency: 2-5 seconds

---

## 📈 Best Practices

### Trading with AI Alerts

1. **Trust the Score**
   - 80+ = High confidence, full size
   - 60-79 = Good setup, standard size
   - <60 = Skip (won't receive anyway)

2. **Consider Risk Level**
   - LOW = Favorable conditions
   - MEDIUM = Standard caution
   - HIGH = Reduce size or skip

3. **Read the Insights**
   - AI explains its reasoning
   - Look for red flags
   - Consider market context

4. **Use Position Sizing**
   - Follow AI suggestions
   - Adjust for your account size
   - Never risk more than 1-2% per trade

5. **Track Performance**
   - Monitor AI accuracy over time
   - Note which setups work best
   - Adjust your strategy accordingly

---

## 🔄 Maintenance

### Daily
- Check server status
- Review alert history
- Monitor AI performance

### Weekly
- Review statistics
- Check API usage/quotas
- Update market data sources

### Monthly
- Analyze AI accuracy
- Optimize parameters
- Review and improve

---

## 📞 Quick Links

- **Setup Guide**: [AI_SETUP_GUIDE.md](AI_SETUP_GUIDE.md)
- **Enhancement Plan**: [AI_ENHANCEMENT_PLAN.md](AI_ENHANCEMENT_PLAN.md)
- **Implementation Summary**: [IMPLEMENTATION_SUMMARY.md](IMPLEMENTATION_SUMMARY.md)
- **Full README**: [README.md](README.md)

---

## 💡 Pro Tips

1. **Start Conservative**
   - Use 0.5x sizing initially
   - Build confidence in AI recommendations
   - Track results for 2 weeks

2. **Combine with Your Analysis**
   - AI is a tool, not a replacement
   - Use your judgment
   - Consider your trading plan

3. **Monitor Market Conditions**
   - Pay attention to time quality
   - Avoid trading during news events
   - Respect market sentiment

4. **Keep Learning**
   - Review AI reasoning
   - Understand why trades work/fail
   - Improve your strategy

---

**Remember: AI enhances your trading, but you're still the decision-maker!** 🎯
