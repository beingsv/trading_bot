"""
Main Trading Bot Orchestrator
"""
import time
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

from config.config import PAPER_TRADING, WATCHLIST, MARKET_OPEN_HOUR, MARKET_CLOSE_HOUR, USE_MOCK_DATA
from data.storage import DataStorage
from data.fetcher import DataFetcher
from analysis.technical import TechnicalAnalyzer
from analysis.news_sentiment import NewsSentimentAnalyzer
from strategies.strategy_pool import StrategyPool
from trading.paper_trading import PaperTradingEngine
from trading.signal_generator import SignalGenerator
from trading.angelone_api import AngelOneAPI
from learning.feedback_loop import FeedbackLoop
from learning.market_conditions import MarketConditionDetector

class TradingBot:
    """Main trading bot orchestrator"""
    
    def __init__(self):
        print("🤖 Initializing Trading Bot...")
        
        self.storage = DataStorage()
        self.technical_analyzer = TechnicalAnalyzer()
        self.news_analyzer = NewsSentimentAnalyzer()
        self.strategy_pool = StrategyPool(self.storage)
        self.paper_trading = PaperTradingEngine(self.storage)
        self.feedback_loop = FeedbackLoop(self.storage, self.strategy_pool)
        self.market_detector = MarketConditionDetector()
        # Create AngelOne client if using real data (even in paper trading)
        self.angelone = AngelOneAPI() if (not PAPER_TRADING or not USE_MOCK_DATA) else None
        
        # Data fetcher (for real data mode)
        self.data_fetcher = None
        if not USE_MOCK_DATA and self.angelone:
            self.data_fetcher = DataFetcher(self.angelone.client if self.angelone else None)
        
        self.signal_generator = SignalGenerator(
            self.strategy_pool, self.technical_analyzer, self.news_analyzer
        )
        
        self.is_market_open = False
        self.market_context = {}
        
        print("✅ Bot initialized")
    
    def start(self):
        """Start the bot"""
        print("\n🚀 STARTING TRADING BOT")
        print(f"📝 Mode: {'PAPER TRADING' if PAPER_TRADING else 'LIVE TRADING'}")
        print(f"📊 Data Source: {'MOCK DATA' if USE_MOCK_DATA else 'REAL-TIME ANGELONE'}")
        print(f"📈 Watching {len(WATCHLIST)} symbols\n")
        
        # Login to AngelOne if using real data (even in paper trading)
        if not USE_MOCK_DATA and self.angelone:
            print("🔐 Logging into AngelOne...")
            if not self.angelone.login():
                print("❌ Failed to login. Falling back to mock data.")
                self.data_fetcher = None
                print("❌ Failed to login. Exiting.")
                return
        
        # Update market context
        self.update_market_context()
        
        # Fetch historical data and analyze
        print("\n📊 Fetching historical data and analyzing...\n")
        self.analyze_watchlist()
        
        # Generate report
        self.generate_report()
    
    def update_market_context(self):
        """Update market context"""
        print("📡 Updating market context...")
        
        try:
            market_sentiment = self.news_analyzer.get_market_sentiment()
            
            self.market_context = {
                'timestamp': datetime.now(),
                'news_sentiment': market_sentiment,
                'condition': 'SIDEWAYS'
            }
            
            print(f"✅ Market Sentiment: {market_sentiment.get('sentiment', 'UNKNOWN')} "
                  f"(Score: {market_sentiment.get('sentiment_score', 0):.2f})")
            print(f"📰 Analyzed {market_sentiment.get('article_count', 0)} news articles\n")
        except Exception as e:
            print(f"⚠️  Could not fetch news (API limit or network issue): {e}\n")
            self.market_context = {
                'timestamp': datetime.now(),
                'news_sentiment': {'sentiment': 'NEUTRAL', 'sentiment_score': 0},
                'condition': 'SIDEWAYS'
            }
    
    def generate_mock_data(self, symbol, days=100):
        """Generate mock historical data for testing"""
        dates = pd.date_range(end=datetime.now(), periods=days, freq='D')
        
        # Generate realistic price data
        base_price = np.random.uniform(1000, 3000)
        returns = np.random.normal(0.001, 0.02, days)
        prices = base_price * np.exp(np.cumsum(returns))
        
        df = pd.DataFrame({
            'timestamp': dates,
            'open': prices * np.random.uniform(0.98, 1.02, days),
            'high': prices * np.random.uniform(1.00, 1.05, days),
            'low': prices * np.random.uniform(0.95, 1.00, days),
            'close': prices,
            'volume': np.random.randint(100000, 1000000, days)
        })
        
        return df
    
    def fetch_data(self, symbol, days=100):
        """Fetch data based on USE_MOCK_DATA setting"""
        if USE_MOCK_DATA:
            return self.generate_mock_data(symbol, days)
        else:
            # Fetch real data from AngelOne
            if self.data_fetcher:
                try:
                    df = self.data_fetcher.get_historical_data(symbol, days)
                    if not df.empty:
                        return df
                    else:
                        print(f"  ⚠️  No real data available for {symbol}, using mock data")
                        return self.generate_mock_data(symbol, days)
                except Exception as e:
                    print(f"  ⚠️  Error fetching real data for {symbol}: {e}, using mock data")
                    return self.generate_mock_data(symbol, days)
            else:
                print(f"  ⚠️  Data fetcher not initialized, using mock data")
                return self.generate_mock_data(symbol, days)
    
    def analyze_watchlist(self):
        """Analyze all symbols in watchlist"""
        
        for symbol in WATCHLIST[:3]:  # Analyze first 3 for demo
            print(f"📊 Analyzing {symbol}...")
            
            try:
                # Fetch data based on mode (mock or real)
                df = self.fetch_data(symbol)
                
                # Calculate technical indicators
                df = self.technical_analyzer.calculate_all_indicators(df)
                
                # Generate trading signal
                signal = self.signal_generator.generate_signal(symbol, df, self.market_context)
                
                # Display signal
                action_emoji = "🟢" if signal['action'] == 'BUY' else "🔴" if signal['action'] == 'SELL' else "⚪"
                print(f"  {action_emoji} Signal: {signal['action']} (Confidence: {signal['confidence']:.1f}%)")
                print(f"  📝 Reason: {signal['reason'][:80]}...")
                
                # Execute trade if signal is strong
                if signal['action'] == 'BUY' and signal['confidence'] > 65:
                    current_price = df['close'].iloc[-1]
                    quantity = int((self.paper_trading.capital * 0.1) / current_price)
                    
                    if quantity > 0:
                        result = self.paper_trading.execute_buy(
                            symbol, current_price, quantity,
                            'Consensus', signal['reason']
                        )
                        
                elif signal['action'] == 'SELL':
                    position = self.paper_trading.get_position(symbol)
                    if position:
                        current_price = df['close'].iloc[-1]
                        result = self.paper_trading.execute_sell(
                            symbol, current_price, 'Consensus', signal['reason']
                        )
                        
                        # Learn from the trade
                        if result['success']:
                            trade_result = {
                                'symbol': symbol,
                                'strategy': 'Consensus',
                                'pnl': result['pnl'],
                                'pnl_percent': result['pnl_percent'],
                                'entry_price': position['entry_price'],
                                'exit_price': current_price
                            }
                            self.feedback_loop.analyze_trade(trade_result, self.market_context)
                
                print()
                
            except Exception as e:
                print(f"  ❌ Error analyzing {symbol}: {e}\n")
    
    def generate_report(self):
        """Generate performance report"""
        print("="*60)
        print("📊 PERFORMANCE REPORT")
        print("="*60)
        
        stats = self.paper_trading.get_statistics()
        print(f"💰 Capital: ₹{stats['capital']:,.2f}")
        print(f"📈 Total P&L: ₹{stats['total_pnl']:,.2f}")
        print(f"📊 ROI: {stats['roi']:.2f}%")
        print(f"🎯 Win Rate: {stats['win_rate']:.1f}%")
        print(f"📝 Total Trades: {stats['total_trades']}")
        print(f"🔓 Open Positions: {stats['open_positions']}")
        
        # Show open positions
        if self.paper_trading.positions:
            print(f"\n📋 Open Positions:")
            for symbol, pos in self.paper_trading.positions.items():
                print(f"  • {symbol}: {pos['quantity']} @ ₹{pos['entry_price']:.2f}")
        
        # Strategy performance
        print(f"\n📈 Strategy Performance:")
        for strategy in self.strategy_pool.get_performance_report():
            if strategy['total_trades'] > 0:
                print(f"  • {strategy['strategy']}: {strategy['total_trades']} trades, "
                      f"Win Rate: {strategy['win_rate']:.1f}%, P&L: ₹{strategy['total_pnl']:.2f}")
        
        # Recommendations
        recommendations = self.feedback_loop.get_recommendations()
        print(f"\n💡 Recommendations:")
        for rec in recommendations:
            print(f"  {rec}")
        
        print("\n" + "="*60)
        print("✅ Analysis complete! Run again tomorrow to continue learning.")
        print("="*60)

if __name__ == "__main__":
    bot = TradingBot()
    bot.start()
