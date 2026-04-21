"""
Feedback Loop - Learn from trading mistakes and successes
"""
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

class FeedbackLoop:
    """Analyze trades and learn from mistakes"""
    
    def __init__(self, storage, strategy_pool):
        self.storage = storage
        self.strategy_pool = strategy_pool
        self.learnings = []
    
    def analyze_trade(self, trade_result, market_context):
        """Analyze a completed trade"""
        
        learning = {
            'timestamp': datetime.now(),
            'symbol': trade_result['symbol'],
            'strategy': trade_result.get('strategy', 'Unknown'),
            'pnl': trade_result['pnl'],
            'pnl_percent': trade_result['pnl_percent'],
            'market_condition': market_context.get('condition', 'UNKNOWN'),
            'news_sentiment': market_context.get('news_sentiment', {}).get('sentiment_score', 0)
        }
        
        # Classify as success or failure
        if trade_result['pnl'] > 0:
            learning['outcome'] = 'SUCCESS'
            learning['lesson'] = self._extract_success_pattern(trade_result, market_context)
        else:
            learning['outcome'] = 'FAILURE'
            learning['lesson'] = self._extract_failure_pattern(trade_result, market_context)
        
        self.learnings.append(learning)
        
        # Update strategy performance
        self.strategy_pool.update_strategy_performance(
            learning['strategy'],
            trade_result
        )
        
        return learning
    
    def _extract_success_pattern(self, trade, market_context):
        """Extract what worked in successful trade"""
        lessons = []
        
        # Market condition
        condition = market_context.get('condition', 'UNKNOWN')
        lessons.append(f"Strategy worked well in {condition} market")
        
        # Sentiment alignment
        sentiment = market_context.get('news_sentiment', {}).get('sentiment_score', 0)
        if sentiment > 0.2:
            lessons.append("Positive news sentiment supported the trade")
        
        return " | ".join(lessons)
    
    def _extract_failure_pattern(self, trade, market_context):
        """Extract what went wrong in failed trade"""
        lessons = []
        
        # Market condition mismatch
        condition = market_context.get('condition', 'UNKNOWN')
        lessons.append(f"Strategy underperformed in {condition} market")
        
        # Sentiment conflict
        sentiment = market_context.get('news_sentiment', {}).get('sentiment_score', 0)
        if sentiment < -0.2:
            lessons.append("Negative news sentiment worked against the trade")
        
        # Loss magnitude
        if trade['pnl_percent'] < -3:
            lessons.append("Stop loss was too wide, consider tighter risk management")
        
        return " | ".join(lessons)
    
    def get_strategy_insights(self, strategy_name, days=30):
        """Get insights for a specific strategy"""
        trades = self.storage.get_strategy_trades(strategy_name, days)
        
        if trades.empty:
            return {"message": "No trades found for this strategy"}
        
        winning_trades = trades[trades['pnl'] > 0]
        losing_trades = trades[trades['pnl'] <= 0]
        
        insights = {
            'total_trades': len(trades),
            'win_rate': len(winning_trades) / len(trades) * 100,
            'avg_win': winning_trades['pnl'].mean() if not winning_trades.empty else 0,
            'avg_loss': losing_trades['pnl'].mean() if not losing_trades.empty else 0,
            'total_pnl': trades['pnl'].sum(),
            'best_trade': trades['pnl'].max(),
            'worst_trade': trades['pnl'].min()
        }
        
        # Risk-reward ratio
        if insights['avg_loss'] != 0:
            insights['risk_reward_ratio'] = abs(insights['avg_win'] / insights['avg_loss'])
        else:
            insights['risk_reward_ratio'] = 0
        
        return insights
    
    def get_market_condition_performance(self):
        """Analyze performance across different market conditions"""
        learnings_df = pd.DataFrame(self.learnings)
        
        if learnings_df.empty:
            return {}
        
        performance = {}
        
        for condition in learnings_df['market_condition'].unique():
            condition_trades = learnings_df[learnings_df['market_condition'] == condition]
            
            performance[condition] = {
                'total_trades': len(condition_trades),
                'success_rate': len(condition_trades[condition_trades['outcome'] == 'SUCCESS']) / len(condition_trades) * 100,
                'avg_pnl': condition_trades['pnl'].mean()
            }
        
        return performance
    
    def get_recommendations(self):
        """Get actionable recommendations based on learnings"""
        recommendations = []
        
        # Analyze recent performance
        recent_learnings = [l for l in self.learnings[-20:]]
        
        if not recent_learnings:
            return ["Continue paper trading to gather more data"]
        
        # Check win rate
        successes = len([l for l in recent_learnings if l['outcome'] == 'SUCCESS'])
        win_rate = successes / len(recent_learnings) * 100
        
        if win_rate < 40:
            recommendations.append("⚠️ Win rate is low. Consider reducing position sizes.")
        elif win_rate > 60:
            recommendations.append("✅ Good win rate. Strategy is working well.")
        
        # Check sentiment alignment
        sentiment_aligned = [l for l in recent_learnings 
                           if (l['pnl'] > 0 and l['news_sentiment'] > 0) or 
                              (l['pnl'] < 0 and l['news_sentiment'] < 0)]
        
        if len(sentiment_aligned) > len(recent_learnings) * 0.6:
            recommendations.append("📰 News sentiment is a strong indicator. Continue monitoring.")
        
        # Strategy-specific recommendations
        perf_report = self.strategy_pool.get_performance_report()
        if perf_report:
            best_strategy = perf_report[0]
            recommendations.append(f"🎯 Best performing strategy: {best_strategy['strategy']} (Win rate: {best_strategy['win_rate']:.1f}%)")
        
        return recommendations
