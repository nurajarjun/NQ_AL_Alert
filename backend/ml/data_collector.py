"""
Historical Data Collector
Downloads and manages NQ futures historical data
"""

import yfinance as yf
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import logging
import os
import pickle

logger = logging.getLogger(__name__)


class HistoricalDataCollector:
    """Collects and manages historical NQ futures data"""
    
    def __init__(self, data_dir="ml/data"):
        self.data_dir = data_dir
        os.makedirs(data_dir, exist_ok=True)
        self.cache_file = os.path.join(data_dir, "nq_historical.pkl")
    
    
    def download_nq_data(self, start_date=None, end_date=None, force_refresh=False, symbol="NQ"):
        """
        Download futures historical data
        """
        # Map common names to Yahoo Tickers
        ticker_map = {
            "NQ": "NQ=F",
            "ES": "ES=F",
            "SPY": "SPY",    # S&P 500 ETF (tradeable)
            "YM": "YM=F",
            "CL": "CL=F",
            "GC": "GC=F",
            "RTY": "RTY=F"
        }
        ticker = ticker_map.get(symbol.upper(), symbol) # Fallback to raw input if not found

        # Update cache filename to be symbol-specific
        cache_file = os.path.join(self.data_dir, f"{symbol.lower()}_historical.pkl")
        
        # Check cache first
        df_cache = None
        if os.path.exists(cache_file):
            try:
                with open(cache_file, 'rb') as f:
                    df_cache = pickle.load(f)
            except Exception:
                logger.warning(f"Failed to load cache for {symbol}, forcing fresh download.")
                
        # Smart Cache Logic: If cache exists and no force refresh, fetch delta
        if df_cache is not None and not force_refresh:
            try:
                last_timestamp = df_cache.index[-1]
                
                # Standardize timezones to UTC for robust comparison
                now_utc = pd.Timestamp.now(tz='UTC')
                
                # Ensure last_timestamp is UTC
                if last_timestamp.tzinfo is None:
                    last_timestamp = last_timestamp.tz_localize('UTC')
                else:
                    last_timestamp = last_timestamp.tz_convert('UTC')
                
                # Buffer period (2 days back to ensure continuity)
                delta_start = last_timestamp - timedelta(days=2)
                
                if delta_start < (now_utc - timedelta(days=720)):
                     delta_start = now_utc - timedelta(days=720)

                logger.info(f"🔄 Smart Cache: Fetching delta for {symbol} since {last_timestamp}...")
                
                # Use daily interval for ETFs (longer holding trades)
                etf_symbols = ['TQQQ', 'SQQQ', 'SOXL', 'SOXS']
                interval = "1d" if symbol.upper() in etf_symbols else "1h"
                
                df_new = yf.download(ticker, start=delta_start, end=end_date, interval=interval, progress=False)
                
                if df_new.empty:
                    logger.info("Smart Cache: No new data found. Returning cached.")
                    return df_cache
                
                # Cleanup new data columns
                df_new.columns = [col[0] if isinstance(col, tuple) else col for col in df_new.columns]
                
                # Filter strictly new data (avoid duplicates)
                # Ensure df_new index is also UTC
                if df_new.index.tz is None:
                    df_new.index = df_new.index.tz_localize('UTC')
                else:
                    df_new.index = df_new.index.tz_convert('UTC')
                    
                df_new = df_new[df_new.index > last_timestamp]
                
                if df_new.empty:
                    logger.info("Smart Cache: Up to date.")
                    return df_cache
                
                # Append new data
                logger.info(f"Smart Cache: Appending {len(df_new)} new candles.")
                df_combined = pd.concat([df_cache, df_new])
                
                # Save updated cache
                with open(cache_file, 'wb') as f:
                    pickle.dump(df_combined, f)
                    
                return df_combined
                
            except Exception as e:
                logger.error(f"Smart Update failed: {e}. Falling back to full download.")
                # Fall through to full download
        
        # FULL DOWNLOAD LOGIC (Fallback or Force Refresh)
        if end_date is None:
            end_date = datetime.now()
        if start_date is None:
            start_date = end_date - timedelta(days=720)
        
        logger.info(f"⬇️ Full Download {symbol} from {start_date} to {end_date}...")
        
        try:
            # Use daily interval for ETFs (longer holding trades)
            etf_symbols = ['TQQQ', 'SQQQ', 'SOXL', 'SOXS']
            interval = "1d" if symbol.upper() in etf_symbols else "1h"
            
            # Download VIX for Market Context (Fear/Volatility)
            try:
                logger.info("⬇️ Downloading VIX data for market context...")
                # VIX is an index, use ^VIX
                df_vix = yf.download("^VIX", start=start_date, end=end_date, interval="1h", progress=False)
                if not df_vix.empty:
                    # Clean VIX columns
                    df_vix.columns = [col[0] if isinstance(col, tuple) else col for col in df_vix.columns]
                    # Rename Close to VIX_Close to avoid collision
                    df_vix = df_vix[['Close']].rename(columns={'Close': 'VIX_Close'})
                    # Forward fill to handle missing VIX candles (it trades slightly different hours)
                    df_vix = df_vix.resample('1h').ffill()
            except Exception as e:
                logger.warning(f"Failed to download VIX data: {e}. Continuing without VIX.")
                df_vix = None

            df = yf.download(ticker, start=start_date, end=end_date, interval=interval, progress=False)

            if not df.empty:
                # Clean column names immediately
                df.columns = [col[0] if isinstance(col, tuple) else col for col in df.columns]

            if not df.empty and df_vix is not None:
                # Merge VIX data (left join to keep NQ index)
                # Ensure index types match (tz-naive vs tz-aware often an issue with yfinance)
                if df.index.tz is None and df_vix.index.tz is not None:
                    df.index = df.index.tz_localize(df_vix.index.tz)
                elif df.index.tz is not None and df_vix.index.tz is None:
                     df_vix.index = df_vix.index.tz_localize(df.index.tz)
                
                df = df.join(df_vix, how='left')
                # Fill missing VIX with previous value
                df['VIX_Close'] = df['VIX_Close'].ffill()
            
            if df.empty and symbol == "NQ":
                 df = yf.download("^NDX", start=start_date, end=end_date, interval="1h", progress=False)
                 if not df.empty:
                     df.columns = [col[0] if isinstance(col, tuple) else col for col in df.columns]
            
            if df.empty:
                raise ValueError(f"Failed to download data for {ticker}")
            
            # Remove any NaN rows
            
            # Remove any NaN rows
            df = df.dropna()
            
            logger.info(f"Downloaded {len(df)} candles")
            
            # Cache the data
            with open(cache_file, 'wb') as f:
                pickle.dump(df, f)
            
            return df
            
        except Exception as e:
            logger.error(f"Error downloading data: {e}")
            raise
    
    def get_recent_candles(self, n_candles=60, symbol="NQ"):
        """
        Get most recent N candles
        """
        data = self.download_nq_data(symbol=symbol)
        return data.tail(n_candles)
    
    def get_data_for_training(self, test_size=0.2, symbol="NQ"):
        """
        Get data split into training and testing sets
        
        Args:
            test_size: Fraction of data to use for testing
            
        Returns:
            train_data, test_data
        """
        data = self.download_nq_data(symbol=symbol)
        
        # Split by time (not random - important for time series!)
        split_idx = int(len(data) * (1 - test_size))
        
        train_data = data.iloc[:split_idx]
        test_data = data.iloc[split_idx:]
        
        logger.info(f"Training data: {len(train_data)} candles")
        logger.info(f"Testing data: {len(test_data)} candles")
        
        return train_data, test_data
    
    def save_data(self, data, filename):
        """Save data to file"""
        filepath = os.path.join(self.data_dir, filename)
        with open(filepath, 'wb') as f:
            pickle.dump(data, f)
        logger.info(f"Data saved to {filepath}")
    
    def load_data(self, filename):
        """Load data from file"""
        filepath = os.path.join(self.data_dir, filename)
        with open(filepath, 'rb') as f:
            data = pickle.load(f)
        logger.info(f"Data loaded from {filepath}")
        return data


if __name__ == "__main__":
    # Test the data collector
    logging.basicConfig(level=logging.INFO)
    
    collector = HistoricalDataCollector()
    
    print("Downloading NQ historical data...")
    data = collector.download_nq_data(force_refresh=True)
    
    print(f"\nData shape: {data.shape}")
    print(f"\nFirst few rows:")
    print(data.head())
    print(f"\nLast few rows:")
    print(data.tail())
    print(f"\nData info:")
    print(data.info())
