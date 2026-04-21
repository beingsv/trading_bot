"""
Base Strategy Template
"""
from abc import ABC, abstractmethod

class BaseStrategy(ABC):
    """Base class for all trading strategies"""
    
    def __init__(self, name):
        self.name = name
        self.trades = []
        self.performance = {
            'total_trades': 0,
            'winning_trades': 0,
            'losing_trades': 0,
            'total_pnl': 0,
            'win_rate': 0
        }
    
    @abstractmethod
    def generate_signal(self, data, market_context):
        """
        Generate trading signal
        
        Args:
            data: DataFrame with OHLCV and indicators
            market_context: Dict with market conditions, news, etc.
        
        Returns:
            dict: {'action': 'BUY'/'SELL'/'HOLD', 'confidence': 0-100, 'reason': str}
        """
        pass
    
    def update_performance(self, trade_result):
        """Update strategy performance metrics"""
        self.trades.append(trade_result)
        self.performance['total_trades'] += 1
        
        if trade_result['pnl'] > 0:
            self.performance['winning_trades'] += 1
        else:
            self.performance['losing_trades'] += 1
        
        self.performance['total_pnl'] += trade_result['pnl']
        
        if self.performance['total_trades'] > 0:
            self.performance['win_rate'] = (
                self.performance['winning_trades'] / self.performance['total_trades']
            ) * 100
    
    def get_performance(self):
        """Get strategy performance metrics"""
        return self.performance
    
    def __str__(self):
        return f"Strategy: {self.name}"
