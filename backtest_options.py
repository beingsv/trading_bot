"""
Options Backtesting - Train bot on historical data
Run bot on past dates to learn and improve
"""
import sys
from datetime import datetime, timedelta
import pandas as pd

from config.config import (
    PRIMARY_INDEX, INDEX_CONFIG, INITIAL_CAPITAL,
    MAX_DAILY_LOSS, MAX_POSITIONS
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

class OptionsBacktester:
    """Backtest options trading on historical data"""
    
    def __init__(self):
        print("🤖 Initializing Options Backtester...")
        
        self.storage = DataStorage()
        self.angelone = AngelOneAPI()
        self.data_fetcher = DataFetcher(self.angelone)
        
        # Options components
        self.options_chain = OptionsChainFetcher(self.angelone)
        self.paper_trading = OptionsPaperTradingEngine(self.storage, initial_capital=INITIAL_CAPITAL)
        
        # Analysis
        self.technical_analyzer = TechnicalAnalyzer()
        self.news_analyzer = NewsSentimentAnalyzer()
        self.market_detector = MarketConditionDetector()
        
        # Strategies
        self.strategy_pool = StrategyPool(self.storage)
        self.signal_generator = OptionsSignalGenerator(
            self.strategy_pool,
            self.technical_analyzer,
            self.options_chain
        )
        
        self.feedback_loop = FeedbackLoop(self.storage, self.strategy_pool)
        
        self.daily_start_capital = INITIAL_CAPITAL
        
        print("✅ Backtester initialized\n")
    
    def login(self):
        """Login to AngelOne"""
        print("🔐 Logging into AngelOne...")
        success = self.angelone.login()
        
        if success:
            print("✅ Login successful!\n")
            return True
        else:
            print("❌ Login failed\n")
            return False
    
    def fetch_historical_data(self, date_str, days_back=2):
        """
        Fetch historical NIFTY data for backtesting
        
        Args:
            date_str: Date to backtest (YYYY-MM-DD)
            days_back: Days of data to fetch (for indicators)
        """
        target_date = datetime.strptime(date_str, '%Y-%m-%d')
        
        print(f"📊 Fetching NIFTY data for {target_date.strftime('%d %B %Y')}...")
        
        index_config = INDEX_CONFIG[PRIMARY_INDEX]
        token = index_config['token']
        
        # Set to_date to end of target day (3:30 PM or later)
        to_date = target_date.replace(hour=23, minute=59, second=59)
        
        # Fetch data from (target_date - days_back) to end of target_date
        data = self.data_fetcher.fetch_historical_data(
            symbol=PRIMARY_INDEX,
            token=token,
            interval='FIVE_MINUTE',
            days=days_back + 1,
            to_date=to_date
        )
        
        if data is None or data.empty:
            print("❌ Failed to fetch data")
            return None
        
        # Filter to only target date (9:15 AM to 3:30 PM)
        data['date'] = pd.to_datetime(data['timestamp']).dt.date
        target_date_only = target_date.date()
        
        day_data = data[data['date'] == target_date_only].copy()
        
        if day_data.empty:
            print(f"❌ No data available for {date_str}")
            print(f"   Possible reasons:")
            print(f"   - Market holiday")
            print(f"   - Weekend")
            print(f"   - Data not yet available (too recent)")
            print(f"   - Try dates from 2-3 weeks ago")
            return None
        
        print(f"✅ Fetched {len(day_data)} candles for {date_str}")
        
        # Calculate indicators on full dataset (including previous days)
        full_data = self.technical_analyzer.calculate_all_indicators(data)
        
        # Re-add date column after indicators (in case it was removed)
        if 'date' not in full_data.columns:
            full_data['date'] = pd.to_datetime(full_data['timestamp']).dt.date
        
        # Return only target date data with indicators
        day_data_with_indicators = full_data[full_data['date'] == target_date_only].copy()
        
        return day_data_with_indicators
    
    def backtest_day(self, date_str):
        """
        Backtest a single day
        
        Args:
            date_str: Date to backtest (YYYY-MM-DD)
        """
        print("\n" + "="*60)
        print(f"📅 BACKTESTING: {date_str}")
        print("="*60 + "\n")
        
        # Fetch data
        day_data = self.fetch_historical_data(date_str)
        
        if day_data is None:
            return False
        
        # Reset capital
        self.paper_trading.capital = INITIAL_CAPITAL
        self.paper_trading.positions = {}
        self.daily_start_capital = INITIAL_CAPITAL
        
        # Get market context (simplified for backtest)
        market_detection = self.market_detector.detect_condition(day_data, {})
        market_condition = market_detection['condition'] if isinstance(market_detection, dict) else market_detection
        
        market_context = {
            'market_condition': market_condition,
            'news_sentiment': {'sentiment_score': 0},  # Neutral for backtest
            'timestamp': datetime.now()
        }
        
        print(f"🌍 Market Condition: {market_condition}")
        print(f"💰 Starting Capital: ₹{INITIAL_CAPITAL:,}\n")
        
        # Simulate trading through the day
        scan_count = 0
        
        # Process every 5th candle (simulate 5-minute scans)
        for i in range(50, len(day_data), 1):  # Start after warmup period
            scan_count += 1
            
            # Get data up to current candle
            current_data = day_data.iloc[:i+1].copy()
            current_time = current_data['timestamp'].iloc[-1]
            spot_price = current_data['close'].iloc[-1]
            
            # Skip if after 2:30 PM (no new entries)
            if current_time.hour >= 14 and current_time.minute >= 30:
                continue
            
            print(f"\n{'─'*60}")
            print(f"🔍 Scan #{scan_count} - {current_time.strftime('%I:%M %p')}")
            print(f"💹 NIFTY: ₹{spot_price:.2f}")
            
            # Check daily loss limit
            daily_pnl = self.paper_trading.capital - self.daily_start_capital
            if daily_pnl <= -MAX_DAILY_LOSS:
                print(f"🛑 Daily loss limit hit: ₹{daily_pnl:.2f}")
                break
            
            # Check existing positions
            open_positions = self.paper_trading.get_all_positions()
            print(f"📦 Open Positions: {len(open_positions)}/{MAX_POSITIONS}")
            
            # Update and check exits
            for pos_id, position in list(open_positions.items()):
                chain_data = self.options_chain.fetch_option_chain(spot_price)
                
                # Find current option
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
                    
                    self.paper_trading.update_position_greeks(
                        pos_id, current_premium, current_option
                    )
                    
                    should_exit, reason = self.paper_trading.check_exit_conditions(
                        pos_id, current_premium, current_option
                    )
                    
                    if should_exit:
                        print(f"🚪 Exiting: {reason}")
                        result = self.paper_trading.execute_sell_option(
                            pos_id, current_premium, reason
                        )
                        
                        if result['success']:
                            # Learn from trade
                            self.feedback_loop.process_trade_result(
                                position['strategy'],
                                result['pnl'],
                                market_context
                            )
            
            # Check if can open new positions
            if len(open_positions) >= MAX_POSITIONS:
                continue
            
            # Generate signal
            signal = self.signal_generator.generate_signal(
                current_data, market_context, spot_price, current_time=current_time
            )
            
            # DEBUG: Show individual strategy signals
            if 'signals' in signal:
                print(f"  📊 Strategy Signals:")
                for strat_signal in signal['signals']:
                    print(f"     • {strat_signal['strategy']}: {strat_signal['action']} ({strat_signal['confidence']:.0f}%) - {strat_signal['reason']}")
            
            print(f"📡 Final Signal: {signal['action']} ({signal['confidence']:.0f}%)")
            if signal.get('reason'):
                print(f"   Reason: {signal['reason']}")
            
            # Execute if high confidence
            # Training mode: 50% threshold (more trades for learning)
            # Live mode: 65% threshold (selective, high quality)
            if signal['action'] in ['BUY_CALL', 'BUY_PUT'] and signal['confidence'] >= 50:
                selected_option = signal['selected_option']
                
                if selected_option:
                    print(f"💼 {selected_option['strike']} {selected_option['option_type']} @ ₹{selected_option['ltp']:.2f}")
                    
                    result = self.paper_trading.execute_buy_option(
                        selected_option,
                        strategy='Backtest',
                        reason=signal['reason'],
                        lots=1
                    )
        
        # Close all positions at end of day
        print(f"\n{'='*60}")
        print("⏰ End of Day - Closing All Positions")
        print(f"{'='*60}\n")
        
        open_positions = self.paper_trading.get_all_positions()
        if open_positions:
            spot_price = day_data['close'].iloc[-1]
            chain_data = self.options_chain.fetch_option_chain(spot_price)
            
            current_premiums = {}
            for pos_id, position in open_positions.items():
                for opt in chain_data['options']:
                    if opt['strike'] == position['strike']:
                        if position['option_type'] == 'CE':
                            current_premiums[pos_id] = opt['call']['ltp']
                        else:
                            current_premiums[pos_id] = opt['put']['ltp']
            
            self.paper_trading.close_all_positions(current_premiums, "EOD")
        
        # Show results
        self.show_results()
        
        return True
    
    def show_results(self):
        """Show backtest results"""
        print("\n" + "="*60)
        print("📊 BACKTEST RESULTS")
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
        
        if stats['total_trades'] > 0:
            avg_pnl = stats['total_pnl'] / stats['total_trades']
            print(f"💵 Avg P&L per Trade: ₹{avg_pnl:.2f}")
        
        print("="*60)
    
    def backtest_multiple_days(self, start_date, end_date):
        """
        Backtest multiple days
        
        Args:
            start_date: Start date (YYYY-MM-DD)
            end_date: End date (YYYY-MM-DD)
        """
        start = datetime.strptime(start_date, '%Y-%m-%d')
        end = datetime.strptime(end_date, '%Y-%m-%d')
        
        current = start
        total_days = 0
        successful_days = 0
        
        while current <= end:
            date_str = current.strftime('%Y-%m-%d')
            
            # Skip weekends
            if current.weekday() < 5:  # Monday = 0, Friday = 4
                success = self.backtest_day(date_str)
                total_days += 1
                if success:
                    successful_days += 1
            
            current += timedelta(days=1)
        
        print(f"\n✅ Backtested {successful_days}/{total_days} days")

def main():
    """Main entry point"""
    
    if len(sys.argv) < 2:
        print("Usage:")
        print("  Single day:    python backtest_options.py 2026-04-15")
        print("  Multiple days: python backtest_options.py 2026-04-01 2026-04-15")
        print("\nExample:")
        print("  python backtest_options.py 2026-04-22")
        return
    
    backtester = OptionsBacktester()
    
    # Login
    if not backtester.login():
        print("❌ Cannot proceed without login")
        return
    
    # Single day or range
    if len(sys.argv) == 2:
        # Single day
        date_str = sys.argv[1]
        backtester.backtest_day(date_str)
    else:
        # Multiple days
        start_date = sys.argv[1]
        end_date = sys.argv[2]
        backtester.backtest_multiple_days(start_date, end_date)

if __name__ == "__main__":
    main()
