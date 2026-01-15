# Changelog

## [2026-01-04] - AI "Pro Upgrade" (Liquidity Sweep & Trade Manager)

### Added
- **Liquidity Sweep Detection (The "Alpha" Signal)**
  - Detects "fake-out" wicks that reclaim support/resistance (classic NQ trap).
  - Overrides standard Direction signal with "🌊 LIQUIDITY SWEEP SETUP".
- **Dynamic Trade Manager**
  - Background monitoring of all active AI trades.
  - **Lock Profit Alerts**: Automatically alerts when T1 is hit to lock 50% profit.
- **Confluence Scoring (NQ Specific)**
  - Explicitly checks **21 EMA** (Institutional NQ Level).
  - Score includes: Trend (21 EMA) + Momentum (RSI) + Candle Body.
- **10 AM Reversal Watch**
  - Warns of high-volatility reversal window (09:50-10:10 AM ET).

### Changed
- **Technical Analysis**: Now uses EMA_21 and EMA_200.
- **Telegram Formatting**: Displays Confluence details and Reversal warnings.

## [2026-01-04] - Telegram /check Command Fixes & Alert Formatting Improvements

### Fixed
- **Telegram /check Command**
  - Fixed method name from `calculate_features` to `calculate_all_features` in callback function
  - Fixed feature column names (RSI_14 → RSI, EMA_9 → SMA_10, EMA_21 → SMA_20)
  - Added proper checks for `transformer_model` existence before use
  - Added try-catch blocks around all optional components (trade_calculator, economic_calendar, news_analyzer, session_analyzer)
  - Removed Markdown formatting from error messages to prevent Telegram parsing errors
  - Added graceful fallback to technical analysis when transformer model fails

- **Trade Alert Formatting**
  - Fixed stop/target distance signs to show correct direction:
    - Stop loss: Now shows NEGATIVE (e.g., -156 pts = risk)
    - Targets: Now show POSITIVE (e.g., +234 pts = reward)
  - Added clear trade direction display in setup header (🟢 LONG or 🔴 SHORT)
  - Fixed RSI precision from 15+ decimals to 1 decimal place (38.125272753945524 → 38.1)
  - Improved market session logic to avoid contradictory information
  - Better handling of SIDEWAYS/NEUTRAL predictions

- **Trade Calculator**
  - Updated distance calculations to use signed values based on trade direction
  - LONG trades: Stop distance is negative (risk), targets are positive (reward)
  - SHORT trades: Stop distance is negative (risk), targets are positive (reward)

- **Telegram Bot Handler**
  - Enhanced error logging with full traceback
  - Added debug logging for command processing
  - Improved RSI formatting with type checking
  - Fixed market session display to only show relevant details when market is open

### Verified
- Support/Resistance level ordering is correct (closest to price first)
- All formatting follows industry standard conventions
- Local self-test passed successfully

### Technical Details
- Modified files:
  - `backend/main.py` - Fixed callback function
  - `backend/analysis/trade_calculator.py` - Fixed distance calculations
  - `backend/utils/telegram_bot.py` - Improved formatting and error handling
