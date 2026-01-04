"""
Feature Engineer
Calculates technical indicators and creates ML features
"""

import pandas as pd
import numpy as np
import logging

logger = logging.getLogger(__name__)


class FeatureEngineer:
    """Creates features for machine learning models"""
    
    def __init__(self):
        self.feature_names = []
    
    def calculate_all_features(self, df):
        """
        Calculate all technical indicators and features
        
        Args:
            df: DataFrame with OHLCV data
            
        Returns:
            DataFrame with all features added
        """
        logger.info("Calculating features...")
        
        df = df.copy()
        
        # Price-based features
        df = self._add_price_features(df)
        
        # Trend indicators
        df = self._add_trend_indicators(df)
        
        # Momentum indicators
        df = self._add_momentum_indicators(df)
        
        # Volatility indicators
        df = self._add_volatility_indicators(df)
        
        # Volume indicators
        df = self._add_volume_indicators(df)
        
        # Pattern features
        df = self._add_pattern_features(df)
        
        # Time-based features
        df = self._add_time_features(df)
        
        # Remove NaN rows (from indicator calculations)
        initial_len = len(df)
        df = df.dropna()
        logger.info(f"Removed {initial_len - len(df)} rows with NaN values")
        
        # Store feature names
        self.feature_names = [col for col in df.columns if col not in ['Open', 'High', 'Low', 'Close', 'Volume']]
        
        logger.info(f"Created {len(self.feature_names)} features")
        
        return df
    
    def _add_price_features(self, df):
        """Add price-based features"""
        df['Price_Change'] = df['Close'].pct_change()
        df['Price_Range'] = (df['High'] - df['Low']) / df['Close']
        df['Body_Size'] = abs(df['Close'] - df['Open']) / df['Close']
        df['Upper_Shadow'] = (df['High'] - df[['Open', 'Close']].max(axis=1)) / df['Close']
        df['Lower_Shadow'] = (df[['Open', 'Close']].min(axis=1) - df['Low']) / df['Close']
        
        return df
    
    def _add_trend_indicators(self, df):
        """Add trend indicators"""
        # Simple Moving Averages
        df['SMA_10'] = df['Close'].rolling(10).mean()
        df['SMA_20'] = df['Close'].rolling(20).mean()
        df['SMA_50'] = df['Close'].rolling(50).mean()
        
        # Exponential Moving Averages
        df['EMA_12'] = df['Close'].ewm(span=12).mean()
        df['EMA_26'] = df['Close'].ewm(span=26).mean()
        
        # Price relative to MAs
        df['Price_vs_SMA20'] = (df['Close'] - df['SMA_20']) / df['SMA_20']
        df['Price_vs_SMA50'] = (df['Close'] - df['SMA_50']) / df['SMA_50']
        
        # MA crossovers
        df['SMA_10_20_Cross'] = (df['SMA_10'] > df['SMA_20']).astype(int)
        df['EMA_12_26_Cross'] = (df['EMA_12'] > df['EMA_26']).astype(int)
        
        return df
    
    def _add_momentum_indicators(self, df):
        """Add momentum indicators"""
        # RSI
        df['RSI'] = self._calculate_rsi(df['Close'])
        
        # MACD
        df['MACD'] = df['EMA_12'] - df['EMA_26']
        df['MACD_Signal'] = df['MACD'].ewm(span=9).mean()
        df['MACD_Hist'] = df['MACD'] - df['MACD_Signal']
        
        # Rate of Change
        df['ROC_10'] = df['Close'].pct_change(10)
        df['ROC_20'] = df['Close'].pct_change(20)
        
        # Momentum
        df['Momentum_10'] = df['Close'] - df['Close'].shift(10)
        
        return df
    
    def _add_volatility_indicators(self, df):
        """Add volatility indicators"""
        # ATR (Average True Range)
        df['ATR'] = self._calculate_atr(df)
        df['ATR_Pct'] = df['ATR'] / df['Close']
        
        # Bollinger Bands
        df['BB_Middle'] = df['Close'].rolling(20).mean()
        bb_std = df['Close'].rolling(20).std()
        df['BB_Upper'] = df['BB_Middle'] + (bb_std * 2)
        df['BB_Lower'] = df['BB_Middle'] - (bb_std * 2)
        df['BB_Width'] = (df['BB_Upper'] - df['BB_Lower']) / df['BB_Middle']
        df['BB_Position'] = (df['Close'] - df['BB_Lower']) / (df['BB_Upper'] - df['BB_Lower'])
        
        # Historical Volatility
        df['Volatility_10'] = df['Price_Change'].rolling(10).std()
        df['Volatility_20'] = df['Price_Change'].rolling(20).std()
        
        return df
    
    def _add_volume_indicators(self, df):
        """Add volume indicators"""
        # Volume moving averages
        df['Volume_SMA_20'] = df['Volume'].rolling(20).mean()
        df['Volume_Ratio'] = df['Volume'] / df['Volume_SMA_20']
        
        # On-Balance Volume (OBV)
        df['OBV'] = (np.sign(df['Close'].diff()) * df['Volume']).fillna(0).cumsum()
        df['OBV_SMA'] = df['OBV'].rolling(20).mean()
        
        # Volume Price Trend
        df['VPT'] = (df['Volume'] * df['Price_Change']).cumsum()
        
        return df
    
    def _add_pattern_features(self, df):
        """Add pattern recognition features"""
        # Higher highs / Lower lows
        df['Higher_High'] = (df['High'] > df['High'].shift(1)).astype(int)
        df['Lower_Low'] = (df['Low'] < df['Low'].shift(1)).astype(int)
        
        # Trend strength
        df['Uptrend_Strength'] = df['Higher_High'].rolling(10).sum()
        df['Downtrend_Strength'] = df['Lower_Low'].rolling(10).sum()
        
        # Gap detection
        df['Gap_Up'] = ((df['Low'] > df['High'].shift(1)).astype(int))
        df['Gap_Down'] = ((df['High'] < df['Low'].shift(1)).astype(int))
        
        return df
    
    def _add_time_features(self, df):
        """Add time-based features"""
        # Extract time components
        df['Hour'] = df.index.hour
        df['DayOfWeek'] = df.index.dayofweek
        df['DayOfMonth'] = df.index.day
        df['Month'] = df.index.month
        
        # Trading session
        df['Is_Morning'] = ((df['Hour'] >= 9) & (df['Hour'] <= 11)).astype(int)
        df['Is_Afternoon'] = ((df['Hour'] >= 14) & (df['Hour'] <= 16)).astype(int)
        df['Is_Lunch'] = ((df['Hour'] >= 11) & (df['Hour'] <= 14)).astype(int)
        
        return df
    
    def _calculate_rsi(self, prices, period=14):
        """Calculate RSI indicator"""
        delta = prices.diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
        
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))
        
        return rsi
    
    def _calculate_atr(self, df, period=14):
        """Calculate Average True Range"""
        high_low = df['High'] - df['Low']
        high_close = abs(df['High'] - df['Close'].shift())
        low_close = abs(df['Low'] - df['Close'].shift())
        
        true_range = pd.concat([high_low, high_close, low_close], axis=1).max(axis=1)
        atr = true_range.rolling(period).mean()
        
        return atr
    
    def create_target(self, df, lookahead=4):
        """
        Create target variable for training
        
        Args:
            df: DataFrame with features
            lookahead: How many periods ahead to look
            
        Returns:
            DataFrame with 'Target' column (0=DOWN, 1=SIDEWAYS, 2=UP)
        """
        df = df.copy()
        
        # Calculate future return
        future_return = df['Close'].shift(-lookahead) / df['Close'] - 1
        
        # Classify into 3 categories
        # UP if return > 0.3%, DOWN if < -0.3%, else SIDEWAYS
        # Remove rows where we don't have future data
        df = df[:-lookahead].copy()
        future_return = future_return[:-lookahead]
        
        # Classify into 3 categories
        # UP if return > 0.3%, DOWN if < -0.3%, else SIDEWAYS
        df['Target'] = pd.cut(
            future_return,
            bins=[-np.inf, -0.003, 0.003, np.inf],
            labels=[0, 1, 2]  # DOWN, SIDEWAYS, UP
        ).astype(int)
        
        logger.info(f"Target distribution:\n{df['Target'].value_counts()}")
        
        return df
    
    def get_feature_matrix(self, df):
        """
        Get feature matrix (X) for ML models
        
        Args:
            df: DataFrame with all features
            
        Returns:
            Feature matrix as numpy array
        """
        return df[self.feature_names].values
    
    def get_target_vector(self, df):
        """
        Get target vector (y) for ML models
        
        Args:
            df: DataFrame with Target column
            
        Returns:
            Target vector as numpy array
        """
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
    
    print("\nCreating target...")
    data_with_target = engineer.create_target(data_with_features)
    
    print(f"\nFinal data shape: {data_with_target.shape}")
    print(f"\nSample data:")
    print(data_with_target[engineer.feature_names + ['Target']].tail())
