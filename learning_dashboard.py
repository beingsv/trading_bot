"""
Learning Dashboard - Shows what the bot learned
Run anytime to see bot's knowledge and insights
"""
import pandas as pd
from datetime import datetime, timedelta
from data.storage import DataStorage
from strategies.strategy_pool import StrategyPool
from learning.feedback_loop import FeedbackLoop

class LearningDashboard:
    """Display bot's learning insights"""
    
    def __init__(self):
        self.storage = DataStorage()
        self.strategy_pool = StrategyPool(self.storage)
        self.feedback_loop = FeedbackLoop(self.storage, self.strategy_pool)
    
    def show_dashboard(self, days=7):
        """Show complete learning dashboard"""
        
        print("\n" + "="*70)
        print("🧠 BOT LEARNING DASHBOARD")
        print("="*70)
        print(f"📅 Analysis Period: Last {days} days")
        print(f"🕐 Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("="*70)
        
        # 1. Overall Performance
        self.show_overall_performance(days)
        
        # 2. Strategy Intelligence
        self.show_strategy_intelligence()
        
        # 3. Market Condition Insights
        self.show_market_insights()
        
        # 4. Recent Learnings
        self.show_recent_learnings(days)
        
        # 5. Recommendations
        self.show_recommendations()
        
        # 6. Knowledge Base Stats
        self.show_knowledge_stats()
        
        print("\n" + "="*70)
        print("✅ Dashboard Complete")
        print("="*70 + "\n")
    
    def show_overall_performance(self, days):
        """Show overall trading performance"""
        print("\n📊 OVERALL PERFORMANCE")
        print("-" * 70)
        
        # Get trades from database
        query = f'''
            SELECT * FROM trades 
            WHERE timestamp >= datetime('now', '-{days} days')
        '''
        trades_df = pd.read_sql_query(query, self.storage.conn)
        
        if trades_df.empty:
            print("  No trades yet. Bot is still learning from observations.")
            return
        
        total_trades = len(trades_df)
        winning_trades = len(trades_df[trades_df['pnl'] > 0])
        losing_trades = len(trades_df[trades_df['pnl'] <= 0])
        total_pnl = trades_df['pnl'].sum()
        win_rate = (winning_trades / total_trades * 100) if total_trades > 0 else 0
        
        avg_win = trades_df[trades_df['pnl'] > 0]['pnl'].mean() if winning_trades > 0 else 0
        avg_loss = trades_df[trades_df['pnl'] <= 0]['pnl'].mean() if losing_trades > 0 else 0
        
        print(f"  📝 Total Trades: {total_trades}")
        print(f"  ✅ Winning Trades: {winning_trades}")
        print(f"  ❌ Losing Trades: {losing_trades}")
        print(f"  🎯 Win Rate: {win_rate:.1f}%")
        print(f"  💰 Total P&L: ₹{total_pnl:,.2f}")
        print(f"  📈 Avg Win: ₹{avg_win:,.2f}")
        print(f"  📉 Avg Loss: ₹{avg_loss:,.2f}")
        
        if avg_loss != 0:
            risk_reward = abs(avg_win / avg_loss)
            print(f"  ⚖️  Risk/Reward Ratio: {risk_reward:.2f}")
    
    def show_strategy_intelligence(self):
        """Show what bot learned about each strategy"""
        print("\n🎯 STRATEGY INTELLIGENCE")
        print("-" * 70)
        
        perf_df = self.storage.get_all_strategies_performance()
        
        if perf_df.empty:
            print("  No strategy data yet. Run backtest to train strategies.")
            return
        
        # Sort by win rate
        perf_df = perf_df.sort_values('win_rate', ascending=False)
        
        for idx, row in perf_df.iterrows():
            if row['total_trades'] == 0:
                continue
            
            # Emoji based on performance
            if row['win_rate'] >= 60:
                emoji = "🌟"
                status = "EXCELLENT"
            elif row['win_rate'] >= 55:
                emoji = "✅"
                status = "GOOD"
            elif row['win_rate'] >= 50:
                emoji = "📊"
                status = "AVERAGE"
            else:
                emoji = "⚠️"
                status = "NEEDS IMPROVEMENT"
            
            print(f"\n  {emoji} {row['strategy_name']} - {status}")
            print(f"     Trades: {row['total_trades']} | "
                  f"Win Rate: {row['win_rate']:.1f}% | "
                  f"P&L: ₹{row['total_pnl']:,.2f}")
            print(f"     Wins: {row['winning_trades']} | "
                  f"Losses: {row['losing_trades']} | "
                  f"Sharpe: {row['sharpe_ratio']:.2f}")
            
            # Bot's learning about this strategy
            if row['win_rate'] >= 60:
                print(f"     🧠 Bot learned: \"Trust this strategy - high success rate\"")
            elif row['win_rate'] < 45:
                print(f"     🧠 Bot learned: \"Use cautiously - underperforming\"")
    
    def show_market_insights(self):
        """Show what bot learned about market conditions"""
        print("\n🌍 MARKET CONDITION INSIGHTS")
        print("-" * 70)
        
        condition_perf = self.feedback_loop.get_market_condition_performance()
        
        if not condition_perf:
            print("  No market condition data yet.")
            return
        
        for condition, metrics in condition_perf.items():
            emoji = "📈" if metrics['success_rate'] >= 55 else "📉"
            
            print(f"\n  {emoji} {condition} Market:")
            print(f"     Trades: {metrics['total_trades']} | "
                  f"Success Rate: {metrics['success_rate']:.1f}% | "
                  f"Avg P&L: ₹{metrics['avg_pnl']:,.2f}")
            
            # Bot's learning
            if metrics['success_rate'] >= 60:
                print(f"     🧠 Bot learned: \"Strategies work well in {condition} conditions\"")
            elif metrics['success_rate'] < 45:
                print(f"     🧠 Bot learned: \"Be cautious in {condition} conditions\"")
    
    def show_recent_learnings(self, days):
        """Show recent specific learnings"""
        print("\n📚 RECENT LEARNINGS")
        print("-" * 70)
        
        # Get recent trades
        query = f'''
            SELECT * FROM trades 
            WHERE timestamp >= datetime('now', '-{days} days')
            ORDER BY timestamp DESC
            LIMIT 10
        '''
        recent_trades = pd.read_sql_query(query, self.storage.conn)
        
        if recent_trades.empty:
            print("  No recent trades to learn from yet.")
            return
        
        learnings = []
        
        # Analyze patterns
        for strategy in recent_trades['strategy'].unique():
            strategy_trades = recent_trades[recent_trades['strategy'] == strategy]
            wins = len(strategy_trades[strategy_trades['pnl'] > 0])
            total = len(strategy_trades)
            win_rate = (wins / total * 100) if total > 0 else 0
            
            if total >= 3:  # Only if enough data
                if win_rate >= 70:
                    learnings.append(f"  ✅ {strategy} is performing excellently ({win_rate:.0f}% win rate)")
                elif win_rate <= 30:
                    learnings.append(f"  ⚠️  {strategy} is struggling ({win_rate:.0f}% win rate)")
        
        # Time-based patterns
        recent_trades['hour'] = pd.to_datetime(recent_trades['timestamp']).dt.hour
        morning_trades = recent_trades[recent_trades['hour'] < 12]
        afternoon_trades = recent_trades[recent_trades['hour'] >= 12]
        
        if len(morning_trades) >= 3:
            morning_pnl = morning_trades['pnl'].mean()
            if morning_pnl > 0:
                learnings.append(f"  🌅 Morning trades are profitable (Avg: ₹{morning_pnl:.2f})")
        
        if len(afternoon_trades) >= 3:
            afternoon_pnl = afternoon_trades['pnl'].mean()
            if afternoon_pnl > 0:
                learnings.append(f"  🌆 Afternoon trades are profitable (Avg: ₹{afternoon_pnl:.2f})")
        
        # Symbol-based patterns
        for symbol in recent_trades['symbol'].unique():
            symbol_trades = recent_trades[recent_trades['symbol'] == symbol]
            if len(symbol_trades) >= 3:
                symbol_pnl = symbol_trades['pnl'].sum()
                if symbol_pnl > 500:
                    learnings.append(f"  💎 {symbol} is a strong performer (Total P&L: ₹{symbol_pnl:.2f})")
                elif symbol_pnl < -500:
                    learnings.append(f"  ⚠️  {symbol} is underperforming (Total P&L: ₹{symbol_pnl:.2f})")
        
        if learnings:
            for learning in learnings:
                print(learning)
        else:
            print("  Gathering more data to identify patterns...")
    
    def show_recommendations(self):
        """Show bot's recommendations"""
        print("\n💡 BOT'S RECOMMENDATIONS")
        print("-" * 70)
        
        recommendations = self.feedback_loop.get_recommendations()
        
        if recommendations:
            for rec in recommendations:
                print(f"  {rec}")
        else:
            print("  Continue trading to generate recommendations.")
    
    def show_knowledge_stats(self):
        """Show knowledge base statistics"""
        print("\n📊 KNOWLEDGE BASE STATISTICS")
        print("-" * 70)
        
        # Count total data points
        total_trades = pd.read_sql_query('SELECT COUNT(*) as count FROM trades', self.storage.conn)
        total_strategies = pd.read_sql_query('SELECT COUNT(*) as count FROM strategy_performance', self.storage.conn)
        
        trades_count = total_trades['count'].iloc[0]
        strategies_count = total_strategies['count'].iloc[0]
        
        print(f"  📝 Total Trades Recorded: {trades_count}")
        print(f"  🎯 Strategies Tracked: {strategies_count}")
        print(f"  🧠 Learning Sessions: {trades_count} (one per trade)")
        
        # Experience level
        if trades_count < 50:
            level = "BEGINNER 🌱"
            message = "Bot is learning the basics"
        elif trades_count < 200:
            level = "INTERMEDIATE 📈"
            message = "Bot has good understanding"
        elif trades_count < 500:
            level = "ADVANCED 🎯"
            message = "Bot has strong market knowledge"
        else:
            level = "EXPERT 🏆"
            message = "Bot is highly experienced"
        
        print(f"\n  🎓 Experience Level: {level}")
        print(f"     {message}")
        
        # Days of experience
        first_trade = pd.read_sql_query(
            'SELECT MIN(timestamp) as first_trade FROM trades', 
            self.storage.conn
        )
        
        if not first_trade.empty and first_trade['first_trade'].iloc[0]:
            first_date = pd.to_datetime(first_trade['first_trade'].iloc[0])
            days_active = (datetime.now() - first_date).days
            print(f"  📅 Days Active: {days_active}")
            print(f"  📊 Avg Trades/Day: {trades_count / max(days_active, 1):.1f}")

def main():
    """Main function"""
    dashboard = LearningDashboard()
    
    print("\n🧠 Bot Learning Dashboard")
    print("Choose time period:")
    print("  1. Today")
    print("  2. Last 7 days")
    print("  3. Last 30 days")
    print("  4. All time")
    
    choice = input("\nEnter choice (1-4) [default: 2]: ").strip() or "2"
    
    days_map = {
        "1": 1,
        "2": 7,
        "3": 30,
        "4": 10000  # All time
    }
    
    days = days_map.get(choice, 7)
    dashboard.show_dashboard(days)

if __name__ == "__main__":
    main()
