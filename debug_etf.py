"""
Debug ETF Training - Step by Step
"""
import sys
sys.path.insert(0, 'backend')

from ml.data_collector import HistoricalDataCollector
from ml.feature_engineer import FeatureEngineer

print("="*60)
print("DEBUG: TQQQ Training")
print("="*60)

# Step 1: Download data
print("\n1. Downloading TQQQ data...")
collector = HistoricalDataCollector()
try:
    train_data, test_data = collector.get_data_for_training(symbol='TQQQ')
    print(f"   Train data: {len(train_data)} rows")
    print(f"   Test data: {len(test_data)} rows")
    print(f"   Interval: {(train_data.index[1] - train_data.index[0]).total_seconds() / 3600} hours")
except Exception as e:
    print(f"   ❌ ERROR: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# Step 2: Engineer features
print("\n2. Engineering features...")
engineer = FeatureEngineer()
try:
    train_features = engineer.calculate_all_features(train_data)
    print(f"   Features created: {len(train_features)} rows")
    print(f"   Feature count: {len(engineer.feature_names)}")
except Exception as e:
    print(f"   ❌ ERROR: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# Step 3: Create targets
print("\n3. Creating targets with auto-detection...")
try:
    train_with_target = engineer.create_target_auto(train_features, symbol='TQQQ')
    print(f"   Rows with target: {len(train_with_target)}")
    print(f"   Target distribution:")
    print(train_with_target['Target'].value_counts())
    
    if len(train_with_target) == 0:
        print("   ❌ PROBLEM: No rows with targets!")
    else:
        print("   ✅ Targets created successfully")
        
except Exception as e:
    print(f"   ❌ ERROR: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

print("\n" + "="*60)
print("DEBUG COMPLETE")
print("="*60)
