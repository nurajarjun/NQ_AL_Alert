# 🔍 DATA SOURCES & ALGORITHMS - Complete Breakdown

## 📊 WHAT DATA IS BEING USED?

### **INPUT DATA (From TradingView)**

When TradingView sends a signal, it includes:

```json
{
  "direction": "LONG",        // Your Pine Script determines this
  "entry": 21880.0,           // Current price from TradingView
  "stop": 21850.0,            // Your Pine Script calculates this
  "target1": 21940.0,         // Your Pine Script calculates this
  "target2": 22000.0,         // Your Pine Script calculates this
  "rsi": 55.0,                // RSI indicator value
  "atr": 35.0,                // Average True Range (volatility)
  "volume_ratio": 1.3         // Current volume vs average
}
```

**Source:** Your TradingView Pine Script strategy

---

## 🤖 AI ANALYSIS LAYER

### **1. Market Context Data**

#### **A. Fear & Greed Index**
- **Source:** https://api.alternative.me/fng/
- **What it provides:** Market sentiment score (0-100)
- **Free:** Yes
- **Update frequency:** Daily
- **Example:** 52 = Neutral, 75 = Greed, 25 = Fear

```python
# Code location: backend/ai/context.py, line 45
async def _get_market_sentiment(self):
    url = "https://api.alternative.me/fng/"
    # Returns: fear_greed_index, sentiment_score, description
```

#### **B. SPY Market Trend** (Optional - if you add Alpha Vantage key)
- **Source:** Alpha Vantage API
- **What it provides:** S&P 500 ETF price and trend
- **Free tier:** 25 requests/day
- **Example:** SPY +0.45% = Bullish market

```python
# Code location: backend/ai/context.py, line 100
async def _get_market_conditions(self):
    url = "https://www.alphavantage.co/query"
    params = {"function": "GLOBAL_QUOTE", "symbol": "SPY"}
    # Returns: spy_price, spy_change_pct, spy_trend
```

#### **C. Financial News** (Optional - if you add NewsAPI key)
- **Source:** NewsAPI.org
- **What it provides:** Recent financial headlines
- **Free tier:** 100 requests/day
- **Example:** "Tech earnings beat expectations"

```python
# Code location: backend/ai/context.py, line 125
async def _get_recent_news(self):
    url = "https://newsapi.org/v2/everything"
    params = {"q": "nasdaq OR tech stocks OR futures"}
    # Returns: List of recent headlines with sentiment
```

#### **D. Time of Day Analysis**
- **Source:** System clock (local calculation)
- **What it provides:** Trading hour quality assessment
- **Algorithm:**

```python
# Code location: backend/ai/context.py, line 175
def _analyze_time_of_day(self):
    hour = current_time.hour
    
    if 9.5 <= hour <= 11.5:
        quality = "Excellent"  # Morning session
    elif 14 <= hour <= 15.5:
        quality = "Good"       # Afternoon session
    elif 11.5 <= hour <= 14:
        quality = "Poor"       # Lunch chop
    else:
        quality = "Risky"      # Near close
```

---

### **2. AI Decision Engine**

#### **Google Gemini 1.5 Flash** (or OpenAI GPT-4o-mini)
- **Source:** Your GOOGLE_API_KEY
- **What it does:** Analyzes the complete picture
- **Input to AI:**

```python
# Code location: backend/ai/prompts.py, line 25
prompt = f"""
You are an expert NQ futures trader. Analyze this setup:

SIGNAL:
- Direction: {direction}
- Entry: {entry}
- Stop: {stop}
- RSI: {rsi}
- ATR: {atr}

MARKET CONTEXT:
- Sentiment: {fear_greed_text} ({fear_greed_index})
- SPY Trend: {spy_trend} ({spy_change_pct}%)
- Time: {current_time} - {time_quality}
- Recent News: {news_headlines}

Provide analysis in JSON format:
{
  "score": 0-100,
  "recommendation": "YES|NO|MAYBE",
  "risk_level": "LOW|MEDIUM|HIGH",
  "reasoning": ["point 1", "point 2"],
  "position_size": "0.5x|1x|1.5x|2x",
  "confidence": 0.0-1.0
}
"""
```

**AI Output Example:**
```json
{
  "score": 75,
  "recommendation": "YES",
  "risk_level": "MEDIUM",
  "reasoning": [
    "Strong bullish context with tech sector strength",
    "Good R/R ratio of 2.3:1",
    "Prime trading hour with high liquidity"
  ],
  "position_size": "1x",
  "confidence": 0.75
}
```

---

## 🎯 TRADE PLAN CALCULATIONS

### **3. Entry Zones Calculation**

**Algorithm:** Based on ATR (Average True Range)

```python
# Code location: backend/ai/trade_planner.py, line 75
def _calculate_entry_zones(self, entry, direction, atr):
    if direction == "LONG":
        aggressive = entry                    # Enter now
        optimal = entry - (atr * 0.25)       # Wait for 25% ATR pullback
        conservative = entry - (atr * 0.5)   # Wait for 50% ATR pullback
```

**Example with NQ at 21880, ATR = 35:**
- Aggressive: 21880 (no pullback)
- Optimal: 21880 - (35 × 0.25) = 21871.25
- Conservative: 21880 - (35 × 0.5) = 21862.50

**Why ATR?** It's a measure of volatility. Bigger ATR = bigger pullbacks expected.

---

### **4. Profit Targets Calculation**

**Algorithm:** Risk multiples (R) + ATR-based extensions

```python
# Code location: backend/ai/trade_planner.py, line 110
def _calculate_targets(self, entry, stop, direction, atr, ai_analysis):
    risk = abs(entry - stop)  # Risk in points
    
    if direction == "LONG":
        target_1 = entry + (risk * 1.5)   # 1.5R
        target_2 = entry + (risk * 2.5)   # 2.5R
        target_3 = entry + (risk * 4.0)   # 4.0R
        target_4 = entry + (atr * 4)      # Extended (ATR-based)
```

**Example with Entry 21880, Stop 21850 (Risk = 30 pts), ATR = 35:**
- Target 1: 21880 + (30 × 1.5) = 21925 (1.5:1 R/R)
- Target 2: 21880 + (30 × 2.5) = 21955 (2.5:1 R/R)
- Target 3: 21880 + (30 × 4.0) = 22000 (4.0:1 R/R)
- Target 4: 21880 + (35 × 4) = 22020 (Extended)

**Probabilities:** Adjusted based on AI score
```python
base_probability = [70, 50, 30, 15]  # For targets 1-4
adjustment = (ai_score - 50) / 100   # -0.5 to +0.5

# If AI score = 75:
# adjustment = (75 - 50) / 100 = 0.25
# Target 1: 70 * (1 + 0.25) = 87.5%
```

---

### **5. Position Sizing Calculation**

**Algorithm:** Fixed fractional position sizing (1% risk rule)

```python
# Code location: backend/ai/trade_planner.py, line 200
def _calculate_position_sizing(self, account_balance, risk_points, ai_analysis):
    # Base risk: 1% of account
    base_risk_amount = account_balance * 0.01
    
    # Adjust based on AI confidence
    if ai_score >= 80 and confidence >= 0.75:
        risk_multiplier = 1.5  # Increase for high-quality
    elif ai_score >= 70:
        risk_multiplier = 1.0  # Standard
    elif ai_score >= 60:
        risk_multiplier = 0.5  # Reduce for marginal
    
    adjusted_risk = base_risk_amount * risk_multiplier
    
    # Calculate contracts (NQ = $20 per point)
    contracts = adjusted_risk / (risk_points * 20)
```

**Example with $10,000 account, 30 pts risk, AI score 75:**
- Base risk: $10,000 × 0.01 = $100
- Risk multiplier: 1.0 (score 75 = standard)
- Adjusted risk: $100 × 1.0 = $100
- Contracts: $100 / (30 × $20) = 0.167 → **1 contract**
- Actual risk: 1 × 30 × $20 = **$600**

---

### **6. Profit Scenarios Calculation**

**Algorithm:** Weighted average based on target allocation

```python
# Code location: backend/ai/trade_planner.py, line 350
def _generate_scenarios(self, entry, targets, stop, ai_analysis):
    point_value = 20  # NQ
    risk_points = abs(entry - stop)
    
    # Expected Case: Targets 1-2 hit
    expected_profit_points = (
        abs(targets[0]['price'] - entry) * 0.5 +  # 50% at T1
        abs(targets[1]['price'] - entry) * 0.3    # 30% at T2
        # Remaining 20% at breakeven = 0
    )
    expected_profit_usd = expected_profit_points * point_value
```

**Example with Entry 21880, T1 21925, T2 21963:**
- T1 profit: (21925 - 21880) × 0.5 = 45 × 0.5 = 22.5 pts
- T2 profit: (21963 - 21880) × 0.3 = 83 × 0.3 = 24.9 pts
- Total: 22.5 + 24.9 = 47.4 pts
- USD: 47.4 × $20 = **$948**

---

### **7. Dynamic Stop-Loss Strategy**

**Algorithm:** Trailing stops based on target achievement

```python
# Code location: backend/ai/trade_planner.py, line 270
def _generate_stop_strategy(self, entry, initial_stop, targets, direction):
    return {
        "initial_stop": initial_stop,
        "breakeven_rule": {
            "trigger": targets[0]['price'],  # When T1 hit
            "action": f"Move stop to {entry}"  # Move to breakeven
        },
        "trailing_stops": [
            {"trigger": targets[0]['price'], "stop_price": entry},
            {"trigger": targets[1]['price'], "stop_price": targets[0]['price']},
            {"trigger": targets[2]['price'], "stop_price": targets[1]['price']}
        ]
    }
```

---

## 📐 MATHEMATICAL FORMULAS USED

### **1. Risk/Reward Ratio**
```
R/R = (Target - Entry) / (Entry - Stop)

Example:
Entry: 21880
Stop: 21850
Target: 21925

R/R = (21925 - 21880) / (21880 - 21850)
    = 45 / 30
    = 1.5:1
```

### **2. Position Size (Kelly Criterion Simplified)**
```
Position Size = (Account × Risk%) / (Risk in Points × Point Value)

Example:
Account: $10,000
Risk%: 1%
Risk Points: 30
Point Value: $20

Position = ($10,000 × 0.01) / (30 × $20)
         = $100 / $600
         = 0.167 contracts
         ≈ 1 contract (rounded)
```

### **3. Expected Value**
```
EV = (Win% × Avg Win) - (Loss% × Avg Loss)

Example:
Win%: 60%
Avg Win: $960
Loss%: 40%
Avg Loss: $600

EV = (0.60 × $960) - (0.40 × $600)
   = $576 - $240
   = $336 per trade
```

### **4. Probability Adjustment**
```
Adjusted Probability = Base Probability × (1 + AI Score Adjustment)

AI Score Adjustment = (AI Score - 50) / 100

Example:
Base Probability: 70%
AI Score: 75

Adjustment = (75 - 50) / 100 = 0.25
Adjusted = 70 × (1 + 0.25) = 87.5%
```

---

## 🔄 DATA FLOW DIAGRAM

```
┌─────────────────────────────────────────────────────────┐
│ 1. TRADINGVIEW SIGNAL                                   │
│    • Entry, Stop, Targets (from your Pine Script)      │
│    • RSI, ATR, Volume (technical indicators)           │
└────────────────────┬────────────────────────────────────┘
                     ↓
┌─────────────────────────────────────────────────────────┐
│ 2. MARKET CONTEXT GATHERING                             │
│    • Fear & Greed Index (alternative.me API)           │
│    • SPY Trend (Alpha Vantage API - optional)          │
│    • News Headlines (NewsAPI - optional)               │
│    • Time of Day (system clock + algorithm)            │
└────────────────────┬────────────────────────────────────┘
                     ↓
┌─────────────────────────────────────────────────────────┐
│ 3. AI ANALYSIS (Google Gemini)                          │
│    Input: Signal + Context                             │
│    Output: Score, Recommendation, Risk Level           │
└────────────────────┬────────────────────────────────────┘
                     ↓
┌─────────────────────────────────────────────────────────┐
│ 4. TRADE PLAN CALCULATIONS                              │
│    • Entry Zones (ATR-based algorithm)                 │
│    • Targets (Risk multiples + ATR)                    │
│    • Position Size (1% risk rule + AI adjustment)      │
│    • Scenarios (Weighted probability math)             │
│    • Stops (Trailing algorithm)                        │
└────────────────────┬────────────────────────────────────┘
                     ↓
┌─────────────────────────────────────────────────────────┐
│ 5. FORMATTED ALERT                                      │
│    • All data combined into readable format            │
│    • Sent to your Telegram                             │
└─────────────────────────────────────────────────────────┘
```

---

## 📚 CODE LOCATIONS

### **Where Each Calculation Happens:**

| Component | File | Function | Lines |
|-----------|------|----------|-------|
| Market Context | `backend/ai/context.py` | `get_market_context()` | 30-60 |
| Fear & Greed | `backend/ai/context.py` | `_get_market_sentiment()` | 45-75 |
| SPY Trend | `backend/ai/context.py` | `_get_market_conditions()` | 100-135 |
| News | `backend/ai/context.py` | `_get_recent_news()` | 125-160 |
| Time Analysis | `backend/ai/context.py` | `_analyze_time_of_day()` | 175-210 |
| AI Analysis | `backend/ai/analyzer.py` | `analyze_trade()` | 35-75 |
| AI Prompts | `backend/ai/prompts.py` | `get_trade_analysis_prompt()` | 10-120 |
| Entry Zones | `backend/ai/trade_planner.py` | `_calculate_entry_zones()` | 75-100 |
| Targets | `backend/ai/trade_planner.py` | `_calculate_targets()` | 110-180 |
| Position Size | `backend/ai/trade_planner.py` | `_calculate_position_sizing()` | 200-250 |
| Scenarios | `backend/ai/trade_planner.py` | `_generate_scenarios()` | 350-420 |
| Stops | `backend/ai/trade_planner.py` | `_generate_stop_strategy()` | 270-300 |

---

## 🎓 SUMMARY - WHAT'S BEING USED

### **Data Sources:**
1. ✅ **TradingView** - Your signal (entry, stop, targets, indicators)
2. ✅ **Fear & Greed Index** - Market sentiment (FREE)
3. ⏳ **Alpha Vantage** - SPY trend (optional, FREE tier)
4. ⏳ **NewsAPI** - Financial news (optional, FREE tier)
5. ✅ **System Clock** - Time of day analysis
6. ✅ **Google Gemini** - AI analysis (FREE tier)

### **Algorithms:**
1. ✅ **ATR-based Entry Zones** - Volatility-adjusted pullbacks
2. ✅ **Risk Multiple Targets** - 1.5R, 2.5R, 4R progression
3. ✅ **Fixed Fractional Position Sizing** - 1% risk rule
4. ✅ **Probability Adjustment** - AI score-based weighting
5. ✅ **Trailing Stop Logic** - Target-based progression
6. ✅ **Weighted Scenario Calculation** - Expected value math

### **Cost:**
- **FREE** if using Google Gemini + free tier APIs
- **~$3/month** if using OpenAI instead

---

**Everything is transparent, mathematical, and based on proven trading principles!** 📊

Want me to explain any specific calculation in more detail?
