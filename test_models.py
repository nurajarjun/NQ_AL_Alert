import sys
sys.path.insert(0, '/app/backend')
from ml.xgboost_model import XGBoostPredictor

symbols = ['NQ', 'ES', 'TQQQ', 'SQQQ', 'SOXL', 'SOXS']
for sym in symbols:
    try:
        m = XGBoostPredictor(sym)
        print(f'{sym}: trained={m.is_trained}')
    except Exception as e:
        print(f'{sym}: ERROR - {e}')
