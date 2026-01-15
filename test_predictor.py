
import sys
import os
import pandas as pd
import logging

sys.path.append(os.path.abspath("backend"))

from ml.data_collector import HistoricalDataCollector
from ml.transformer_predictor import TransformerPredictor

logging.basicConfig(level=logging.INFO)

print("Loading data...")
collector = HistoricalDataCollector(data_dir=r"d:\Google\.gemini\antigravity\scratch\NQ-AI-Alerts\backend\ml\data")
data = collector.download_nq_data()

print("Initializing Predictor...")
predictor = TransformerPredictor()

print("Running Prediction...")
result = predictor.predict(data)

print("\n--- RESULT ---")
print(result)
