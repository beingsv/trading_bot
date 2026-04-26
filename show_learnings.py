"""
Show what the bot learned from trading
"""
import pandas as pd
from data.storage import DataStorage
from learning.feedback_loop import FeedbackLoop
from strategies.strategy_pool import StrategyPool

# Initialize
storage = DataStorage()
strategy_pool = StrategyPool(storage)
feedback_loop = FeedbackLoop(storage, strategy_pool)

print("=" * 60)
print("📚 BOT LEARNING SUMMARY")
print("=" * 60)

# Get all trades directly from database
trades_df = pd.read_sql_query('SELECT * FROM trades ORDER BY timestamp', storage.conn)

if trades_df.empty:
    print("\n❌ No trades found in database")
else:
    print(f"\n📊 Total Trades: {len(trades_df)}")
    print(f"✅ Winning Trades: {len(trades_df[trades_df['pnl'] > 0])}")
    print(f"❌ Losing Trades: {len(trades_df[trades_df['pnl'] <= 0])}")
    print(f"💰 Total P&L: ₹{trades_df['pnl'].sum():.2f}")
    
    if len(trades_df) > 0:
        win_rate = len(trades_df[trades_df['pnl'] > 0]) / len(trades_df) * 100
        print(f"🎯 Win Rate: {win_rate:.1f}%")
    
    print("\n" + "=" * 60)
    print("📝 TRADE DETAILS")
    print("=" * 60)
    
    for idx, trade in trades_df.iterrows():
        emoji = "🟢" if trade['pnl'] > 0 else "🔴"
        print(f"\n{emoji} Trade #{idx + 1}")
        print(f"   Symbol: {trade['symbol']}")
        print(f"   Strategy: {trade['strategy']}")
        print(f"   Action: {trade['action']}")
        print(f"   Price: ₹{trade['price']:.2f}")
        print(f"   Quantity: {trade['quantity']}")
        print(f"   P&L: ₹{trade['pnl']:.2f}")
        print(f"   Reason: {trade['reason']}")
        print(f"   Time: {trade['timestamp']}")

# Strategy performance
print("\n" + "=" * 60)
print("🎯 STRATEGY PERFORMANCE")
print("=" * 60)

perf_df = storage.get_all_strategies_performance()

if perf_df.empty:
    print("\n❌ No strategy performance data yet")
else:
    for idx, strat in perf_df.iterrows():
        print(f"\n📊 {strat['strategy_name']}")
        print(f"   Total Trades: {strat['total_trades']}")
        print(f"   Winning: {strat['winning_trades']}")
        print(f"   Losing: {strat['losing_trades']}")
        print(f"   Win Rate: {strat['win_rate']:.1f}%")
        print(f"   Total P&L: ₹{strat['total_pnl']:.2f}")
        print(f"   Avg P&L: ₹{strat['avg_pnl']:.2f}")

# Recommendations
print("\n" + "=" * 60)
print("💡 RECOMMENDATIONS")
print("=" * 60)

# Analyze the trades
for idx, trade in trades_df.iterrows():
    trade_result = {
        'symbol': trade['symbol'],
        'strategy': trade['strategy'],
        'pnl': trade['pnl'],
        'pnl_percent': (trade['pnl'] / (trade['price'] * trade['quantity'])) * 100 if trade['quantity'] > 0 else 0
    }
    market_context = {
        'condition': 'SIDEWAYS',  # From today's trading
        'news_sentiment': {'sentiment_score': 0}
    }
    feedback_loop.analyze_trade(trade_result, market_context)

recommendations = feedback_loop.get_recommendations()
for rec in recommendations:
    print(f"\n{rec}")

print("\n" + "=" * 60)
print("🧠 KEY LEARNINGS")
print("=" * 60)

if feedback_loop.learnings:
    for learning in feedback_loop.learnings:
        print(f"\n{learning['outcome']}: {learning['strategy']}")
        print(f"   P&L: ₹{learning['pnl']:.2f} ({learning['pnl_percent']:.2f}%)")
        print(f"   Market: {learning['market_condition']}")
        print(f"   Lesson: {learning['lesson']}")
else:
    print("\n❌ No learnings recorded yet")

print("\n" + "=" * 60)
