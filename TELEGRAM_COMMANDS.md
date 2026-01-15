# Telegram Bot Commands

## Available Commands

### 🔎 Analysis Commands

#### `/check` - Analyze NQ (Default)
Get instant NQ market analysis using Deep Learning AI (with fallback to Technical Analysis).

**Usage:**
```
/check
```

**Output includes:**
- AI Prediction (LONG/SHORT/NEUTRAL)
- Confidence percentage
- AI Score
- Analysis method (Deep Learning or Technical Analysis)
- Complete trade setup:
  - Trade type (⚡ SCALP / 📊 DAY TRADE / 📈 SWING TRADE)
  - Entry price
  - Stop loss (with risk in points)
  - 2 Targets (with reward in points and R:R ratios)
  - Support & Resistance levels
  - Risk per contract
  - ATR
- Market session info
- Economic context
- News sentiment
- Technical indicators (Price, RSI, Trend)

#### `/check <SYMBOL>` - Analyze Other Symbols
Analyze other futures symbols using Technical Analysis.

**Supported symbols:**
- `ES` - S&P 500 E-mini
- `YM` - Dow Jones E-mini
- `CL` - Crude Oil
- `GC` - Gold
- `RTY` - Russell 2000

**Usage:**
```
/check ES
/check GC
```

### 🎮 Control Commands

#### `/pause` - Pause Alerts
Stop receiving all alerts temporarily.

#### `/resume` - Resume Alerts
Resume receiving alerts after pausing.

#### `/threshold <score>` - Set Minimum Score
Set the minimum AI score for alerts (50-100).

**Usage:**
```
/threshold 75
/threshold 80
```

**Expected frequency:**
- 50-60: 10-20 alerts/day
- 60-70: 5-10 alerts/day
- 70-80: 2-5 alerts/day
- 80+: 1-3 alerts/day

### ℹ️ Information Commands

#### `/status` - System Health Check
View current system status, uptime, and component health.

#### `/stats` - Performance Statistics
View today's alert statistics and performance metrics.

#### `/help` - Command Guide
Display full command list with descriptions.

#### `/symbols` - Supported Symbols
List all supported trading symbols with details.

## Alert Format

### Trade Setup Display

```
🟢 PREDICTION: LONG
💪 Confidence: 65.0%
🎯 AI Score: 72
📊 Method: Technical Analysis

💰 TRADE SETUP 🟢 LONG 📈 SWING TRADE
⏱️ Duration: 1-3 days (Hold overnight)
📍 Entry: 25,385.25
🛑 Stop: 25,229.25 (-156 pts)
🎯 T1: 25,619.25 (+234 pts) [1.5R]
🎯 T2: 25,853.25 (+468 pts) [3.0R]

📊 KEY LEVELS
Support: 25,300 | 25,265 | 25,250
Resistance: 25,457 | 25,634 | 25,717

💰 Risk: $3,121/contract
📈 ATR: 104.0 pts

⏰ MARKET SESSION
Time: 2026-01-04 10:55:06 EST
💡 ⏸️ MARKET CLOSED - Wait for Sunday 6 PM ET open

📅 ECONOMIC CONTEXT
Risk Level: NORMAL
💡 NORMAL TRADING

➡️ NEWS: NEUTRAL (50%)

📊 TECHNICAL
Price: 25,385.25
RSI: 38.1
Trend: DOWN
```

## Notes

- **NQ Analysis**: Uses Deep Learning (Transformer model) with fallback to Technical Analysis
- **Other Symbols**: Use Technical Analysis (heuristic-based)
- **Distance Signs**: 
  - Negative (-) = Risk (stop loss)
  - Positive (+) = Reward (targets)
- **Support/Resistance**: Ordered by proximity to current price (closest first)
- **Market Hours**: System monitors 24/5 during futures market hours
- **TradingView Integration**: Webhook alerts work independently of /check command
