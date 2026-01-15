
import sys
import os
import itertools
import pandas as pd
import logging
from concurrent.futures import ThreadPoolExecutor

# Path setup
sys.path.append(os.getcwd())
try:
    from backend.backtest import Backtester
except ImportError:
    sys.path.append(os.path.join(os.getcwd(), 'backend'))
    from backend.backtest import Backtester

# Suppress logs during optimization
logging.getLogger("BACKTEST").setLevel(logging.ERROR)

def run_sim(params):
    try:
        bt = Backtester(days=60, config=params)
        bt.run(verbose=False)
        stats = bt.stats
        stats.update(params) # Add params to result
        return stats
    except Exception as e:
        return None

def main():
    print("🚀 Starting Grid Search Optimization (Target: >80% Win Rate)...")
    
    # Define Parameter Grid (5m SCALPING)
    # We test Low Reward:Risk ratios to maximize Win Rate
    # RSI: Broader range
    rsi_shorts = [65, 70, 75, 80]
    rsi_longs = [20, 25, 30, 35]
    stop_mults = [1.0, 1.5, 2.0] # Tighter stops
    t1_ratios = [0.5, 0.75, 1.0, 1.5] # Reward < Risk allowed for High WR
    
    combinations = list(itertools.product(rsi_shorts, rsi_longs, stop_mults, t1_ratios))
    print(f"Testing {len(combinations)} combinations...")
    
    results = []
    
    # Run loop (Sequential for safety, or simple loop)
    # Using simple loop to avoid complex threading issues with pandas/cache
    for i, (rs, rl, sm, t1) in enumerate(combinations):
        if i % 20 == 0: sum_char = "."
        
        params = {
            'rsi_short': rs,
            'rsi_long': rl,
            'atr_stop_mult': sm,
            'target1_ratio': t1,
            'target2_ratio': t1 * 2  # T2 is usually 2x T1 (or fixed)
        }
        
        res = run_sim(params)
        if res and res['trades'] > 10: # Min 10 trades to be statistically relevant
            results.append(res)
            
        print(".", end="", flush=True)

    print("\n\n✅ Optimization Complete.")
    
    if not results:
        print("No valid results found.")
        return

    df = pd.DataFrame(results)
    
    # Sort by Win Rate
    df_wr = df.sort_values(by='win_rate', ascending=False).head(10)
    
    csv_path = os.path.join(os.getcwd(), 'backend', 'optimization_results.csv')
    df.to_csv(csv_path, index=False) # Save ALL results for analysis
    print(f"Results saved to {csv_path}")
    
    print("\nTOP 10 CONFIGS BY WIN RATE:")
    print("="*60)
    print(df_wr[['win_rate', 'pnl', 'trades', 'rsi_short', 'rsi_long', 'atr_stop_mult', 'target1_ratio']].to_string(index=False))
    print("="*60)
    
    # Sort by PnL
    df_pnl = df.sort_values(by='pnl', ascending=False).head(5)
    print("\n💰 TOP 5 CONFIGS BY PNL:")
    print(df_pnl[['win_rate', 'pnl', 'trades', 'rsi_short', 'rsi_long', 'atr_stop_mult', 'target1_ratio']].to_string(index=False))

if __name__ == "__main__":
    main()
