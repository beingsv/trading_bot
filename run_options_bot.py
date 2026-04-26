"""
Options Trading Bot - NIFTY Options Intraday Trading
Simplified version focused on options trading
"""
import time
from datetime import datetime, time as dt_time
import pandas as pd

from config.config import (
    PRIMARY_INDEX, INDEX_CONFIG, MARKET_OPEN_HOUR, MARKET_CLOSE_HOUR,
    MAX_DAILY_LOSS, MAX_POSITIONS, MARKET_HOLIDAYS, INITIAL_CAPITAL,
    NO_TRADE_AFTER_HOUR, NO_TRADE_AFTER_MINUTE, EXIT_ALL_BY_HOUR, EXIT_ALL_BY_MINUTE
)
from data.storage import DataStorage
from data.fetcher import DataFetcher
from data.options_chain import OptionsChainFetcher
from analysis.technical import TechnicalAnalyzer
from analysis.news_sentiment import NewsSentimentAnalyzer
from strategies.strategy_pool import StrategyPool
from trading.options_paper_trading import OptionsPaperTradingEngine
from trading.options_signal_generator import OptionsSignalGenerator
from trading.angelone_api import AngelOneAPI
from learning.feedback_loop import FeedbackLoop
from learning.market_conditions import MarketConditionDetector

class OptionsBot:
    """NIFTY Options Trading Bot"""
    
    def __init__(self):
        print("🤖 Initializing Options Trading Bot...")
        print(f"📊 Trading: {PRIMARY_INDEX} Options")
        print(f"💰 Capital: ₹{INITIAL_CAPITAL:,}")
        
        self.storage = DataStorage()
        self.angelone = AngelOneAPI()
        self.data_fetcher = DataFetcher(self.angelone)
        
        # Options-specific components
        self.options_chain = OptionsChainFetcher(self.angelone)
        self.paper_trading = OptionsPaperTradingEngine(self.storage)
        
        # Analysis components
        self.technical_analyzer = TechnicalAnalyzer()
        self.news_analyzer = NewsSentimentAnalyzer()
        self.market_detector = MarketConditionDetector()
        
        # Strategy components
        self.strategy_pool = StrategyPool(self.storage)
        self.signal_generator = OptionsSignalGenerator(
            self.strategy_pool,
            self.technical_analyzer,
            self.options_chain
        )
        
        self.feedback_loop = FeedbackLoop(self.storage, self.strategy_pool)
        
        self.logged_in = False
        self.scan_count = 0
        self.daily_start_capital = INITIAL_CAPITAL
        
        print("✅ Bot initialized\n")
    
    def is_market_holiday(self):
        """Check if today is a market holiday"""
        today = datetime.now().strftime('%Y-%m-%d')
        return today in MARKET_HOLIDAYS
    
    def is_market_hours(self):
        """Check if market is currently open"""
        now = datetime.now()
        current_time = now.time()
        
        market_open = dt_time(MARKET_OPEN_HOUR, 15)  # 9:15 AM
        market_close = dt_time(MARKET_CLOSE_HOUR, 30)  # 3:30 PM
        
        return market_open <= current_time <= market_close
    
    def login(self):
        """Login to AngelOne"""
        print("🔐 Logging into AngelOne...")
        success = self.angelone.login()
        
        if success:
            print("✅ Login successful!")
            self.logged_in = True
            return True
        else:
            print("❌ Login failed")
            return False
    
    def fetch_index_data(self):
        """Fetch NIFTY index data for technical analysis"""
        index_config = INDEX_CONFIG[PRIMARY_INDEX]
        token = index_config['token']
        
        # Fetch 5-minute candles for last 2 days (enough for indicators)
        data = self.data_fetcher.fetch_historical_data(
            symbol=PRIMARY_INDEX,
            token=token,
            interval='FIVE_MINUTE',
            days=2
        )
        
        if data is not None and not data.empty:
            # Calculate technical indicators
            data = self.technical_analyzer.calculate_all_indicators(data)
            return data
        
        return None
    
    def get_market_context(self, index_data):
        """Get market context (conditions, sentiment, etc.)"""
        
        # Detect market condition
        market_detection = self.market_detector.detect_condition(index_data, {})
        market_condition = market_detection['condition'] if isinstance(market_detection, dict) else market_detection
        
        # Get news sentiment (cached for 1 hour)
        news_sentiment = self.news_analyzer.get_market_sentiment()
        
        return {
            'market_condition': market_condition,
            'news_sentiment': news_sentiment,
            'timestamp': datetime.now()
        }
    
    def scan_and_trade(self):
        """Main trading logic - scan for signals and execute"""
        
        self.scan_count += 1
        print(f"\n{'='*60}")
        print(f"🔍 SCAN #{self.scan_count} - {datetime.now().strftime('%I:%M:%S %p')}")
        print(f"{'='*60}")
        
        # Check daily loss limit
        # Calculate actual P&L from closed trades, not capital change
        # (Capital decreases when buying options, but that's not a loss)
        closed_pnl = self.paper_trading.get_total_pnl()  # Only closed trades
        if closed_pnl <= -MAX_DAILY_LOSS:
            print(f"🛑 Daily loss limit hit: ₹{closed_pnl:.2f}")
            print("⏸️  Stopping trading for today")
            return False
        
        # Fetch index data
        print(f"📊 Fetching {PRIMARY_INDEX} data...")
        index_data = self.fetch_index_data()
        
        if index_data is None or index_data.empty:
            print("❌ Failed to fetch index data")
            return True
        
        spot_price = index_data['close'].iloc[-1]
        print(f"💹 {PRIMARY_INDEX} Spot: ₹{spot_price:.2f}")
        
        # Get market context
        market_context = self.get_market_context(index_data)
        print(f"🌍 Market: {market_context['market_condition']}")
        
        # Check existing positions first
        open_positions = self.paper_trading.get_all_positions()
        print(f"📦 Open Positions: {len(open_positions)}/{MAX_POSITIONS}")
        
        # Update and check exit conditions for open positions
        for pos_id, position in list(open_positions.items()):
            # Fetch current option data
            chain_data = self.options_chain.fetch_option_chain(spot_price)
            
            # Find matching option in chain
            current_option = None
            for opt in chain_data['options']:
                if opt['strike'] == position['strike']:
                    if position['option_type'] == 'CE':
                        current_option = opt['call']
                    else:
                        current_option = opt['put']
                    break
            
            if current_option:
                current_premium = current_option['ltp']
                
                # Update position
                self.paper_trading.update_position_greeks(
                    pos_id, current_premium, current_option
                )
                
                # Check exit conditions
                should_exit, reason = self.paper_trading.check_exit_conditions(
                    pos_id, current_premium, current_option
                )
                
                if should_exit:
                    print(f"🚪 Exiting position: {reason}")
                    result = self.paper_trading.execute_sell_option(
                        pos_id, current_premium, reason
                    )
                    
                    if result['success']:
                        # Learn from trade
                        trade_result = {
                            'symbol': f"{position['symbol']}_{position['strike']}_{position['option_type']}",
                            'strategy': position['strategy'],
                            'pnl': result['pnl'],
                            'pnl_percent': result['pnl_percent']
                        }
                        self.feedback_loop.analyze_trade(trade_result, market_context)
        
        # Check if we can open new positions
        if len(open_positions) >= MAX_POSITIONS:
            print(f"⏸️  Max positions reached ({MAX_POSITIONS})")
            return True
        
        # Check if it's too late to enter new trades
        current_time = datetime.now().time()
        no_trade_time = dt_time(NO_TRADE_AFTER_HOUR, NO_TRADE_AFTER_MINUTE)
        
        if current_time >= no_trade_time:
            print(f"⏰ No new trades after {NO_TRADE_AFTER_HOUR}:{NO_TRADE_AFTER_MINUTE:02d}")
            return True
        
        # Generate signal
        print(f"🎯 Generating signal...")
        signal = self.signal_generator.generate_signal(
            index_data, market_context, spot_price
        )
        
        # DEBUG: Show individual strategy signals
        if 'signals' in signal and signal['signals']:
            print(f"\n  📊 Individual Strategy Signals:")
            for strat_signal in signal['signals']:
                action_emoji = "🟢" if strat_signal['action'] == 'BUY' else "🔴" if strat_signal['action'] == 'SELL' else "⚪"
                print(f"     {action_emoji} {strat_signal['strategy']}: {strat_signal['action']} ({strat_signal['confidence']:.0f}%)")
                print(f"        → {strat_signal['reason']}")
        
        print(f"\n📡 Final Signal: {signal['action']} (Confidence: {signal['confidence']:.0f}%)")
        print(f"💭 Reason: {signal['reason']}")
        
        # Execute if confidence is high enough
        # PAPER TRADING: 50% threshold for more trades
        if signal['action'] in ['BUY_CALL', 'BUY_PUT'] and signal['confidence'] >= 50:
            selected_option = signal['selected_option']
            
            if selected_option:
                print(f"\n💼 Selected Option:")
                print(f"   Strike: {selected_option['strike']}")
                print(f"   Type: {selected_option['option_type']}")
                print(f"   Premium: ₹{selected_option['ltp']:.2f}")
                print(f"   Delta: {selected_option.get('delta', 0):.2f}")
                print(f"   IV: {selected_option.get('iv', 0)*100:.1f}%")
                
                # Execute trade
                result = self.paper_trading.execute_buy_option(
                    selected_option,
                    strategy='Consensus',
                    reason=signal['reason'],
                    lots=1
                )
                
                if result['success']:
                    print(f"✅ Trade executed successfully!")
                else:
                    print(f"❌ Trade failed: {result.get('reason', 'Unknown')}")
        
        # Show current stats
        stats = self.paper_trading.get_statistics()
        print(f"\n📊 Stats: Capital: ₹{stats['capital']:.2f} | P&L: ₹{stats['total_pnl']:.2f} | Win Rate: {stats['win_rate']:.1f}%")
        
        return True
    
    def run(self):
        """Main bot loop"""
        print("\n" + "="*60)
        print("🚀 STARTING OPTIONS TRADING BOT")
        print("="*60)
        print(f"📅 Date: {datetime.now().strftime('%d %B %Y')}")
        print(f"⏰ Market Hours: 9:15 AM - 3:30 PM")
        print(f"🔄 Scan Interval: Every 5 minutes")
        print(f"🛡️  Max Daily Loss: ₹{MAX_DAILY_LOSS:,}")
        print(f"🎯 Max Positions: {MAX_POSITIONS}")
        print("="*60 + "\n")
        
        # Check holiday
        if self.is_market_holiday():
            print("🏖️  Today is a market holiday")
            return
        
        # Login
        if not self.login():
            print("❌ Cannot proceed without login")
            return
        
        # Record start capital
        self.daily_start_capital = self.paper_trading.capital
        
        # Wait for market open
        while not self.is_market_hours():
            now = datetime.now()
            print(f"⏳ Waiting for market open... (Current: {now.strftime('%I:%M %p')})")
            time.sleep(60)  # Check every minute
        
        print("\n🔔 Market is OPEN! Starting trading...\n")
        
        # Main trading loop
        try:
            while self.is_market_hours():
                # Scan and trade
                should_continue = self.scan_and_trade()
                
                if not should_continue:
                    break
                
                # Check if we need to exit all positions (near market close)
                current_time = datetime.now().time()
                exit_time = dt_time(EXIT_ALL_BY_HOUR, EXIT_ALL_BY_MINUTE)
                
                if current_time >= exit_time:
                    print(f"\n⏰ Market closing time - Exiting all positions...")
                    open_positions = self.paper_trading.get_all_positions()
                    
                    if open_positions:
                        # Fetch current premiums
                        spot_price = self.fetch_index_data()['close'].iloc[-1]
                        chain_data = self.options_chain.fetch_option_chain(spot_price)
                        
                        current_premiums = {}
                        for pos_id, position in open_positions.items():
                            for opt in chain_data['options']:
                                if opt['strike'] == position['strike']:
                                    if position['option_type'] == 'CE':
                                        current_premiums[pos_id] = opt['call']['ltp']
                                    else:
                                        current_premiums[pos_id] = opt['put']['ltp']
                        
                        self.paper_trading.close_all_positions(
                            current_premiums, "Market close"
                        )
                    
                    break
                
                # Wait 5 minutes before next scan
                print(f"\n⏸️  Waiting 5 minutes for next scan...")
                time.sleep(300)  # 5 minutes
        
        except KeyboardInterrupt:
            print("\n\n⚠️  Bot stopped by user")
        
        # End of day summary
        self.show_daily_summary()
    
    def show_daily_summary(self):
        """Show end of day summary"""
        print("\n" + "="*60)
        print("📊 END OF DAY SUMMARY")
        print("="*60)
        
        stats = self.paper_trading.get_statistics()
        
        print(f"💰 Starting Capital: ₹{self.daily_start_capital:,.2f}")
        print(f"💰 Ending Capital: ₹{stats['capital']:,.2f}")
        print(f"📈 Total P&L: ₹{stats['total_pnl']:,.2f}")
        print(f"📊 ROI: {stats['roi']:.2f}%")
        print(f"📝 Total Trades: {stats['total_trades']}")
        print(f"✅ Winning Trades: {stats['winning_trades']}")
        print(f"❌ Losing Trades: {stats['losing_trades']}")
        print(f"🎯 Win Rate: {stats['win_rate']:.1f}%")
        print(f"⏱️  Avg Holding Time: {stats['avg_holding_time_minutes']:.0f} minutes")
        print("="*60)
        
        # Backup database
        print("\n💾 Backing up database...")
        self.storage.backup_database()
        print("✅ Backup complete")
        
        print("\n🎉 Trading session complete!")

if __name__ == "__main__":
    bot = OptionsBot()
    bot.run()
