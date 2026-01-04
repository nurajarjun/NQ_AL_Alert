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
    
    def download_nq_data(self, start_date=None, end_date=None, force_refresh=False):
        """
        Download NQ futures historical data
        
        Args:
            start_date: Start date (default: 2 years ago)
            end_date: End date (default: today)
            force_refresh: Force re-download even if cached
            
        Returns:
            DataFrame with OHLCV data
        """
        # Check cache first
        if not force_refresh and os.path.exists(self.cache_file):
            logger.info("Loading cached historical data...")
            try:
                with open(self.cache_file, 'rb') as f:
                    data = pickle.load(f)
                logger.info(f"Loaded {len(data)} historical candles from cache")
                return data
            except Exception as e:
                logger.warning(f"Cache load failed: {e}, downloading fresh data")
        
        # Set default dates
        if end_date is None:
            end_date = datetime.now()
        if start_date is None:
            start_date = end_date - timedelta(days=720)  # 2 years (approx, safe for 1h data)
        
        logger.info(f"Downloading NQ data from {start_date} to {end_date}...")
        
        try:
            # Download NQ futures data
            # NQ=F is the ticker for Nasdaq-100 E-mini futures
            nq = yf.download("NQ=F", start=start_date, end=end_date, interval="1h")
            
            if nq.empty:
                logger.error("No data downloaded! Trying alternative ticker...")
                # Try alternative ticker
                nq = yf.download("^NDX", start=start_date, end=end_date, interval="1h")
            
            if nq.empty:
                raise ValueError("Failed to download data from both tickers")
            
            # Clean column names
            nq.columns = [col[0] if isinstance(col, tuple) else col for col in nq.columns]
            
            # Remove any NaN rows
            nq = nq.dropna()
            
            logger.info(f"Downloaded {len(nq)} candles")
            
            # Cache the data
            with open(self.cache_file, 'wb') as f:
                pickle.dump(nq, f)
            logger.info("Data cached successfully")
            
            return nq
            
        except Exception as e:
            logger.error(f"Error downloading data: {e}")
            raise
    
    def get_recent_candles(self, n_candles=60):
        """
        Get most recent N candles
        
        Args:
            n_candles: Number of recent candles to return
            
        Returns:
            DataFrame with recent candles
        """
        data = self.download_nq_data()
        return data.tail(n_candles)
    
    def get_data_for_training(self, test_size=0.2):
        """
        Get data split into training and testing sets
        
        Args:
            test_size: Fraction of data to use for testing
            
        Returns:
            train_data, test_data
        """
        data = self.download_nq_data()
        
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
