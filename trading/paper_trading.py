"""
Paper Trading Engine - Simulate trades without real money
"""
from datetime import datetime
from config.config import INITIAL_CAPITAL, MAX_POSITION_SIZE, STOP_LOSS_PERCENT, TAKE_PROFIT_PERCENT

class PaperTradingEngine:
    """Simulate trading with virtual money"""
    
    def __init__(self, storage, initial_capital=INITIAL_CAPITAL):
        self.storage = storage
        self.capital = initial_capital
        self.initial_capital = initial_capital
        self.positions = {}  # {symbol: {'quantity': int, 'entry_price': float, 'strategy': str}}
        self.trade_history = []
    
    def get_portfolio_value(self, current_prices):
        """Calculate total portfolio value"""
        portfolio_value = self.capital
        
        for symbol, position in self.positions.items():
            if symbol in current_prices:
                portfolio_value += position['quantity'] * current_prices[symbol]
        
        return portfolio_value
    
    def can_buy(self, symbol, price, quantity):
        """Check if we can afford to buy"""
        cost = price * quantity
        max_position_value = self.capital * MAX_POSITION_SIZE
        
        return cost <= self.capital and cost <= max_position_value
    
    def execute_buy(self, symbol, price, quantity, strategy, reason=""):
        """Execute buy order"""
        cost = price * quantity
        
        if not self.can_buy(symbol, price, quantity):
            return {'success': False, 'reason': 'Insufficient capital or exceeds position limit'}
        
        self.capital -= cost
        
        if symbol in self.positions:
            # Average down
            old_qty = self.positions[symbol]['quantity']
            old_price = self.positions[symbol]['entry_price']
            new_qty = old_qty + quantity
            new_avg_price = ((old_qty * old_price) + (quantity * price)) / new_qty
            
            self.positions[symbol] = {
                'quantity': new_qty,
                'entry_price': new_avg_price,
                'strategy': strategy
            }
        else:
            self.positions[symbol] = {
                'quantity': quantity,
                'entry_price': price,
                'strategy': strategy
            }
        
        # Log trade
        self.storage.save_trade(symbol, strategy, 'BUY', price, quantity, 0, reason)
        
        print(f"✅ BUY {quantity} {symbol} @ ₹{price:.2f} | Capital: ₹{self.capital:.2f}")
        
        return {'success': True, 'action': 'BUY', 'symbol': symbol, 'price': price, 'quantity': quantity}
    
    def execute_sell(self, symbol, price, strategy, reason=""):
        """Execute sell order"""
        if symbol not in self.positions:
            return {'success': False, 'reason': 'No position to sell'}
        
        position = self.positions[symbol]
        quantity = position['quantity']
        entry_price = position['entry_price']
        
        # Calculate P&L
        pnl = (price - entry_price) * quantity
        pnl_percent = ((price - entry_price) / entry_price) * 100
        
        # Update capital
        self.capital += price * quantity
        
        # Remove position
        del self.positions[symbol]
        
        # Log trade
        self.storage.save_trade(symbol, strategy, 'SELL', price, quantity, pnl, reason)
        
        # Update strategy performance
        trade_result = {
            'symbol': symbol,
            'pnl': pnl,
            'pnl_percent': pnl_percent,
            'entry_price': entry_price,
            'exit_price': price
        }
        
        self.trade_history.append(trade_result)
        
        emoji = "🟢" if pnl > 0 else "🔴"
        print(f"{emoji} SELL {quantity} {symbol} @ ₹{price:.2f} | P&L: ₹{pnl:.2f} ({pnl_percent:.2f}%) | Capital: ₹{self.capital:.2f}")
        
        return {
            'success': True,
            'action': 'SELL',
            'symbol': symbol,
            'price': price,
            'quantity': quantity,
            'pnl': pnl,
            'pnl_percent': pnl_percent
        }
    
    def check_stop_loss_take_profit(self, symbol, current_price):
        """Check if stop loss or take profit is hit"""
        if symbol not in self.positions:
            return None
        
        position = self.positions[symbol]
        entry_price = position['entry_price']
        pnl_percent = ((current_price - entry_price) / entry_price) * 100
        
        if pnl_percent <= -STOP_LOSS_PERCENT:
            return {'action': 'SELL', 'reason': f'Stop loss hit at {pnl_percent:.2f}%'}
        
        if pnl_percent >= TAKE_PROFIT_PERCENT:
            return {'action': 'SELL', 'reason': f'Take profit hit at {pnl_percent:.2f}%'}
        
        return None
    
    def get_position(self, symbol):
        """Get current position for symbol"""
        return self.positions.get(symbol)
    
    def get_statistics(self):
        """Get trading statistics"""
        total_pnl = sum([t['pnl'] for t in self.trade_history])
        winning_trades = len([t for t in self.trade_history if t['pnl'] > 0])
        losing_trades = len([t for t in self.trade_history if t['pnl'] <= 0])
        total_trades = len(self.trade_history)
        
        win_rate = (winning_trades / total_trades * 100) if total_trades > 0 else 0
        roi = ((self.capital - self.initial_capital) / self.initial_capital * 100)
        
        return {
            'capital': self.capital,
            'total_pnl': total_pnl,
            'roi': roi,
            'total_trades': total_trades,
            'winning_trades': winning_trades,
            'losing_trades': losing_trades,
            'win_rate': win_rate,
            'open_positions': len(self.positions)
        }
