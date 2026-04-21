"""
Continuous Trading Bot - Monitors market all day
Runs from market open to close, checking every 5 minutes
"""
import time
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import schedule

from config.config import (
    PAPER_TRADING, WATCHLIST, MARKET_OPEN_HOUR, MARKET_CLOSE_HOUR,
    MAX_DAILY_LOSS, MAX_DAILY_LOSS_PERCENT, MAX_POSITIONS, 
    MAX_POSITION_PER_SYMBOL, MARKET_HOLIDAYS, INITIAL_CAPITAL, MIN_CAPITAL_TO_TRADE,
    USE_MOCK_DATA
)
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

class ContinuousTradingBot:
    """Trading bot that monitors market continuously"""
    
    def __init__(self):
        print("🤖 Initializing Continuous Trading Bot...")
        
        self.storage = DataStorage()
        self.technical_analyzer = TechnicalAnalyzer()
        self.news_analyzer = NewsSentimentAnalyzer()
        self.strategy_pool = StrategyPool(self.storage)
        self.paper_trading = PaperTradingEngine(self.storage)
        self.feedback_loop = FeedbackLoop(self.storage, self.strategy_pool)
        self.market_detector = MarketConditionDetector()
        self.angelone = AngelOneAPI() if not PAPER_TRADING else None
        
        # Data fetcher (for real data mode)
        self.data_fetcher = None
        if not USE_MOCK_DATA and self.angelone:
            self.data_fetcher = DataFetcher(self.angelone.client if self.angelone else None)
        
        self.signal_generator = SignalGenerator(
            self.strategy_pool, self.technical_analyzer, self.news_analyzer
        )
        
        self.is_market_open = False
        self.market_context = {}
        self.logged_in = False
        self.scan_count = 0
        self.paused = False  # Pause flag
        self.daily_start_capital = INITIAL_CAPITAL
        self.session_start_time = None
        
        print("✅ Bot initialized")
    
    def start(self):
        """Start continuous monitoring"""
        print("\n" + "="*60)
        print("🚀 STARTING CONTINUOUS TRADING BOT")
        print("="*60)
        print(f"📝 Mode: {'PAPER TRADING' if PAPER_TRADING else 'LIVE TRADING'}")
        print(f"📊 Data Source: {'MOCK DATA' if USE_MOCK_DATA else 'REAL-TIME ANGELONE'}")
        print(f"📈 Watching {len(WATCHLIST)} symbols")
        print(f"⏰ Market Hours: 9:15 AM - 3:30 PM")
        print(f"🔄 Scan Interval: Every 5 minutes")
        print(f"🛡️  Max Daily Loss: ₹{MAX_DAILY_LOSS:,}")
        print(f"🎯 Max Positions: {MAX_POSITIONS}")
        print("="*60 + "\n")
        
        # Check if today is a holiday
        if self.is_market_holiday():
            print("🏖️  Today is a market holiday. Bot will not trade.")
            print("📅 Next trading day: Check NSE calendar")
            return
        
        # Login to AngelOne if live trading
        if not PAPER_TRADING and self.angelone:
            if not self.login_with_retry():
                return
        
        # Record starting capital
        self.daily_start_capital = self.paper_trading.capital
        
        # Initial setup
        self.update_market_context()
        
        # Schedule tasks
        self.schedule_tasks()
        
        print("✅ Bot is now running. Press Ctrl+C to stop.\n")
        print("💡 Commands:")
        print("   - Ctrl+C: Stop bot and close all positions")
        print("   - Create file 'PAUSE' to pause scanning")
        print("   - Delete file 'PAUSE' to resume\n")
        
        # Main loop
        try:
            while True:
                schedule.run_pending()
                
                # Check session every 30 seconds
                if not PAPER_TRADING and self.logged_in:
                    self.check_and_refresh_session()
                
                time.sleep(30)  # Check every 30 seconds
        except KeyboardInterrupt:
            print("\n\n⏹️  Stopping bot...")
            self.on_market_close()
            print("👋 Bot stopped. See you tomorrow!")
    
    def schedule_tasks(self):
        """Schedule periodic tasks"""
        # Market open
        schedule.every().day.at("09:15").do(self.on_market_open)
        
        # Scan every 5 minutes during market hours
        schedule.every(5).minutes.do(self.scan_if_market_open)
        
        # Update news every 2 hours (safer for API limits)
        schedule.every(2).hours.do(self.update_market_context)
        
        # Market close
        schedule.every().day.at("15:30").do(self.on_market_close)
    
    def is_market_holiday(self):
        """Check if today is a market holiday"""
        today = datetime.now().strftime('%Y-%m-%d')
        return today in MARKET_HOLIDAYS
    
    def login_with_retry(self, max_retries=3):
        """Login with retry logic"""
        print("🔐 Logging into AngelOne...")
        
        for attempt in range(max_retries):
            try:
                if self.angelone.login():
                    self.logged_in = True
                    self.session_start_time = datetime.now()
                    print("✅ Login successful!\n")
                    return True
                else:
                    print(f"❌ Login attempt {attempt + 1} failed")
            except Exception as e:
                print(f"❌ Login error: {e}")
            
            if attempt < max_retries - 1:
                print(f"⏳ Retrying in 5 seconds...")
                time.sleep(5)
        
        print("❌ All login attempts failed. Exiting.\n")
        return False
    
    def check_and_refresh_session(self):
        """Check if session needs refresh (every 3 hours)"""
        if not self.session_start_time:
            return
        
        hours_elapsed = (datetime.now() - self.session_start_time).seconds / 3600
        
        if hours_elapsed >= 3:  # Refresh every 3 hours
            print(f"\n🔄 Session refresh needed (running for {hours_elapsed:.1f} hours)")
            if self.login_with_retry():
                print("✅ Session refreshed successfully")
            else:
                print("❌ Session refresh failed. Bot may not work properly.")
    
    def check_daily_loss_limit(self):
        """Check if daily loss limit exceeded"""
        current_capital = self.paper_trading.capital
        daily_pnl = current_capital - self.daily_start_capital
        daily_loss_limit = min(MAX_DAILY_LOSS, self.daily_start_capital * (MAX_DAILY_LOSS_PERCENT / 100))
        
        if daily_pnl < -daily_loss_limit:
            print(f"\n🚨 DAILY LOSS LIMIT EXCEEDED!")
            print(f"   Daily P&L: ₹{daily_pnl:,.2f}")
            print(f"   Loss Limit: ₹{daily_loss_limit:,.2f}")
            print(f"   🛑 STOPPING ALL TRADING FOR TODAY")
            
            # Close all positions
            self.close_all_positions()
            
            # Pause bot
            import os
            with open('PAUSE', 'w') as f:
                f.write('Daily loss limit exceeded')
            
            return True
        
        return False
    
    def can_open_new_position(self, symbol):
        """Check if we can open a new position"""
        # Check minimum capital
        if self.paper_trading.capital < MIN_CAPITAL_TO_TRADE:
            print(f"  🚨 Insufficient capital (₹{self.paper_trading.capital:,.2f}). Minimum required: ₹{MIN_CAPITAL_TO_TRADE:,}")
            print(f"  🛑 STOPPING ALL TRADING")
            import os
            with open('PAUSE', 'w') as f:
                f.write('Insufficient capital')
            return False
        
        # Check max positions
        if len(self.paper_trading.positions) >= MAX_POSITIONS:
            print(f"  ⚠️  Max positions ({MAX_POSITIONS}) reached. Cannot open new position.")
            return False
        
        # Check duplicate position
        if symbol in self.paper_trading.positions:
            print(f"  ⚠️  Already have position in {symbol}. Cannot open duplicate.")
            return False
        
        # Check daily loss limit
        if self.check_daily_loss_limit():
            return False
        
        return True
    
    def is_market_hours(self):
        """Check if market is currently open"""
        now = datetime.now()
        market_open = now.replace(hour=9, minute=15, second=0)
        market_close = now.replace(hour=15, minute=30, second=0)
        
        # Check if it's a weekday
        if now.weekday() >= 5:  # Saturday = 5, Sunday = 6
            return False
        
        return market_open <= now <= market_close
    
    def on_market_open(self):
        """Called when market opens"""
        print("\n" + "="*60)
        print("🔔 MARKET IS NOW OPEN")
        print("="*60)
        self.is_market_open = True
        self.scan_count = 0
        self.update_market_context()
        self.scan_and_trade()
    
    def on_market_close(self):
        """Called when market closes"""
        print("\n" + "="*60)
        print("🔔 MARKET IS NOW CLOSED")
        print("="*60)
        self.is_market_open = False
        
        # Close any open positions (for intraday)
        self.close_all_positions()
        
        # Generate daily report
        self.generate_daily_report()
        
        # Stop the bot
        print("\n👋 Bot stopping automatically. See you tomorrow!")
        print("="*60 + "\n")
        
        # Exit the program
        import sys
        sys.exit(0)
    
    def scan_if_market_open(self):
        """Scan only if market is open and not paused"""
        # Check for pause file
        import os
        if os.path.exists('PAUSE'):
            if not self.paused:
                print(f"\n⏸️  Bot PAUSED at {datetime.now().strftime('%H:%M:%S')}")
                print("   Delete 'PAUSE' file to resume\n")
                self.paused = True
            return
        else:
            if self.paused:
                print(f"\n▶️  Bot RESUMED at {datetime.now().strftime('%H:%M:%S')}\n")
                self.paused = False
        
        if self.is_market_hours():
            self.scan_and_trade()
    
    def update_market_context(self):
        """Update market context with latest news"""
        print(f"\n[{datetime.now().strftime('%H:%M:%S')}] 📡 Updating market context...")
        
        try:
            market_sentiment = self.news_analyzer.get_market_sentiment()
            
            self.market_context = {
                'timestamp': datetime.now(),
                'news_sentiment': market_sentiment,
                'condition': 'SIDEWAYS'
            }
            
            print(f"✅ Market Sentiment: {market_sentiment.get('sentiment', 'UNKNOWN')} "
                  f"(Score: {market_sentiment.get('sentiment_score', 0):.2f})")
        except Exception as e:
            print(f"⚠️  Could not fetch news: {e}")
            self.market_context = {
                'timestamp': datetime.now(),
                'news_sentiment': {'sentiment': 'NEUTRAL', 'sentiment_score': 0},
                'condition': 'SIDEWAYS'
            }
    
    def generate_mock_data(self, symbol, days=100):
        """Generate mock historical data"""
        dates = pd.date_range(end=datetime.now(), periods=days, freq='D')
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
    
    def scan_and_trade(self):
        """Scan all symbols and execute trades"""
        self.scan_count += 1
        
        print(f"\n{'='*60}")
        print(f"🔍 SCAN #{self.scan_count} - {datetime.now().strftime('%H:%M:%S')}")
        print(f"{'='*60}")
        
        # Show portfolio status
        stats = self.paper_trading.get_statistics()
        print(f"💼 Portfolio: ₹{stats['capital']:,.2f} | "
              f"P&L: ₹{stats['total_pnl']:,.2f} ({stats['roi']:.2f}%) | "
              f"Open: {stats['open_positions']}")
        print()
        
        # Analyze each symbol
        for symbol in WATCHLIST[:5]:  # Monitor first 5 stocks
            try:
                self.analyze_and_trade(symbol)
            except Exception as e:
                print(f"  ❌ Error analyzing {symbol}: {e}")
        
        print(f"\n✅ Scan #{self.scan_count} complete. Next scan in 5 minutes...")
    
    def analyze_and_trade(self, symbol):
        """Analyze symbol and execute trade if needed"""
        try:
            # Fetch data based on mode (mock or real)
            df = self.fetch_data(symbol)
            df = self.technical_analyzer.calculate_all_indicators(df)
            
            current_price = df['close'].iloc[-1]
            position = self.paper_trading.get_position(symbol)
            
            if position:
                # Monitor existing position
                entry_price = position['entry_price']
                pnl_percent = ((current_price - entry_price) / entry_price) * 100
                
                print(f"  📊 {symbol}: ₹{current_price:.2f} | "
                      f"Position: {position['quantity']} @ ₹{entry_price:.2f} | "
                      f"P&L: {pnl_percent:+.2f}%")
                
                # Check if should exit
                should_exit, reason = self.signal_generator.should_exit_position(
                    symbol, position, current_price, df, self.market_context
                )
                
                if should_exit:
                    result = self.paper_trading.execute_sell(
                        symbol, current_price, position['strategy'], reason
                    )
                    
                    if result['success']:
                        trade_result = {
                            'symbol': symbol,
                            'strategy': position['strategy'],
                            'pnl': result['pnl'],
                            'pnl_percent': result['pnl_percent'],
                            'entry_price': entry_price,
                            'exit_price': current_price
                        }
                        self.feedback_loop.analyze_trade(trade_result, self.market_context)
                        
                        # Check daily loss limit after trade
                        self.check_daily_loss_limit()
            else:
                # Look for new entry
                signal = self.signal_generator.generate_signal(symbol, df, self.market_context)
                
                action_emoji = "🟢" if signal['action'] == 'BUY' else "🔴" if signal['action'] == 'SELL' else "⚪"
                print(f"  {action_emoji} {symbol}: ₹{current_price:.2f} | "
                      f"{signal['action']} ({signal['confidence']:.0f}%)")
                
                if signal['action'] == 'BUY' and signal['confidence'] > 60:
                    # Safety checks before opening position
                    if not self.can_open_new_position(symbol):
                        return
                    
                    quantity = int((self.paper_trading.capital * 0.1) / current_price)
                    
                    if quantity > 0:
                        self.paper_trading.execute_buy(
                            symbol, current_price, quantity,
                            'Consensus', signal['reason']
                        )
        except Exception as e:
            print(f"  ❌ Error analyzing {symbol}: {e}")
    
    def close_all_positions(self):
        """Close all open positions at market close"""
        if not self.paper_trading.positions:
            return
        
        print("\n📤 Closing all open positions...")
        
        for symbol in list(self.paper_trading.positions.keys()):
            position = self.paper_trading.positions[symbol]
            # Fetch current price based on mode
            df = self.fetch_data(symbol)
            current_price = df['close'].iloc[-1]
            
            result = self.paper_trading.execute_sell(
                symbol, current_price, position['strategy'],
                "Market close - Intraday position"
            )
            
            if result['success']:
                trade_result = {
                    'symbol': symbol,
                    'strategy': position['strategy'],
                    'pnl': result['pnl'],
                    'pnl_percent': result['pnl_percent'],
                    'entry_price': position['entry_price'],
                    'exit_price': current_price
                }
                self.feedback_loop.analyze_trade(trade_result, self.market_context)
    
    def generate_daily_report(self):
        """Generate end-of-day report"""
        print("\n" + "="*60)
        print("📊 DAILY PERFORMANCE REPORT")
        print("="*60)
        
        stats = self.paper_trading.get_statistics()
        print(f"\n💰 Final Capital: ₹{stats['capital']:,.2f}")
        print(f"📈 Today's P&L: ₹{stats['total_pnl']:,.2f}")
        print(f"📊 ROI: {stats['roi']:.2f}%")
        print(f"🎯 Win Rate: {stats['win_rate']:.1f}%")
        print(f"📝 Total Trades Today: {stats['total_trades']}")
        print(f"✅ Winning: {stats['winning_trades']}")
        print(f"❌ Losing: {stats['losing_trades']}")
        print(f"🔄 Total Scans: {self.scan_count}")
        
        # Recommendations
        recommendations = self.feedback_loop.get_recommendations()
        print(f"\n💡 Recommendations:")
        for rec in recommendations:
            print(f"  {rec}")
        
        print("\n" + "="*60)

if __name__ == "__main__":
    bot = ContinuousTradingBot()
    bot.start()
