"""
Strategy Pool - Manage and evaluate multiple strategies
"""
from config.config import TRADING_TYPE

# Import appropriate strategies based on trading type
if TRADING_TYPE == 'OPTIONS':
    from strategies.options_strategies import get_options_strategies as get_all_strategies
else:
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
        
        # Count votes
        buy_votes = 0
        sell_votes = 0
        hold_votes = 0
        
        for signal in signals:
            # PAPER TRADING: Don't weight by performance (no history yet)
            # Use equal weight for all strategies
            weight = 1.0
            
            # Map options actions to equity actions
            action = signal['action']
            if action == 'BUY_CALL':
                action = 'BUY'
            elif action == 'BUY_PUT':
                action = 'SELL'
            
            if action == 'BUY':
                buy_score += signal['confidence'] * weight
                buy_votes += 1
                reasons.append(f"{signal['strategy']}: {signal['reason']}")
            elif action == 'SELL':
                sell_score += signal['confidence'] * weight
                sell_votes += 1
                reasons.append(f"{signal['strategy']}: {signal['reason']}")
            else:
                hold_votes += 1
            
            total_weight += weight
        
        # Normalize scores by number of voting strategies (not total weight)
        # This way a single 60% vote stays at 60%, not diluted
        if buy_votes > 0:
            buy_score = buy_score / buy_votes
        if sell_votes > 0:
            sell_score = sell_score / sell_votes
        
        # SINGLE STRATEGY MODE: If only 1 strategy, use its signal directly
        if len(signals) == 1:
            signal = signals[0]
            if signal['action'] == 'BUY':
                return {
                    'action': 'BUY',
                    'confidence': signal['confidence'],
                    'reason': signal['reason'],
                    'signals': signals
                }
            elif signal['action'] == 'SELL':
                return {
                    'action': 'SELL',
                    'confidence': signal['confidence'],
                    'reason': signal['reason'],
                    'signals': signals
                }
            else:
                return {
                    'action': 'HOLD',
                    'confidence': signal['confidence'],
                    'reason': signal['reason'],
                    'signals': signals
                }
        
        # PAPER TRADING MODE: Allow single strong signal to trigger (1 vote minimum)
        if buy_votes >= 1 and buy_votes > sell_votes and buy_score > 50:
            confidence = max(buy_score, 52)
            return {
                'action': 'BUY',
                'confidence': confidence,
                'reason': f"{buy_votes} strategy bullish | " + ' | '.join(reasons[:2]),
                'signals': signals
            }
        elif sell_votes >= 1 and sell_votes > buy_votes and sell_score > 50:
            confidence = max(sell_score, 52)
            return {
                'action': 'SELL',
                'confidence': confidence,
                'reason': f"{sell_votes} strategy bearish | " + ' | '.join(reasons[:2]),
                'signals': signals
            }
        
        # MULTI-STRATEGY MODE: Majority voting - require at least 2 votes for action
        elif buy_votes >= 2 and buy_votes > sell_votes:  # At least 2 BUY votes
            confidence = max(buy_score, 52)  # Minimum 52% confidence
            return {
                'action': 'BUY',
                'confidence': confidence,
                'reason': f"{buy_votes} strategies bullish | " + ' | '.join(reasons[:2]),
                'signals': signals
            }
        elif sell_votes >= 2 and sell_votes > buy_votes:  # At least 2 SELL votes
            confidence = max(sell_score, 52)  # Minimum 52% confidence
            return {
                'action': 'SELL',
                'confidence': confidence,
                'reason': f"{sell_votes} strategies bearish | " + ' | '.join(reasons[:2]),
                'signals': signals
            }
        
        # Original weighted scoring for strong signals
        elif buy_score > sell_score and buy_score > 50:  # Lowered from 55 to 50
            return {
                'action': 'BUY',
                'confidence': buy_score,
                'reason': ' | '.join(reasons[:3]),
                'signals': signals
            }
        elif sell_score > buy_score and sell_score > 50:  # Lowered from 55 to 50
            return {
                'action': 'SELL',
                'confidence': sell_score,
                'reason': ' | '.join(reasons[:3]),
                'signals': signals
            }
        
        # Weak signals
        elif buy_score > sell_score and buy_score > 45:
            return {
                'action': 'BUY',
                'confidence': buy_score,
                'reason': 'Weak bullish bias | ' + ' | '.join(reasons[:2]) if reasons else 'Weak bullish bias',
                'signals': signals
            }
        elif sell_score > buy_score and sell_score > 45:
            return {
                'action': 'SELL',
                'confidence': sell_score,
                'reason': 'Weak bearish bias | ' + ' | '.join(reasons[:2]) if reasons else 'Weak bearish bias',
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
