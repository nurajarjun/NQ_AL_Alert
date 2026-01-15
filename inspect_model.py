
import joblib
import sys

try:
    data = joblib.load('/app/ml/models/xgboost_model_NQ.pkl')
    print(f"Root data type: {type(data)}")
    
    if isinstance(data, dict):
        print(f"Keys: {list(data.keys())}")
        if 'model' in data:
            model_val = data['model']
            print(f"data['model'] type: {type(model_val)}")
            if isinstance(model_val, dict):
                print(f"data['model'] keys: {list(model_val.keys())}")
            else:
                print(f"data['model'] content: {model_val}")
    else:
        print("Root data is not a dict")

except Exception as e:
    print(f"Error: {e}")
