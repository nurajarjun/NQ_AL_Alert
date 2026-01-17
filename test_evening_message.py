"""
Quick test to verify evening scalper Telegram message formatting
"""

# Mock signal data (same structure as evening_scalper.py returns)
mock_signal = {
    'pair': 'Nasdaq Futures',
    'strategy': '🚀 Breakout Long',
    'signal': 'LONG',
    'confidence': 'HIGH',
    'entry': 16850.50,
    'stop': 16820.00,
    'target1': 16920.00,
    'target2': 16980.00,
    'rr_ratio1': 2.3,
    'rr_ratio2': 4.3,
    'risk_dollars': 150,
    'reward1_dollars': 350,
    'reward2_dollars': 650,
    'adx': 28.5,
    'rsi': 62.3,
    'in_session': True
}

# Test the exact message formatting from main.py (lines 912-930)
if mock_signal.get('in_session', False):
    msg = f"🌙 **EVENING SCALP** | {mock_signal['pair']}\n\n"
    msg += f"📊 **{mock_signal['strategy']}**\n"
    msg += f"Signal: **{mock_signal['signal']}** | Conf: {mock_signal['confidence']}\n\n"
    
    # Entry and Levels
    msg += f"💰 **Trade Setup:**\n"
    msg += f"Entry: {mock_signal['entry']:.2f}\n"
    msg += f"Stop: {mock_signal['stop']:.2f}\n"
    msg += f"Target 1: {mock_signal['target1']:.2f} (R/R: {mock_signal['rr_ratio1']}:1)\n"
    msg += f"Target 2: {mock_signal['target2']:.2f} (R/R: {mock_signal['rr_ratio2']}:1)\n\n"
    
    # Risk/Reward in Dollars
    msg += f"💵 **Risk/Reward:**\n"
    msg += f"Risk: ${mock_signal['risk_dollars']:.0f}\n"
    msg += f"Reward 1: ${mock_signal['reward1_dollars']:.0f}\n"
    msg += f"Reward 2: ${mock_signal['reward2_dollars']:.0f}\n\n"
    
    # Technical Stats
    msg += f"📈 **Stats:** ADX={mock_signal['adx']:.1f} | RSI={mock_signal['rsi']:.1f}"
    
    print("="*60)
    print("TELEGRAM MESSAGE PREVIEW:")
    print("="*60)
    print(msg)
    print("="*60)
    print("\n✅ Message formatting test PASSED - No KeyError")
else:
    print("❌ Not in session")
