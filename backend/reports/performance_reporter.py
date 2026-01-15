"""
Daily Performance Report Generator
Tracks trades, calculates P&L, generates insights
"""
import json
import os
from datetime import datetime, timedelta
from pathlib import Path
import pandas as pd

class PerformanceReporter:
    def __init__(self):
        self.reports_dir = Path(__file__).parent.parent / "reports"
        self.reports_dir.mkdir(exist_ok=True)
        self.trades_file = self.reports_dir / "trades.json"
        
    def log_trade(self, trade_data):
        """Log a trade to the trades file"""
        trades = self._load_trades()
        
        trade_entry = {
            'timestamp': datetime.now().isoformat(),
            'symbol': trade_data.get('symbol'),
            'direction': trade_data.get('direction'),
            'entry': trade_data.get('entry'),
            'exit': trade_data.get('exit'),
            'pnl': trade_data.get('pnl'),
            'strategy': trade_data.get('strategy'),
            'confidence': trade_data.get('confidence')
        }
        
        trades.append(trade_entry)
        self._save_trades(trades)
        
    def generate_daily_report(self):
        """Generate daily performance report"""
        trades = self._load_trades()
        
        if not trades:
            return "No trades to report"
        
        # Filter today's trades
        today = datetime.now().date()
        today_trades = [t for t in trades if datetime.fromisoformat(t['timestamp']).date() == today]
        
        if not today_trades:
            return "No trades today"
        
        # Calculate metrics
        total_trades = len(today_trades)
        wins = [t for t in today_trades if t.get('pnl', 0) > 0]
        losses = [t for t in today_trades if t.get('pnl', 0) < 0]
        
        win_rate = len(wins) / total_trades * 100 if total_trades > 0 else 0
        total_pnl = sum(t.get('pnl', 0) for t in today_trades)
        avg_win = sum(t['pnl'] for t in wins) / len(wins) if wins else 0
        avg_loss = sum(t['pnl'] for t in losses) / len(losses) if losses else 0
        
        # Generate report
        report = f"""
# Daily Performance Report - {today.strftime('%Y-%m-%d')}

## Summary
- **Total Trades:** {total_trades}
- **Wins:** {len(wins)} ({win_rate:.1f}%)
- **Losses:** {len(losses)} ({100-win_rate:.1f}%)
- **Total P&L:** ${total_pnl:,.2f}

## Trade Breakdown
- **Average Win:** ${avg_win:,.2f}
- **Average Loss:** ${avg_loss:,.2f}
- **Win/Loss Ratio:** {abs(avg_win/avg_loss):.2f}:1 if avg_loss != 0 else 'N/A'

## By Symbol
"""
        # Group by symbol
        df = pd.DataFrame(today_trades)
        if not df.empty:
            symbol_stats = df.groupby('symbol').agg({
                'pnl': ['count', 'sum', 'mean']
            }).round(2)
            report += symbol_stats.to_string()
        
        report += f"\n\n## Insights\n"
        
        if win_rate >= 60:
            report += "✅ Excellent win rate! Strategy is working well.\n"
        elif win_rate >= 50:
            report += "✅ Good win rate. Continue monitoring.\n"
        else:
            report += "⚠️ Win rate below 50%. Review strategy parameters.\n"
        
        if total_pnl > 0:
            report += f"✅ Profitable day: +${total_pnl:,.2f}\n"
        else:
            report += f"❌ Losing day: ${total_pnl:,.2f}\n"
        
        # Save report
        report_file = self.reports_dir / f"daily_report_{today.strftime('%Y%m%d')}.md"
        with open(report_file, 'w') as f:
            f.write(report)
        
        return report
    
    def _load_trades(self):
        """Load trades from JSON file"""
        if not self.trades_file.exists():
            return []
        
        try:
            with open(self.trades_file, 'r') as f:
                return json.load(f)
        except:
            return []
    
    def _save_trades(self, trades):
        """Save trades to JSON file"""
        with open(self.trades_file, 'w') as f:
            json.dump(trades, f, indent=2)

if __name__ == "__main__":
    # Test
    reporter = PerformanceReporter()
    
    # Simulate some trades
    test_trades = [
        {'symbol': 'NQ', 'direction': 'LONG', 'entry': 21500, 'exit': 21550, 'pnl': 1000, 'strategy': 'Breakout', 'confidence': 'HIGH'},
        {'symbol': 'ES', 'direction': 'SHORT', 'entry': 5800, 'exit': 5790, 'pnl': 500, 'strategy': 'Mean Reversion', 'confidence': 'MEDIUM'},
        {'symbol': 'NQ', 'direction': 'LONG', 'entry': 21550, 'exit': 21540, 'pnl': -200, 'strategy': 'Momentum', 'confidence': 'MEDIUM'}
    ]
    
    for trade in test_trades:
        reporter.log_trade(trade)
    
    print(reporter.generate_daily_report())
