"""
Strategy Pool - Manage and evaluate multiple strategies
"""
from strategies.predefined import get_all_strategies
import numpy as np

class StrategyPool:
    """Manage multiple trading strategies"""
    
    def __init__(self, storage):
        self.storage = storage
        self.strategies = get_all_strategies()
        self.active_strategies = []
        self.load_performance()
    
    def load_performance(self):
        """Load historical performance from database"""
        perf_df = self.storage.get_all_strategies_performance()
        
        for strategy in self.strategies:
            matching = perf_df[perf_df['strategy_name'] == strategy.name]
            if not matching.empty:
                row = matching.iloc[0]
                strategy.performance = {
                    'total_trades': row['total_trades'],
                    'winning_trades': row['winning_trades'],
                    'losing_trades': row['losing_trades'],
                    'total_pnl': row['total_pnl'],
                    'win_rate': row['win_rate']
                }
    
    def get_all_signals(self, data, market_context):
        """Get signals from all strategies"""
        signals = []
        
        for strategy in self.strategies:
            signal = strategy.generate_signal(data, market_context)
            signal['strategy'] = strategy.name
            signal['performance'] = strategy.get_performance()
            signals.append(signal)
        
        return signals
    
    def get_consensus_signal(self, data, market_context):
        """Get weighted consensus from all strategies"""
        signals = self.get_all_signals(data, market_context)
        
        buy_score = 0
        sell_score = 0
        total_weight = 0
        reasons = []
        
        for signal in signals:
            # Weight by strategy performance
            win_rate = signal['performance'].get('win_rate', 50)
            weight = max(win_rate / 100, 0.3)  # Minimum 30% weight
            
            if signal['action'] == 'BUY':
                buy_score += signal['confidence'] * weight
                reasons.append(f"{signal['strategy']}: {signal['reason']}")
            elif signal['action'] == 'SELL':
                sell_score += signal['confidence'] * weight
                reasons.append(f"{signal['strategy']}: {signal['reason']}")
            
            total_weight += weight
        
        # Normalize scores
        if total_weight > 0:
            buy_score /= total_weight
            sell_score /= total_weight
        
        # Determine final action
        if buy_score > sell_score and buy_score > 60:
            return {
                'action': 'BUY',
                'confidence': buy_score,
                'reason': ' | '.join(reasons[:3]),
                'signals': signals
            }
        elif sell_score > buy_score and sell_score > 60:
            return {
                'action': 'SELL',
                'confidence': sell_score,
                'reason': ' | '.join(reasons[:3]),
                'signals': signals
            }
        
        return {
            'action': 'HOLD',
            'confidence': 50,
            'reason': 'No strong consensus',
            'signals': signals
        }
    
    def get_best_strategy(self, market_condition='ALL'):
        """Get best performing strategy for current market condition"""
        best_strategy = None
        best_score = -float('inf')
        
        for strategy in self.strategies:
            perf = strategy.get_performance()
            
            if perf['total_trades'] < 10:
                continue
            
            # Score based on win rate and total PnL
            score = perf['win_rate'] * 0.6 + (perf['total_pnl'] / 1000) * 0.4
            
            if score > best_score:
                best_score = score
                best_strategy = strategy
        
        return best_strategy
    
    def update_strategy_performance(self, strategy_name, trade_result):
        """Update performance for a strategy"""
        for strategy in self.strategies:
            if strategy.name == strategy_name:
                strategy.update_performance(trade_result)
                
                # Save to database
                self.storage.update_strategy_performance(
                    strategy_name,
                    strategy.get_performance()
                )
                break
    
    def get_performance_report(self):
        """Get performance report for all strategies"""
        report = []
        
        for strategy in self.strategies:
            perf = strategy.get_performance()
            report.append({
                'strategy': strategy.name,
                'total_trades': perf['total_trades'],
                'win_rate': perf['win_rate'],
                'total_pnl': perf['total_pnl']
            })
        
        return sorted(report, key=lambda x: x['win_rate'], reverse=True)
