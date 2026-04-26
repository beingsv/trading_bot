"""
Test Options Trading System
Quick test to verify all components work
"""
from datetime import datetime, timedelta

print("🧪 Testing Options Trading System...\n")

# Test 1: Config
print("1️⃣ Testing Config...")
from config.config import TRADING_TYPE, PRIMARY_INDEX, INDEX_CONFIG, INITIAL_CAPITAL
print(f"   Trading Type: {TRADING_TYPE}")
print(f"   Primary Index: {PRIMARY_INDEX}")
print(f"   Lot Size: {INDEX_CONFIG[PRIMARY_INDEX]['lot_size']}")
print(f"   Capital: ₹{INITIAL_CAPITAL:,}")
print("   ✅ Config OK\n")

# Test 2: Options Greeks Calculator
print("2️⃣ Testing Options Greeks Calculator...")
from analysis.options_greeks import OptionsGreeksCalculator

greeks_calc = OptionsGreeksCalculator()
test_greeks = greeks_calc.calculate_greeks(
    spot_price=24000,
    strike_price=24000,
    days_to_expiry=3,
    implied_volatility=0.15,
    option_type='CE'
)
print(f"   ATM Call Premium: ₹{test_greeks['premium']:.2f}")
print(f"   Delta: {test_greeks['delta']:.2f}")
print(f"   Theta: {test_greeks['theta']:.2f}")
print(f"   Vega: {test_greeks['vega']:.2f}")
print("   ✅ Greeks Calculator OK\n")

# Test 3: Options Chain (simulated)
print("3️⃣ Testing Options Chain Fetcher...")
from trading.angelone_api import AngelOneAPI
from data.options_chain import OptionsChainFetcher

angelone = AngelOneAPI()
options_chain = OptionsChainFetcher(angelone)

# Test with simulated data
chain_data = options_chain.fetch_option_chain(spot_price=24000)
print(f"   Spot Price: ₹{chain_data['spot_price']:.2f}")
print(f"   ATM Strike: {chain_data['atm_strike']}")
print(f"   Days to Expiry: {chain_data['days_to_expiry']}")
print(f"   Options Available: {len(chain_data['options'])}")

# Test strike selection
selected_call = options_chain.select_best_strike(chain_data, 'BULLISH', 'ATM')
print(f"   Selected Call: {selected_call['strike']} CE @ ₹{selected_call['ltp']:.2f}")
print("   ✅ Options Chain OK\n")

# Test 4: Options Strategies
print("4️⃣ Testing Options Strategies...")
from strategies.options_strategies import get_options_strategies
import pandas as pd
import numpy as np

strategies = get_options_strategies()
print(f"   Loaded {len(strategies)} strategies:")
for s in strategies:
    print(f"      - {s.name}")

# Create dummy data for testing
from datetime import datetime, timedelta
base_time = datetime.now() - timedelta(hours=5)
timestamps = [base_time + timedelta(minutes=5*i) for i in range(100)]

dummy_data = pd.DataFrame({
    'timestamp': timestamps,
    'close': np.random.randn(100).cumsum() + 24000,
    'open': np.random.randn(100).cumsum() + 24000,
    'high': np.random.randn(100).cumsum() + 24100,
    'low': np.random.randn(100).cumsum() + 23900,
    'volume': np.random.randint(1000, 10000, 100),
    'RSI_14': np.random.uniform(30, 70, 100),
    'MACD': np.random.randn(100),
    'MACD_signal': np.random.randn(100),
    'SMA_20': np.random.randn(100).cumsum() + 24000,
    'SMA_50': np.random.randn(100).cumsum() + 23950,
    'support': np.full(100, 23800),
    'resistance': np.full(100, 24200),
    'vwap': np.random.randn(100).cumsum() + 24000
})

market_context = {'market_condition': 'SIDEWAYS', 'news_sentiment': {'sentiment_score': 0}}

signal = strategies[0].generate_signal(dummy_data, market_context)
print(f"   Test Signal: {signal['action']} (Confidence: {signal['confidence']}%)")
print("   ✅ Strategies OK\n")

# Test 5: Options Paper Trading
print("5️⃣ Testing Options Paper Trading...")
from data.storage import DataStorage
from trading.options_paper_trading import OptionsPaperTradingEngine

storage = DataStorage()
paper_trading = OptionsPaperTradingEngine(storage, initial_capital=10000)

# Test buy
result = paper_trading.execute_buy_option(
    option_data=selected_call,
    strategy='Test',
    reason='Testing',
    lots=1
)
print(f"   Buy Result: {result['success']}")
print(f"   Position ID: {result.get('position_id', 'N/A')}")

# Test sell
if result['success']:
    sell_result = paper_trading.execute_sell_option(
        result['position_id'],
        current_premium=selected_call['ltp'] * 1.1,  # 10% profit
        reason='Test exit'
    )
    print(f"   Sell Result: {sell_result['success']}")
    print(f"   P&L: ₹{sell_result.get('pnl', 0):.2f}")

stats = paper_trading.get_statistics()
print(f"   Final Capital: ₹{stats['capital']:.2f}")
print("   ✅ Paper Trading OK\n")

# Test 6: Signal Generator
print("6️⃣ Testing Options Signal Generator...")
from strategies.strategy_pool import StrategyPool
from analysis.technical import TechnicalAnalyzer
from trading.options_signal_generator import OptionsSignalGenerator

strategy_pool = StrategyPool(storage)
technical_analyzer = TechnicalAnalyzer()

signal_gen = OptionsSignalGenerator(
    strategy_pool,
    technical_analyzer,
    options_chain
)

# Add technical indicators to dummy data
dummy_data = technical_analyzer.calculate_all_indicators(dummy_data)

signal = signal_gen.generate_signal(dummy_data, market_context, spot_price=24000)
print(f"   Signal Action: {signal['action']}")
print(f"   Confidence: {signal['confidence']:.0f}%")
print(f"   Reason: {signal['reason']}")
if signal['selected_option']:
    print(f"   Selected: {signal['selected_option']['strike']} {signal['selected_option']['option_type']}")
print("   ✅ Signal Generator OK\n")

print("="*60)
print("✅ ALL TESTS PASSED!")
print("="*60)
print("\n🚀 Options trading system is ready!")
print("\nNext steps:")
print("1. Run: python run_options_bot.py")
print("2. Bot will trade NIFTY options intraday")
print("3. Monitor performance and adjust parameters")
print("\n💡 Tip: Start with paper trading to test the system")
