"""
Backtest and Train Bot on Historical Data
Fetches real historical data from AngelOne and simulates trades
"""
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import time

from config.config import WATCHLIST
from data.storage import DataStorage
from analysis.technical import TechnicalAnalyzer
from analysis.news_sentiment import NewsSentimentAnalyzer
from strategies.strategy_pool import StrategyPool
from trading.paper_trading import PaperTradingEngine
from trading.signal_generator import SignalGenerator
from trading.angelone_api import AngelOneAPI
from learning.feedback_loop import FeedbackLoop

class BacktestTrainer:
    """Backtest on historical data and train strategies"""
    
    def __init__(self):
        print("🤖 Initializing Backtest Trainer...")
        
        self.storage = DataStorage()
        self.technical_analyzer = TechnicalAnalyzer()
        self.news_analyzer = NewsSentimentAnalyzer()
        self.strategy_pool = StrategyPool(self.storage)
        self.paper_trading = PaperTradingEngine(self.storage, initial_capital=100000)
        self.feedback_loop = FeedbackLoop(self.storage, self.strategy_pool)
        self.angelone = AngelOneAPI()
        self.signal_generator = SignalGenerator(
            self.strategy_pool, self.technical_analyzer, self.news_analyzer
        )
        
        # Symbol tokens for AngelOne (you'll need to get these)
        self.symbol_tokens = {
            'RELIANCE-EQ': '2885',
            'TCS-EQ': '11536',
            'INFY-EQ': '1594',
            'HDFCBANK-EQ': '1333',
            'ICICIBANK-EQ': '4963',
            'SBIN-EQ': '3045',
            'BHARTIARTL-EQ': '10604',
            'ITC-EQ': '1660',
            'KOTAKBANK-EQ': '1922',
            'LT-EQ': '11483'
        }
        
        print("✅ Trainer initialized")
    
    def login(self):
        """Login to AngelOne"""
        print("\n🔐 Logging into AngelOne...")
        if self.angelone.login():
            print("✅ Login successful!")
            return True
        else:
            print("❌ Login failed. Will use mock data.")
            return False
    
    def fetch_historical_data(self, symbol, token, days=365):
        """Fetch real historical data from AngelOne"""
        try:
            print(f"  📥 Fetching {days} days of data for {symbol}...")
            
            to_date = datetime.now()
            from_date = to_date - timedelta(days=days)
            
            hist_data = self.angelone.smart_api.getCandleData({
                "exchange": "NSE",
                "symboltoken": token,
                "interval": "ONE_DAY",
                "fromdate": from_date.strftime("%Y-%m-%d 09:15"),
                "todate": to_date.strftime("%Y-%m-%d 15:30")
            })
            
            if hist_data['status'] and hist_data['data']:
                df = pd.DataFrame(
                    hist_data['data'],
                    columns=['timestamp', 'open', 'high', 'low', 'close', 'volume']
                )
                df['timestamp'] = pd.to_datetime(df['timestamp'])
                print(f"  ✅ Fetched {len(df)} days of data")
                return df
            else:
                print(f"  ⚠️  No data returned, using mock data")
                return self.generate_mock_data(symbol, days)
                
        except Exception as e:
            print(f"  ⚠️  Error fetching data: {e}, using mock data")
            return self.generate_mock_data(symbol, days)
    
    def generate_mock_data(self, symbol, days=365):
        """Generate realistic mock data"""
        dates = pd.date_range(end=datetime.now(), periods=days, freq='D')
        
        # Generate realistic price movements
        base_price = np.random.uniform(1000, 3000)
        returns = np.random.normal(0.0005, 0.015, days)
        prices = base_price * np.exp(np.cumsum(returns))
        
        df = pd.DataFrame({
            'timestamp': dates,
            'open': prices * np.random.uniform(0.99, 1.01, days),
            'high': prices * np.random.uniform(1.00, 1.03, days),
            'low': prices * np.random.uniform(0.97, 1.00, days),
            'close': prices,
            'volume': np.random.randint(500000, 5000000, days)
        })
        
        return df
    
    def backtest_symbol(self, symbol, df):
        """Backtest trading strategies on historical data"""
        print(f"\n📊 Backtesting {symbol}...")
        
        # Calculate technical indicators
        df = self.technical_analyzer.calculate_all_indicators(df)
        
        trades_executed = 0
        
        # Simulate trading day by day
        for i in range(50, len(df)):  # Start after 50 days for indicators
            current_data = df.iloc[:i+1].copy()
            current_price = current_data['close'].iloc[-1]
            
            # Mock market context
            market_context = {
                'timestamp': current_data['timestamp'].iloc[-1],
                'news_sentiment': {'sentiment': 'NEUTRAL', 'sentiment_score': 0},
                'condition': 'SIDEWAYS'
            }
            
            # Check existing position
            position = self.paper_trading.get_position(symbol)
            
            if position:
                # Check if we should exit
                should_exit, reason = self.signal_generator.should_exit_position(
                    symbol, position, current_price, current_data, market_context
                )
                
                if should_exit:
                    result = self.paper_trading.execute_sell(
                        symbol, current_price, position['strategy'], reason
                    )
                    
                    if result['success']:
                        trades_executed += 1
                        # Learn from trade
                        trade_result = {
                            'symbol': symbol,
                            'strategy': position['strategy'],
                            'pnl': result['pnl'],
                            'pnl_percent': result['pnl_percent'],
                            'entry_price': position['entry_price'],
                            'exit_price': current_price
                        }
                        self.feedback_loop.analyze_trade(trade_result, market_context)
            else:
                # Generate signal for new entry
                signal = self.signal_generator.generate_signal(symbol, current_data, market_context)
                
                if signal['action'] == 'BUY' and signal['confidence'] > 55:
                    quantity = int((self.paper_trading.capital * 0.1) / current_price)
                    
                    if quantity > 0:
                        result = self.paper_trading.execute_buy(
                            symbol, current_price, quantity,
                            'Consensus', signal['reason']
                        )
                        if result['success']:
                            trades_executed += 1
        
        # Close any remaining position
        position = self.paper_trading.get_position(symbol)
        if position:
            current_price = df['close'].iloc[-1]
            result = self.paper_trading.execute_sell(
                symbol, current_price, position['strategy'], "End of backtest"
            )
            if result['success']:
                trades_executed += 1
                trade_result = {
                    'symbol': symbol,
                    'strategy': position['strategy'],
                    'pnl': result['pnl'],
                    'pnl_percent': result['pnl_percent'],
                    'entry_price': position['entry_price'],
                    'exit_price': current_price
                }
                self.feedback_loop.analyze_trade(trade_result, market_context)
        
        print(f"  ✅ Completed {trades_executed} trades on {symbol}")
    
    def run_backtest(self, days=180):
        """Run backtest on all symbols"""
        print("\n" + "="*60)
        print("🎯 STARTING BACKTEST & TRAINING")
        print("="*60)
        print(f"📅 Training on last {days} days of data")
        print(f"📈 Symbols: {len(WATCHLIST)}")
        print()
        
        # Login to AngelOne
        logged_in = self.login()
        
        # Backtest each symbol
        for symbol in WATCHLIST:
            try:
                # Fetch historical data
                if logged_in and symbol in self.symbol_tokens:
                    df = self.fetch_historical_data(symbol, self.symbol_tokens[symbol], days)
                else:
                    df = self.generate_mock_data(symbol, days)
                
                # Run backtest
                self.backtest_symbol(symbol, df)
                
                # Small delay to avoid API rate limits
                time.sleep(1)
                
            except Exception as e:
                print(f"  ❌ Error backtesting {symbol}: {e}")
        
        # Generate final report
        self.generate_training_report()
    
    def generate_training_report(self):
        """Generate training results report"""
        print("\n" + "="*60)
        print("📊 TRAINING RESULTS")
        print("="*60)
        
        stats = self.paper_trading.get_statistics()
        print(f"\n💰 Final Capital: ₹{stats['capital']:,.2f}")
        print(f"📈 Total P&L: ₹{stats['total_pnl']:,.2f}")
        print(f"📊 ROI: {stats['roi']:.2f}%")
        print(f"🎯 Win Rate: {stats['win_rate']:.1f}%")
        print(f"📝 Total Trades: {stats['total_trades']}")
        print(f"✅ Winning Trades: {stats['winning_trades']}")
        print(f"❌ Losing Trades: {stats['losing_trades']}")
        
        # Strategy performance
        print(f"\n📈 Strategy Performance (Ranked):")
        perf_report = self.strategy_pool.get_performance_report()
        
        for i, strategy in enumerate(perf_report, 1):
            if strategy['total_trades'] > 0:
                emoji = "🥇" if i == 1 else "🥈" if i == 2 else "🥉" if i == 3 else "📊"
                print(f"  {emoji} {strategy['strategy']}:")
                print(f"     Trades: {strategy['total_trades']} | "
                      f"Win Rate: {strategy['win_rate']:.1f}% | "
                      f"P&L: ₹{strategy['total_pnl']:,.2f}")
        
        # Recommendations
        print(f"\n💡 Key Learnings:")
        recommendations = self.feedback_loop.get_recommendations()
        for rec in recommendations:
            print(f"  {rec}")
        
        # Market condition insights
        print(f"\n🌍 Market Condition Performance:")
        condition_perf = self.feedback_loop.get_market_condition_performance()
        for condition, metrics in condition_perf.items():
            print(f"  • {condition}: {metrics['total_trades']} trades, "
                  f"Success Rate: {metrics['success_rate']:.1f}%")
        
        print("\n" + "="*60)
        print("✅ Training Complete! Bot is now ready for live trading.")
        print("🚀 Run 'python main.py' tomorrow morning to start trading!")
        print("="*60)

if __name__ == "__main__":
    trainer = BacktestTrainer()
    
    # Run backtest on last 180 days (6 months)
    trainer.run_backtest(days=180)
