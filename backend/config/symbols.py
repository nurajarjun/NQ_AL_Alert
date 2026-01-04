"""
Symbol Configuration
Defines settings for each supported symbol with automatic asset type detection
"""

SYMBOL_CONFIG = {
    # ===== FUTURES =====
    'NQ': {
        'name': 'Nasdaq-100 Futures',
        'type': 'futures',
        'asset_class': 'index_futures',
        'leverage': 1,
        'point_value': 20,
        'tick_size': 0.25,
        'correlation_symbol': 'QQQ',
        'sector': 'tech',
        'inverse': False,
        'position_multiplier': 1.0,
        'stop_multiplier': 1.0,
        'emoji': '📈',
        'description': 'E-mini Nasdaq-100 Futures',
        'trading_hours': '23/6 (Sun 6PM - Fri 5PM ET)',
        'margin_requirement': '$13,200'
    },
    'ES': {
        'name': 'S&P 500 Futures',
        'type': 'futures',
        'asset_class': 'index_futures',
        'leverage': 1,
        'point_value': 50,
        'tick_size': 0.25,
        'correlation_symbol': 'SPY',
        'sector': 'broad_market',
        'inverse': False,
        'position_multiplier': 1.0,
        'stop_multiplier': 1.0,
        'emoji': '📊',
        'description': 'E-mini S&P 500 Futures',
        'trading_hours': '23/6 (Sun 6PM - Fri 5PM ET)',
        'margin_requirement': '$12,650'
    },
    'YM': {
        'name': 'Dow Jones Futures',
        'type': 'futures',
        'asset_class': 'index_futures',
        'leverage': 1,
        'point_value': 5,
        'tick_size': 1.0,
        'correlation_symbol': 'DIA',
        'sector': 'blue_chip',
        'inverse': False,
        'position_multiplier': 1.0,
        'stop_multiplier': 1.0,
        'emoji': '🏭',
        'description': 'E-mini Dow Jones Futures',
        'trading_hours': '23/6 (Sun 6PM - Fri 5PM ET)',
        'margin_requirement': '$9,900'
    },
    'RTY': {
        'name': 'Russell 2000 Futures',
        'type': 'futures',
        'asset_class': 'index_futures',
        'leverage': 1,
        'point_value': 50,
        'tick_size': 0.10,
        'correlation_symbol': 'IWM',
        'sector': 'small_cap',
        'inverse': False,
        'position_multiplier': 1.0,
        'stop_multiplier': 1.0,
        'emoji': '🏢',
        'description': 'E-mini Russell 2000 Futures',
        'trading_hours': '23/6 (Sun 6PM - Fri 5PM ET)',
        'margin_requirement': '$5,500'
    },
    
    # ===== LEVERAGED ETFs =====
    'TQQQ': {
        'name': 'ProShares UltraPro QQQ',
        'type': 'etf',
        'asset_class': 'leveraged_etf',
        'leverage': 3,
        'point_value': 1,
        'tick_size': 0.01,
        'correlation_symbol': 'QQQ',
        'sector': 'tech',
        'inverse': False,
        'position_multiplier': 0.33,
        'stop_multiplier': 3.0,
        'emoji': '🚀',
        'description': '3x Leveraged QQQ ETF',
        'trading_hours': '9:30 AM - 4:00 PM ET',
        'warning': '⚠️ 3x LEVERAGED - Use 1/3 position size!'
    },
    'SQQQ': {
        'name': 'ProShares UltraPro Short QQQ',
        'type': 'etf',
        'asset_class': 'inverse_etf',
        'leverage': 3,
        'point_value': 1,
        'tick_size': 0.01,
        'correlation_symbol': 'QQQ',
        'sector': 'tech',
        'inverse': True,
        'position_multiplier': 0.33,
        'stop_multiplier': 3.0,
        'emoji': '📉',
        'description': '3x Inverse QQQ ETF',
        'trading_hours': '9:30 AM - 4:00 PM ET',
        'warning': '⚠️ INVERSE 3x LEVERAGED - Profits when QQQ falls!'
    },
    'SOXL': {
        'name': 'Direxion Daily Semiconductor Bull 3X',
        'type': 'etf',
        'asset_class': 'leveraged_etf',
        'leverage': 3,
        'point_value': 1,
        'tick_size': 0.01,
        'correlation_symbol': 'SOXX',
        'sector': 'semiconductors',
        'inverse': False,
        'position_multiplier': 0.33,
        'stop_multiplier': 3.0,
        'emoji': '💻',
        'description': '3x Leveraged Semiconductor ETF',
        'trading_hours': '9:30 AM - 4:00 PM ET',
        'warning': '⚠️ 3x LEVERAGED - Semiconductor sector only!',
        'key_stocks': ['NVDA', 'AMD', 'INTC', 'TSM']
    },
    'SOXS': {
        'name': 'Direxion Daily Semiconductor Bear 3X',
        'type': 'etf',
        'asset_class': 'inverse_etf',
        'leverage': 3,
        'point_value': 1,
        'tick_size': 0.01,
        'correlation_symbol': 'SOXX',
        'sector': 'semiconductors',
        'inverse': True,
        'position_multiplier': 0.33,
        'stop_multiplier': 3.0,
        'emoji': '🔻',
        'description': '3x Inverse Semiconductor ETF',
        'trading_hours': '9:30 AM - 4:00 PM ET',
        'warning': '⚠️ INVERSE 3x LEVERAGED - Profits when semiconductors fall!',
        'key_stocks': ['NVDA', 'AMD', 'INTC', 'TSM']
    },
    
    # ===== REGULAR ETFs =====
    'SPY': {
        'name': 'SPDR S&P 500 ETF',
        'type': 'etf',
        'asset_class': 'index_etf',
        'leverage': 1,
        'point_value': 1,
        'tick_size': 0.01,
        'correlation_symbol': 'ES',
        'sector': 'broad_market',
        'inverse': False,
        'position_multiplier': 1.0,
        'stop_multiplier': 1.0,
        'emoji': '📈',
        'description': 'S&P 500 ETF',
        'trading_hours': '9:30 AM - 4:00 PM ET'
    },
    'QQQ': {
        'name': 'Invesco QQQ Trust',
        'type': 'etf',
        'asset_class': 'index_etf',
        'leverage': 1,
        'point_value': 1,
        'tick_size': 0.01,
        'correlation_symbol': 'NQ',
        'sector': 'tech',
        'inverse': False,
        'position_multiplier': 1.0,
        'stop_multiplier': 1.0,
        'emoji': '💻',
        'description': 'Nasdaq-100 ETF',
        'trading_hours': '9:30 AM - 4:00 PM ET'
    },
    
    # ===== STOCKS (Examples) =====
    'AAPL': {
        'name': 'Apple Inc.',
        'type': 'stock',
        'asset_class': 'mega_cap_tech',
        'leverage': 1,
        'point_value': 1,
        'tick_size': 0.01,
        'correlation_symbol': 'QQQ',
        'sector': 'tech',
        'inverse': False,
        'position_multiplier': 1.0,
        'stop_multiplier': 1.0,
        'emoji': '🍎',
        'description': 'Apple Stock',
        'trading_hours': '9:30 AM - 4:00 PM ET'
    },
    'TSLA': {
        'name': 'Tesla Inc.',
        'type': 'stock',
        'asset_class': 'growth_stock',
        'leverage': 1,
        'point_value': 1,
        'tick_size': 0.01,
        'correlation_symbol': 'QQQ',
        'sector': 'automotive_tech',
        'inverse': False,
        'position_multiplier': 1.0,
        'stop_multiplier': 1.0,
        'emoji': '🚗',
        'description': 'Tesla Stock',
        'trading_hours': '9:30 AM - 4:00 PM ET'
    }
}


def get_symbol_config(symbol: str) -> dict:
    """Get configuration for a symbol"""
    symbol = symbol.upper()
    return SYMBOL_CONFIG.get(symbol, SYMBOL_CONFIG['NQ'])


def detect_asset_type(symbol: str) -> str:
    """
    Automatically detect asset type from symbol
    
    Returns:
        'futures', 'etf', 'stock', or 'unknown'
    """
    symbol = symbol.upper()
    
    # Check if in config
    if symbol in SYMBOL_CONFIG:
        return SYMBOL_CONFIG[symbol]['type']
    
    # Auto-detect from symbol pattern
    # Futures typically: ES, NQ, YM, RTY, CL, GC, etc.
    if len(symbol) <= 3 and symbol.isalpha():
        # Could be futures or ETF
        # Common futures: ES, NQ, YM, RTY, CL, GC, SI, ZB, ZN
        futures_symbols = ['ES', 'NQ', 'YM', 'RTY', 'CL', 'GC', 'SI', 'ZB', 'ZN', 'ZC', 'ZW']
        if symbol in futures_symbols:
            return 'futures'
        # Otherwise likely ETF
        return 'etf'
    
    # Stocks typically have 1-5 letters
    if 1 <= len(symbol) <= 5 and symbol.isalpha():
        return 'stock'
    
    return 'unknown'


def is_futures(symbol: str) -> bool:
    """Check if symbol is a futures contract"""
    return detect_asset_type(symbol) == 'futures'


def is_etf(symbol: str) -> bool:
    """Check if symbol is an ETF"""
    return detect_asset_type(symbol) == 'etf'


def is_stock(symbol: str) -> bool:
    """Check if symbol is a stock"""
    return detect_asset_type(symbol) == 'stock'


def is_inverse_symbol(symbol: str) -> bool:
    """Check if symbol is inverse"""
    config = get_symbol_config(symbol)
    return config.get('inverse', False)


def get_position_multiplier(symbol: str) -> float:
    """Get position size multiplier for symbol"""
    config = get_symbol_config(symbol)
    return config.get('position_multiplier', 1.0)


def get_stop_multiplier(symbol: str) -> float:
    """Get stop loss multiplier for symbol"""
    config = get_symbol_config(symbol)
    return config.get('stop_multiplier', 1.0)


def flip_direction_if_inverse(symbol: str, direction: str) -> str:
    """Flip direction if symbol is inverse"""
    if is_inverse_symbol(symbol):
        return 'SHORT' if direction == 'LONG' else 'LONG'
    return direction


def get_symbol_warning(symbol: str) -> str:
    """Get warning message for symbol"""
    config = get_symbol_config(symbol)
    return config.get('warning', '')


def format_symbol_header(symbol: str, direction: str) -> str:
    """Format alert header for symbol"""
    config = get_symbol_config(symbol)
    emoji = config.get('emoji', '📊')
    name = config.get('name', symbol)
    asset_type = config.get('type', 'unknown').upper()
    
    # Flip direction if inverse
    display_direction = flip_direction_if_inverse(symbol, direction)
    
    return f"{emoji} {symbol} {display_direction} ({asset_type})"


def get_all_symbols_by_type() -> dict:
    """Get all symbols grouped by type"""
    by_type = {
        'futures': [],
        'etf': [],
        'stock': []
    }
    
    for symbol, config in SYMBOL_CONFIG.items():
        asset_type = config['type']
        by_type[asset_type].append(symbol)
    
    return by_type


if __name__ == "__main__":
    # Test symbol detection
    print("="*60)
    print("SYMBOL DETECTION TEST")
    print("="*60)
    
    test_symbols = ['NQ', 'ES', 'TQQQ', 'SPY', 'AAPL', 'TSLA', 'SQQQ', 'YM']
    
    for symbol in test_symbols:
        config = get_symbol_config(symbol)
        asset_type = detect_asset_type(symbol)
        
        print(f"\n{symbol}:")
        print(f"  Type: {asset_type}")
        print(f"  Asset Class: {config.get('asset_class', 'N/A')}")
        print(f"  Leverage: {config['leverage']}x")
        print(f"  Inverse: {config['inverse']}")
        print(f"  Point Value: ${config['point_value']}")
        if 'trading_hours' in config:
            print(f"  Hours: {config['trading_hours']}")
    
    print("\n" + "="*60)
    print("SYMBOLS BY TYPE")
    print("="*60)
    
    by_type = get_all_symbols_by_type()
    for asset_type, symbols in by_type.items():
        print(f"\n{asset_type.upper()}: {', '.join(symbols)}")
    
    print("\n" + "="*60)
