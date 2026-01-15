"""
Feature Engineer
Calculates technical indicators using pandas_ta and creates robust ML features
Refactored for Phase 1 Pro Upgrade
"""

import pandas as pd
import numpy as np
try:
    import pandas_ta as ta
    PANDAS_TA_AVAILABLE = True
except ImportError:
    PANDAS_TA_AVAILABLE = False
    ta = None
import logging

logger = logging.getLogger(__name__)


class FeatureEngineer:
    """Creates features for machine learning models using pandas_ta"""
    
    def __init__(self):
        self.feature_names = []
    
    def calculate_all_features(self, df):
        """
        Calculate all technical indicators and features using pandas_ta
        
        Args:
            df: DataFrame with OHLCV data
            
        Returns:
            DataFrame with all features added
        """
        if not PANDAS_TA_AVAILABLE:
            logger.error("pandas_ta is not available - cannot calculate features")
            raise ImportError(
                "pandas_ta is required for feature calculation. "
                "Install it with: pip install pandas-ta"
            )
        
        logger.info("Calculating features with pandas_ta...")
        
        df = df.copy()
        
        # Ensure we have a datetime index if not already
        logger.info(f"DEBUG INPUT INDEX: type={type(df.index)}")
        if len(df) > 0: logger.info(f"DEBUG HEAD INDEX: {df.index[:5]}")

        if not isinstance(df.index, pd.DatetimeIndex):
            try:
                # Try converting the text index to datetime
                df.index = pd.to_datetime(df.index, utc=True) # Ensure UTC to handle mixed TZ
            except Exception as e:
                logger.warning(f"Index conversion failed: {e}")
                # Fallback: Check columns
                if 'Date' in df.columns:
                    df['Date'] = pd.to_datetime(df['Date'], utc=True)
                    df.set_index('Date', inplace=True)
                elif 'Datetime' in df.columns:
                    df['Datetime'] = pd.to_datetime(df['Datetime'], utc=True)
                    df.set_index('Datetime', inplace=True)
                else:
                    logger.warning("Could not convert index to DatetimeIndex. Time features may fail.")

        # Force DatetimeIndex if it's still generic Index but contains dates
        if not isinstance(df.index, pd.DatetimeIndex):
             try:
                 df.index = pd.DatetimeIndex(df.index)
             except Exception as e:
                 logger.warning(f"Final DatetimeIndex force failed: {e}")
        
        # Ensure OHLCV are numeric
        numeric_cols = ['Open', 'High', 'Low', 'Close', 'Volume']
        for col in numeric_cols:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors='coerce')

        # Verify it worked
        if not isinstance(df.index, pd.DatetimeIndex):
             # Final attempt: inspect if we can rescue it
             pass # Will likely duplicate error below but let's proceed

        
        # --- Trend Indicators ---
        # Moving Averages
        df["SMA_10"] = ta.sma(df["Close"], length=10)
        df["SMA_20"] = ta.sma(df["Close"], length=20)
        df["SMA_50"] = ta.sma(df["Close"], length=50)
        df["EMA_12"] = ta.ema(df["Close"], length=12)
        df["EMA_21"] = ta.ema(df["Close"], length=21) # NQ Institutional Level
        df["EMA_26"] = ta.ema(df["Close"], length=26)
        df["EMA_200"] = ta.ema(df["Close"], length=200) # Long term trend
        
        # Price relative to MAs
        df['Price_vs_SMA20'] = (df['Close'] - df['SMA_20']) / df['SMA_20']
        df['Price_vs_SMA50'] = (df['Close'] - df['SMA_50']) / df['SMA_50']
        
        # Crosses
        df['SMA_10_20_Cross'] = (df['SMA_10'] > df['SMA_20']).astype(int)
        
        # --- Momentum Indicators ---
        # RSI
        df["RSI"] = ta.rsi(df["Close"], length=14)
        
        # ADX (Trend Strength)
        try:
            adx = ta.adx(df['High'], df['Low'], df['Close'], length=14)
            if adx is not None:
                df = pd.concat([df, adx], axis=1) # Adds ADX_14, DMP_14, DMN_14
        except Exception as e:
            logger.warning(f"Could not calc ADX: {e}")
        
        # MACD
        macd = ta.macd(df["Close"])
        df = pd.concat([df, macd], axis=1) # Adds MACD_12_26_9, MACDh_12_26_9, MACDs_12_26_9
        
        # Stochastic RSI
        stochrsi = ta.stochrsi(df["Close"])
        df = pd.concat([df, stochrsi], axis=1)
        
        # Know Sure Thing (KST)
        try:
            kst = ta.kst(df["Close"])
            if kst is not None:
                df = pd.concat([df, kst], axis=1)
        except Exception as e:
            logger.warning(f"Could not calc KST: {e}")
            
        # Rate of Change
        df['ROC_10'] = ta.roc(df['Close'], length=10)
        
        # --- Volatility Indicators ---
        # ATR
        df['ATR'] = ta.atr(df['High'], df['Low'], df['Close'], length=14)
        df['ATR_Pct'] = df['ATR'] / df['Close']
        
        # Bollinger Bands
        bb = ta.bbands(df['Close'], length=20, std=2)
        df = pd.concat([df, bb], axis=1)
        
        # Donchian Channels
        donchian = ta.donchian(df['High'], df['Low'], lower_length=20, upper_length=20)
        df = pd.concat([df, donchian], axis=1)
        
        # --- Volume Indicators ---
        # OBV (On-Balance Volume)
        df['OBV'] = ta.obv(df['Close'], df['Volume'])
        
        # Force Index
        try:
            df['EFI'] = ta.efi(df['Close'], df['Volume'], length=13)
        except Exception as e:
            logger.warning(f"Could not calc EFI: {e}")
            
        # Volume Price Trend (VPT) - manual if not in ta, or check ta.pvt
        # df['VPT'] = (df['Volume'] * df['Close'].pct_change()).cumsum() # Simple VPT
        
        # --- Pattern & Price Action ---
        # Body Size
        df['Body_Size'] = abs(df['Close'] - df['Open']) / df['Close']
        df['Upper_Shadow'] = (df['High'] - df[['Open', 'Close']].max(axis=1)) / df['Close']
        df['Lower_Shadow'] = (df[['Open', 'Close']].min(axis=1) - df['Low']) / df['Close']
        
        # --- Time Features ---
        if hasattr(df.index, 'hour'):
            df['Hour'] = df.index.hour
            df['DayOfWeek'] = df.index.dayofweek
        else:
            logger.warning("Index does not have time attributes (hour/dayofweek). Using defaults.")
            df['Hour'] = 0
            df['DayOfWeek'] = 0
        
        # ===== INSTITUTIONAL FEATURES (from GreenBack Riders) =====
        logger.info("Adding institutional features...")
        
        # 1. EMA 20 (60-minute) - Trend Anchor
        df = self._add_60m_ema(df)
        
        # 2. Fair Value Gap (FVG) Detection
        df = self._detect_fvg(df)
        
        # 3. Opening Drive Patterns
        df = self._detect_opening_drive(df)
        
        # 4. Gap Analysis
        df = self._analyze_gaps(df)

        # 5. STRATEGY SIGNALS (Pine Script Logic)
        df = self._add_strategy_signals(df)

        # 6. MARKET CONTEXT (VIX)
        df = self._add_vix_features(df)

        # 7. EVENT CONTEXT (World Data)
        df = self._add_event_features(df)
        
        # --- Cleanup ---
        
        # --- Multi-Timeframe Features (Phase 4 Enhancement) ---
        # "RightChoice" Style: Triple Screen Logic (RSI + MACD + ADX Fusion)
        
        # 1. Momentum Pulse (RSI)
        if 'RSI_14' in df.columns:
             df['RSI_Overbought'] = np.where(df['RSI_14'] > 70, 1, 0)
             df['RSI_Oversold'] = np.where(df['RSI_14'] < 30, 1, 0)
        
        # 2. Trend Pulse (MACD)
        # MACD_12_26_9 is the line, MACDs_12_26_9 is signal
        if 'MACD_12_26_9' in df.columns and 'MACDs_12_26_9' in df.columns:
             df['MACD_Bullish'] = np.where(df['MACD_12_26_9'] > df['MACDs_12_26_9'], 1, 0)
        
        # 3. Volatility Filter (ADX)
        if 'ADX_14' in df.columns:
            df['Trending_State'] = np.where(df['ADX_14'] > 25, 1, 0)
            
        # 4. Multi-Frame Simulation (HTF Trend)
        # Using SMA50 vs SMA200 as proxy for higher timeframe
        if 'SMA_50' in df.columns and 'SMA_200' in df.columns:
            df['HTF_Trend_Bullish'] = np.where(df['SMA_50'] > df['SMA_200'], 1, 0)

        # Flatten columns if MultiIndex
        if isinstance(df.columns, pd.MultiIndex):
            df.columns = [
                "_".join([str(c) for c in col]).strip() if isinstance(col, tuple) else str(col)
                for col in df.columns
            ]
        
        # Ensure simple column names (pandas_ta can produce tuples)
        df.columns = [str(col) for col in df.columns]

        # Force all data to numeric (coercing errors) to avoid 'object' columns
        # This fixes the XGBoost error: "Invalid columns: EMA_200: object"
        for col in df.columns:
            if col not in ['Date', 'Datetime', 'Target']: # Skip target/index-like if present
                 df[col] = pd.to_numeric(df[col], errors='coerce')

        # Remove NaN rows created by lookback periods
        initial_len = len(df)
        df = df.dropna()
        logger.info(f"Removed {initial_len - len(df)} rows with NaN values")
        
        # Store feature names (exclude raw price cols)
        exclude_cols = ['Open', 'High', 'Low', 'Close', 'Volume', 'Adj Close', 'Date', 'Datetime', 'Target']
        self.feature_names = [col for col in df.columns if col not in exclude_cols]
        
        # Validate and Clean
        df = self._clean_and_validate(df)
        
        logger.info(f"Created {len(self.feature_names)} features")
        
        return df
    
    def _clean_and_validate(self, df):
        """Clean dataframe of NaNs, Infs, and ensure numeric types"""
        # 1. Replace Infinite with NaNs
        df = df.replace([np.inf, -np.inf], np.nan)
        
        # 2. Force Numeric
        # Identify price columns (Critical - MUST NOT BE 0)
        price_cols = [c for c in ['Open', 'High', 'Low', 'Close'] if c in df.columns]
        
        # Identify columns to clean
        cols_to_clean = [col for col in df.columns if col not in ['Date', 'Datetime', 'Target']]
        
        for col in cols_to_clean:
            if df[col].dtype == 'object':
                 df[col] = pd.to_numeric(df[col], errors='coerce')
        
        # 3. Handle Price NaNs -> DROP
        # We cannot train on rows with no price data
        df = df.dropna(subset=price_cols)
        
        # 4. Fill Feature NaNs
        # Forward fill first
        df[cols_to_clean] = df[cols_to_clean].ffill()
        # Fill remaining (indicators at start) with 0
        df[cols_to_clean] = df[cols_to_clean].fillna(0)
        
        return df
    
    def create_target(self, df, lookahead=5, threshold=0.001):
        """
        Create 'Future Mean' Target
        Label each row from the mean of the *next* `lookahead` closes:
          2 (UP)    : future_mean >= current * (1 + threshold)
          1 (DOWN)  : future_mean <= current * (1 - threshold)
          0 (SIDEWAYS): otherwise
          
        Args:
            df: DataFrame with features
            lookahead: How many periods ahead to include in the mean
            threshold: Percentage threshold (e.g., 0.001 = 0.1%)
            
        Returns:
            DataFrame with 'Target' column
        """
        df = df.copy()
        
        # Calculate Future Mean (Robust Labeling)
        # Shift -1 to start from next candle, then roll
        indexer = pd.api.indexers.FixedForwardWindowIndexer(window_size=lookahead)
        future_mean = df['Close'].rolling(window=indexer).mean()
        
        # Calculate percentage change between Future Mean and Current Close
        pct_change = (future_mean - df['Close']) / df['Close']
        
        # Assign Labels
        conditions = [
            pct_change >= threshold,  # UP
            pct_change <= -threshold  # DOWN
        ]
        choices = [2, 1] # 2=UP, 1=DOWN
        df['Target'] = np.select(conditions, choices, default=0) # 0=SIDEWAYS
        
        # Remove rows with NaN target (end of dataset)
        df = df.dropna(subset=['Target'])
        # Force Integer
        df['Target'] = df['Target'].astype(int)
        
        logger.info(f"Target distribution:\n{df['Target'].value_counts()}")
        
        return df
    
    def create_target_daily(self, df, threshold=0.01):
        """
        Create Target for DAILY data (leveraged ETFs)
        
        Based on research: Leveraged ETFs rebalance daily, so we predict
        next-day directional movement with higher threshold due to volatility.
        
        Args:
            df: DataFrame with daily OHLCV data
            threshold: Percentage threshold (0.01 = 1% for leveraged ETFs)
        
        Returns:
            DataFrame with 'Target' column
        """
        df = df.copy()
        
        # Calculate next-day return
        df['Next_Close'] = df['Close'].shift(-1)
        df['Daily_Return'] = (df['Next_Close'] - df['Close']) / df['Close']
        
        # Assign Labels (higher threshold for leveraged ETFs)
        conditions = [
            df['Daily_Return'] >= threshold,   # UP (>1%)
            df['Daily_Return'] <= -threshold   # DOWN (<-1%)
        ]
        choices = [2, 1]  # 2=UP, 1=DOWN
        df['Target'] = np.select(conditions, choices, default=0)  # 0=SIDEWAYS
        
        # Clean up
        df = df.drop(['Next_Close', 'Daily_Return'], axis=1)
        df = df.dropna(subset=['Target'])
        # Force Integer
        df['Target'] = df['Target'].astype(int)
        
        logger.info(f"Daily Target distribution:\n{df['Target'].value_counts()}")
        
        return df
    
    def create_target_auto(self, df, symbol="NQ", threshold_hourly=0.001, threshold_daily=0.01):
        """
        Automatically choose target creation method based on data frequency
        
        Args:
            df: DataFrame with OHLCV data
            symbol: Symbol being trained
            threshold_hourly: Threshold for hourly data
            threshold_daily: Threshold for daily data
        
        Returns:
            DataFrame with 'Target' column
        """
        # Detect data frequency
        if len(df) > 1:
            time_diff = (df.index[1] - df.index[0]).total_seconds() / 3600
            is_daily = time_diff >= 20  # 20+ hours = daily data
        else:
            is_daily = False
        
        # ETFs should use daily logic
        etf_symbols = ['TQQQ', 'SQQQ', 'SOXL', 'SOXS']
        is_etf = symbol.upper() in etf_symbols
        
        if is_daily or is_etf:
            logger.info(f"Using DAILY target creation for {symbol}")
            return self.create_target_daily(df, threshold=threshold_daily)
        else:
            logger.info(f"Using HOURLY target creation for {symbol}")
            return self.create_target(df, lookahead=5, threshold=threshold_hourly)
    
    def calculate_4h_rsi(self, df_1h):
        """
        Resample 1H data to 4H and calculate RSI
        
        Args:
            df_1h: DataFrame with 1-hour OHLCV data
            
        Returns:
            Series with 4H RSI values aligned to 1H index
        """
        # Resample to 4H
        df_4h = df_1h.resample('4H').agg({
            'Open': 'first',
            'High': 'max',
            'Low': 'min',
            'Close': 'last',
            'Volume': 'sum'
        }).dropna()
        
        # Calculate 4H RSI
        df_4h['RSI_4H'] = ta.rsi(df_4h['Close'], length=14)
        
        # Forward fill to align with 1H index
        rsi_4h_aligned = df_4h['RSI_4H'].reindex(df_1h.index, method='ffill')
        
        return rsi_4h_aligned
    
    def check_mtf_rsi_alignment(self, rsi_1h: float, rsi_4h: float, direction: str) -> bool:
        """
        Check if both 1H and 4H RSI show extreme values in same direction
        
        Args:
            rsi_1h: 1-hour RSI value
            rsi_4h: 4-hour RSI value  
            direction: Trade direction ("LONG" or "SHORT")
            
        Returns:
            True if both timeframes aligned, False otherwise
        """
        if pd.isna(rsi_1h) or pd.isna(rsi_4h):
            return False
        
        if direction == "LONG":
            # Both timeframes oversold
            return rsi_1h < 30 and rsi_4h < 35
        elif direction == "SHORT":
            # Both timeframes overbought
            return rsi_1h > 70 and rsi_4h > 65
        
        return False
    
    # ===== INSTITUTIONAL FEATURE METHODS =====
    
    def _add_60m_ema(self, df):
        """Add 60-minute EMA 20 (Trend Anchor from Discord)"""
        try:
            # Check if data is already daily (skip resampling)
            if len(df) > 1:
                time_diff = (df.index[1] - df.index[0]).total_seconds() / 3600
                is_daily = time_diff >= 20
            else:
                is_daily = False
            
            if is_daily:
                # For daily data, use EMA 20 directly (already daily)
                df['EMA_20_60m'] = ta.ema(df['Close'], length=20)
                df['Distance_from_EMA60m'] = (df['Close'] - df['EMA_20_60m']) / df['EMA_20_60m']
            else:
                # For hourly data, resample to 60min
                df_60m = df.resample('60T').agg({
                    'Open': 'first',
                    'High': 'max',
                    'Low': 'min',
                    'Close': 'last',
                    'Volume': 'sum'
                }).dropna()
                
                df_60m['EMA_20_60m'] = ta.ema(df_60m['Close'], length=20)
                
                # Merge back to original timeframe (forward fill)
                df = df.join(df_60m[['EMA_20_60m']], how='left')
                df['EMA_20_60m'] = df['EMA_20_60m'].ffill()
                
                # Distance from 60m EMA
                df['Distance_from_EMA60m'] = (df['Close'] - df['EMA_20_60m']) / df['EMA_20_60m']
            
        except Exception as e:
            logger.warning(f"Could not calc 60m EMA: {e}")
            df['EMA_20_60m'] = 0
            df['Distance_from_EMA60m'] = 0
        
        return df
    
    def _detect_fvg(self, df):
        """Detect Fair Value Gaps (FVG)"""
        try:
            # FVG = gap between candle 1's high and candle 3's low (or vice versa)
            df['FVG_Bullish'] = 0
            df['FVG_Bearish'] = 0
            df['FVG_Strength'] = 0.0
            
            # Convert to numpy arrays to avoid dtype issues
            highs = df['High'].values
            lows = df['Low'].values
            closes = df['Close'].values
            
            for i in range(2, len(df)):
                # Bullish FVG: candle[i-2].high < candle[i].low
                if highs[i-2] < lows[i]:
                    gap_size = float(lows[i] - highs[i-2])
                    df.iloc[i, df.columns.get_loc('FVG_Bullish')] = 1
                    df.iloc[i, df.columns.get_loc('FVG_Strength')] = (gap_size / float(closes[i])) * 100
                
                # Bearish FVG: candle[i-2].low > candle[i].high
                elif lows[i-2] > highs[i]:
                    gap_size = float(lows[i-2] - highs[i])
                    df.iloc[i, df.columns.get_loc('FVG_Bearish')] = 1
                    df.iloc[i, df.columns.get_loc('FVG_Strength')] = (gap_size / float(closes[i])) * 100
            
        except Exception as e:
            logger.warning(f"Could not detect FVG: {e}")
            df['FVG_Bullish'] = 0
            df['FVG_Bearish'] = 0
            df['FVG_Strength'] = 0.0
        
        return df
    
    def _detect_opening_drive(self, df):
        """Detect Opening Drive patterns (first 30-90 min)"""
        try:
            if hasattr(df.index, 'hour'):
                df['Is_First_Hour'] = ((df.index.hour == 9) & (df.index.minute >= 30)) | (df.index.hour == 10)
            else:
                df['Is_First_Hour'] = 0
            
            df['Time_Since_Open'] = 0
            
            # Calculate minutes since market open (9:30 AM ET)
            for idx in df.index:
                if idx.hour >= 9 and idx.minute >= 30:
                    minutes = (idx.hour - 9) * 60 + (idx.minute - 30)
                    df.loc[idx, 'Time_Since_Open'] = minutes
            
        except Exception as e:
            logger.warning(f"Could not detect opening drive: {e}")
            df['Is_First_Hour'] = 0
            df['Time_Since_Open'] = 0
        
        return df
    
    def _analyze_gaps(self, df):
        """Analyze gap opens"""
        try:
            df['Gap_Type'] = 0  # 0=No gap, 1=Gap Up, -1=Gap Down
            df['Gap_Size_Pct'] = 0
            
            # Detect gaps (current open vs previous close)
            df['Prev_Close'] = df['Close'].shift(1)
            gap_pct = ((df['Open'] - df['Prev_Close']) / df['Prev_Close']) * 100
            
            df.loc[gap_pct > 0.2, 'Gap_Type'] = 1  # Gap Up
            df.loc[gap_pct < -0.2, 'Gap_Type'] = -1  # Gap Down
            df['Gap_Size_Pct'] = gap_pct.abs()
            
            df.drop('Prev_Close', axis=1, inplace=True)
            
        except Exception as e:
            logger.warning(f"Could not analyze gaps: {e}")
            df['Gap_Type'] = 0
            df['Gap_Size_Pct'] = 0
        
        return df
    
    def _add_strategy_signals(self, df):
        """
        Add explicit strategy signals from Pine Script
        Logic:
           - Uptrend: EMA20 > EMA50
           - Long Signal: Crossover(EMA20, EMA50) + RSI Filter  OR  Crossover(Close, EMA20) + RSI Filter
        """
        try:
            # Pre-calculate required columns to ensure they exist
            if 'EMA_21' in df.columns: ema20 = df['EMA_21'] # Using EMA 21 as EMA 20 proxy (code uses 21)
            else: ema20 = ta.ema(df['Close'], length=20)
            
            if 'SMA_50' in df.columns: ema50 = df['SMA_50'] # Using SMA 50 (or calc EMA 50)
            else: ema50 = ta.ema(df['Close'], length=50) # Pine uses EMA 50
            
            rsi = df['RSI'] if 'RSI' in df.columns else ta.rsi(df['Close'], length=14)
            
            # Trend State
            df['Trend_State'] = np.where(ema20 > ema50, 1, -1)
            
            # Helper for Crossover
            # Crossover(A, B): A crosses OVER B (A > B now, A <= B prev)
            def crossover(a, b):
                return ((a > b) & (a.shift(1) <= b.shift(1))).astype(int)
            
            def crossunder(a, b):
                return ((a < b) & (a.shift(1) >= b.shift(1))).astype(int)
                
            # Long Logic
            # 1. EMA Cross AND RSI < 70
            long_cond_1 = (crossover(ema20, ema50) == 1) & (rsi < 70)
            # 2. Price Cross EMA20 AND RSI < 60 (Pullback)
            long_cond_2 = (crossover(df['Close'], ema20) == 1) & (rsi < 60)
            
            df['Signal_Long'] = (long_cond_1 | long_cond_2).astype(int)
            
            # Short Logic
            # 1. EMA Cross Under AND RSI > 30
            short_cond_1 = (crossunder(ema20, ema50) == 1) & (rsi > 30)
            # 2. Price Cross Under EMA20 AND RSI > 40 (Bounce)
            short_cond_2 = (crossunder(df['Close'], ema20) == 1) & (rsi > 40)
            
            df['Signal_Short'] = (short_cond_1 | short_cond_2).astype(int)
            
        except Exception as e:
            logger.warning(f"Could not calc Strategy Signals: {e}")
            df['Trend_State'] = 0
            df['Signal_Long'] = 0
            df['Signal_Short'] = 0
            
        return df

    def _add_vix_features(self, df):
        """Add VIX-based market context features"""
        if 'VIX_Close' not in df.columns:
            df['VIX_Close'] = 0
            df['VIX_ROC'] = 0
            df['VIX_High'] = 0
            return df
        
        try:
            # Fill NaNs in VIX
            df['VIX_Close'] = df['VIX_Close'].ffill().fillna(20)
            
            # VIX Rate of Change
            df['VIX_ROC'] = df['VIX_Close'].pct_change()
            
            # Is VIX High?
            df['VIX_High'] = (df['VIX_Close'] > 30).astype(int)
            df['VIX_Low'] = (df['VIX_Close'] < 15).astype(int)
            
            # --- NEW: VIX RANK (Percentile over 1 Year) ---
            # How scared is the market relative to the last year?
            df['VIX_Rank'] = df['VIX_Close'].rolling(window=252).rank(pct=True) * 100
            df['VIX_Rank'] = df['VIX_Rank'].fillna(50) # Default to median
            
        except Exception as e:
            logger.warning(f"Could not calc VIX features: {e}")
        
        return df

    def _add_event_features(self, df):
        """
        Add Economic Event Features (The "World Data")
        """
        try:
            # Import here to avoid circular dependency
            import sys
            import os
            
            # Add backend to path (hacky but reliable for scripts)
            current_dir = os.path.dirname(os.path.abspath(__file__))
            backend_dir = os.path.dirname(current_dir)
            if backend_dir not in sys.path:
                sys.path.insert(0, backend_dir)

            from utils.economic_calendar import EconomicCalendar
            
            calendar = EconomicCalendar()
            all_events = calendar.get_all_event_dates()
            
            # Initialize Columns
            df['Is_FOMC'] = 0
            df['Is_CPI'] = 0
            df['Is_NFP'] = 0
            df['Is_Earnings'] = 0
            df['Days_To_FOMC'] = 10 # Default cap
            df['Days_To_Earnings'] = 10
            
            # Convert Index to Date Strings for fast lookup
            date_strings = df.index.strftime('%Y-%m-%d')
            
            # 1. Flag "Is Event Today"
            df.loc[date_strings.isin(all_events['FOMC']), 'Is_FOMC'] = 1
            df.loc[date_strings.isin(all_events['CPI']), 'Is_CPI'] = 1
            df.loc[date_strings.isin(all_events['NFP']), 'Is_NFP'] = 1
            df.loc[date_strings.isin(all_events['EARNINGS']), 'Is_Earnings'] = 1
            
            # 2. Calculate "Proximity" (Days To Next Event)
            # This is expensive index-looping, so we optimize with a forward pass
            # For each day, look at future days...
            # Optimized Approach: Get list of event dates, find nearest > current
            
            fomc_dates = sorted([pd.to_datetime(d).tz_localize(None) for d in all_events['FOMC']])
            earn_dates = sorted([pd.to_datetime(d).tz_localize(None) for d in all_events['EARNINGS']])
            
            # We will use searchsorted to find next event
            # Ensure df index is tz-naive for comparison
            dates_naive = df.index.tz_localize(None)
            
            # FOMC Proximity
            next_fomc_idx = np.searchsorted(fomc_dates, dates_naive)
            # handle out of bounds (past last event)
            next_fomc_idx = np.clip(next_fomc_idx, 0, len(fomc_dates)-1)
            
            # Calculate days
            for i in range(len(df)):
                # If current date is AFTER the found event, it means we are past all events
                # (searchsorted returns len if > all). 
                # But we clipped. So check manually if fomc_dates[idx] < current.
                
                target_date = fomc_dates[next_fomc_idx[i]]
                current_date = dates_naive[i]
                
                if target_date < current_date:
                    days = 30 # Post-event default
                else:
                    days = (target_date - current_date).days
                
                df.iloc[i, df.columns.get_loc('Days_To_FOMC')] = min(days, 30) # Cap at 30
            
            # Earnings Proximity
            next_earn_idx = np.searchsorted(earn_dates, dates_naive)
            next_earn_idx = np.clip(next_earn_idx, 0, len(earn_dates)-1)
            
            for i in range(len(df)):
                target_date = earn_dates[next_earn_idx[i]]
                current_date = dates_naive[i]
                
                if target_date < current_date:
                    days = 30
                else:
                    days = (target_date - current_date).days
                
                df.iloc[i, df.columns.get_loc('Days_To_Earnings')] = min(days, 30)
                
            # 3. "Priced In" Score (Anxiety)
            # VIX High + Event Close = Max Anxiety
            if 'VIX_Rank' in df.columns:
                # Avoid div by zero
                df['Priced_In_Score'] = df['VIX_Rank'] / (df['Days_To_FOMC'] + 1)
            else:
                df['Priced_In_Score'] = 0
            
        except Exception as e:
            logger.warning(f"Could not calc Event features: {e}")
            
        return df

    
    def get_feature_matrix(self, df):
        """Extract feature matrix (X) from dataframe"""
        return df[self.feature_names].values
    
    def get_target_vector(self, df):
        """Extract target vector (y) from dataframe"""
        return df['Target'].values


if __name__ == "__main__":
    # Test feature engineering
    logging.basicConfig(level=logging.INFO)
    
    from data_collector import HistoricalDataCollector
    
    print("Loading data...")
    collector = HistoricalDataCollector()
    data = collector.download_nq_data()
    
    print("\nCalculating features...")
    engineer = FeatureEngineer()
    data_with_features = engineer.calculate_all_features(data)
    
    print(f"\nFeature count: {len(engineer.feature_names)}")
    print(f"\nFeature names:")
    for i, name in enumerate(engineer.feature_names, 1):
        print(f"{i}. {name}")
    
    print("\nCreating target (Future Mean)...")
    data_with_target = engineer.create_target(data_with_features)
    
    print(f"\nFinal data shape: {data_with_target.shape}")
    print(f"\nSample data:")
    print(data_with_target[engineer.feature_names[-5:] + ['Target']].tail())
