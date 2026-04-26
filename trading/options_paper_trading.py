"""
Options Paper Trading Engine - Simulate options trades
"""
from datetime import datetime, time
from config.config import (
    INITIAL_CAPITAL, STOP_LOSS_PERCENT, TAKE_PROFIT_PERCENT,
    MAX_THETA_PERCENT, INTRADAY_ONLY, EXIT_ALL_BY_HOUR, EXIT_ALL_BY_MINUTE,
    INDEX_CONFIG, PRIMARY_INDEX, POSITION_SIZE_PERCENT
)

class OptionsPaperTradingEngine:
    """Simulate options trading with virtual money"""
    
    def __init__(self, storage, initial_capital=INITIAL_CAPITAL):
        self.storage = storage
        self.capital = initial_capital
        self.initial_capital = initial_capital
        self.positions = {}  # {position_id: {...option details...}}
        self.trade_history = []
        self.position_counter = 0
        self.index_config = INDEX_CONFIG[PRIMARY_INDEX]
        self.total_pnl = 0  # Track total P&L from closed trades
    
    def get_portfolio_value(self, current_option_prices):
        """
        Calculate total portfolio value
        current_option_prices: dict of {position_id: current_premium}
        """
        portfolio_value = self.capital
        
        for pos_id, position in self.positions.items():
            if pos_id in current_option_prices:
                current_premium = current_option_prices[pos_id]
                lots = position['lots']
                lot_size = self.index_config['lot_size']
                position_value = current_premium * lots * lot_size
                portfolio_value += position_value
        
        return portfolio_value
    
    def can_open_position(self, premium, lots=1):
        """Check if we can afford to open position"""
        lot_size = self.index_config['lot_size']
        cost = premium * lots * lot_size
        max_position_value = self.capital * (POSITION_SIZE_PERCENT / 100)
        
        return cost <= self.capital and cost <= max_position_value
    
    def calculate_options_charges(self, trade_value, is_buy=True):
        """
        Calculate brokerage and charges for options trade
        """
        from config.config import (
            BROKERAGE_PER_TRADE, STT_OPTIONS_PERCENT,
            TRANSACTION_CHARGES_PERCENT, GST_PERCENT, STAMP_DUTY_PERCENT
        )
        
        # Flat brokerage for options
        brokerage = BROKERAGE_PER_TRADE
        
        # STT (only on sell side for options)
        stt = 0 if is_buy else (trade_value * STT_OPTIONS_PERCENT / 100)
        
        # Transaction charges (F&O)
        transaction_charges = trade_value * TRANSACTION_CHARGES_PERCENT / 100
        
        # GST on brokerage + transaction charges
        gst = (brokerage + transaction_charges) * GST_PERCENT / 100
        
        # Stamp duty (only on buy side)
        stamp_duty = (trade_value * STAMP_DUTY_PERCENT / 100) if is_buy else 0
        
        total_charges = brokerage + stt + transaction_charges + gst + stamp_duty
        
        return round(total_charges, 2)
    
    def execute_buy_option(self, option_data, strategy, reason="", lots=1):
        """
        Execute buy option order
        
        Args:
            option_data: dict with strike, option_type, premium, greeks, etc.
            strategy: strategy name
            reason: trade reason
            lots: number of lots to buy
        """
        lot_size = self.index_config['lot_size']
        premium = option_data['ltp']
        
        # Calculate cost
        cost = premium * lots * lot_size
        charges = self.calculate_options_charges(cost, is_buy=True)
        total_cost = cost + charges
        
        if total_cost > self.capital:
            return {'success': False, 'reason': 'Insufficient capital'}
        
        # Deduct from capital
        self.capital -= total_cost
        
        # Create position
        self.position_counter += 1
        position_id = f"OPT_{self.position_counter}"
        
        self.positions[position_id] = {
            'position_id': position_id,
            'symbol': PRIMARY_INDEX,
            'strike': option_data['strike'],
            'option_type': option_data['option_type'],
            'entry_premium': premium,
            'current_premium': premium,
            'lots': lots,
            'lot_size': lot_size,
            'quantity': lots * lot_size,
            'entry_time': datetime.now(),
            'strategy': strategy,
            'entry_charges': charges,
            'entry_delta': option_data.get('delta', 0),
            'entry_theta': option_data.get('theta', 0),
            'entry_iv': option_data.get('iv', 0),
            'days_to_expiry': option_data.get('days_to_expiry', 0),
            'reason': reason
        }
        
        # Log trade
        self.storage.save_trade(
            symbol=f"{PRIMARY_INDEX}_{option_data['strike']}_{option_data['option_type']}",
            strategy=strategy,
            action='BUY',
            price=premium,
            quantity=lots,
            pnl=0,
            reason=reason
        )
        
        print(f"✅ BUY {lots} lot {PRIMARY_INDEX} {option_data['strike']} {option_data['option_type']} @ ₹{premium:.2f}")
        print(f"   Delta: {option_data.get('delta', 0):.2f} | Theta: {option_data.get('theta', 0):.2f} | Charges: ₹{charges:.2f}")
        print(f"   Capital: ₹{self.capital:.2f}")
        
        return {
            'success': True,
            'position_id': position_id,
            'action': 'BUY',
            'premium': premium,
            'lots': lots,
            'charges': charges
        }
    
    def execute_sell_option(self, position_id, current_premium, reason=""):
        """Execute sell option order (close position)"""
        
        if position_id not in self.positions:
            return {'success': False, 'reason': 'Position not found'}
        
        position = self.positions[position_id]
        lots = position['lots']
        lot_size = position['lot_size']
        entry_premium = position['entry_premium']
        entry_charges = position['entry_charges']
        
        # Calculate proceeds
        proceeds = current_premium * lots * lot_size
        exit_charges = self.calculate_options_charges(proceeds, is_buy=False)
        net_proceeds = proceeds - exit_charges
        
        # Calculate P&L
        cost_basis = entry_premium * lots * lot_size
        total_charges = entry_charges + exit_charges
        pnl = net_proceeds - cost_basis - entry_charges
        pnl_percent = (pnl / (cost_basis + entry_charges)) * 100
        
        # Update capital
        self.capital += net_proceeds
        
        # Calculate holding time
        holding_time = (datetime.now() - position['entry_time']).total_seconds() / 60  # minutes
        
        # Log trade
        self.storage.save_trade(
            symbol=f"{position['symbol']}_{position['strike']}_{position['option_type']}",
            strategy=position['strategy'],
            action='SELL',
            price=current_premium,
            quantity=lots,
            pnl=pnl,
            reason=reason
        )
        
        # Save to history
        self.trade_history.append({
            'position_id': position_id,
            'symbol': position['symbol'],
            'strike': position['strike'],
            'option_type': position['option_type'],
            'entry_premium': entry_premium,
            'exit_premium': current_premium,
            'lots': lots,
            'pnl': pnl,
            'pnl_percent': pnl_percent,
            'holding_time_minutes': holding_time,
            'exit_reason': reason
        })
        
        # Update total P&L
        self.total_pnl += pnl
        
        # Remove position
        del self.positions[position_id]
        
        emoji = "🟢" if pnl > 0 else "🔴"
        print(f"{emoji} SELL {lots} lot {position['symbol']} {position['strike']} {position['option_type']} @ ₹{current_premium:.2f}")
        print(f"   P&L: ₹{pnl:.2f} ({pnl_percent:.2f}%) | Held: {holding_time:.0f}min | Charges: ₹{total_charges:.2f}")
        print(f"   Capital: ₹{self.capital:.2f}")
        
        return {
            'success': True,
            'action': 'SELL',
            'pnl': pnl,
            'pnl_percent': pnl_percent,
            'charges': total_charges
        }
    
    def check_exit_conditions(self, position_id, current_premium, current_greeks):
        """
        Check if position should be exited
        Returns: (should_exit, reason)
        """
        
        if position_id not in self.positions:
            return False, ""
        
        position = self.positions[position_id]
        entry_premium = position['entry_premium']
        
        # Calculate P&L percent
        pnl_percent = ((current_premium - entry_premium) / entry_premium) * 100
        
        # 1. Stop Loss
        if pnl_percent <= -STOP_LOSS_PERCENT:
            return True, f"Stop loss hit: {pnl_percent:.1f}%"
        
        # 2. Take Profit
        if pnl_percent >= TAKE_PROFIT_PERCENT:
            return True, f"Take profit hit: {pnl_percent:.1f}%"
        
        # 3. Theta Decay (if theta is eating too much premium)
        if current_greeks:
            theta = abs(current_greeks.get('theta', 0))
            theta_percent = (theta / current_premium) * 100 if current_premium > 0 else 0
            
            if theta_percent > MAX_THETA_PERCENT:
                return True, f"High theta decay: {theta_percent:.1f}%"
        
        # 4. Intraday Exit Time (3:15 PM)
        if INTRADAY_ONLY:
            current_time = datetime.now().time()
            exit_time = time(EXIT_ALL_BY_HOUR, EXIT_ALL_BY_MINUTE)
            
            if current_time >= exit_time:
                return True, "Market close - intraday exit"
        
        # 5. Near expiry with loss (don't hold losing positions to expiry)
        days_to_expiry = position.get('days_to_expiry', 7)
        if days_to_expiry == 0 and pnl_percent < -10:
            return True, "Expiry day - cutting loss"
        
        return False, ""
    
    def update_position_greeks(self, position_id, current_premium, current_greeks):
        """Update position with current premium and Greeks"""
        if position_id in self.positions:
            self.positions[position_id]['current_premium'] = current_premium
            if current_greeks:
                self.positions[position_id]['current_delta'] = current_greeks.get('delta', 0)
                self.positions[position_id]['current_theta'] = current_greeks.get('theta', 0)
                self.positions[position_id]['current_iv'] = current_greeks.get('iv', 0)
    
    def get_position(self, position_id):
        """Get position details"""
        return self.positions.get(position_id)
    
    def get_all_positions(self):
        """Get all open positions"""
        return self.positions
    
    def get_total_pnl(self):
        """Get total P&L from all closed trades (not including open positions)"""
        return self.total_pnl
    
    def get_statistics(self):
        """Get trading statistics"""
        total_pnl = sum([t['pnl'] for t in self.trade_history])
        winning_trades = len([t for t in self.trade_history if t['pnl'] > 0])
        losing_trades = len([t for t in self.trade_history if t['pnl'] <= 0])
        total_trades = len(self.trade_history)
        
        win_rate = (winning_trades / total_trades * 100) if total_trades > 0 else 0
        roi = ((self.capital - self.initial_capital) / self.initial_capital * 100)
        
        avg_holding_time = sum([t['holding_time_minutes'] for t in self.trade_history]) / total_trades if total_trades > 0 else 0
        
        return {
            'capital': self.capital,
            'initial_capital': self.initial_capital,
            'total_pnl': total_pnl,
            'roi': roi,
            'total_trades': total_trades,
            'winning_trades': winning_trades,
            'losing_trades': losing_trades,
            'win_rate': win_rate,
            'open_positions': len(self.positions),
            'avg_holding_time_minutes': avg_holding_time
        }
    
    def close_all_positions(self, current_premiums, reason="Market close"):
        """Close all open positions (for end of day)"""
        results = []
        
        for position_id in list(self.positions.keys()):
            if position_id in current_premiums:
                result = self.execute_sell_option(
                    position_id,
                    current_premiums[position_id],
                    reason
                )
                results.append(result)
        
        return results
