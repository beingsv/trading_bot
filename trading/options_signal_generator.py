"""
Options Signal Generator - Generate BUY_CALL/BUY_PUT signals
"""
from datetime import datetime, time
from config.config import (
    NO_TRADE_AFTER_HOUR, NO_TRADE_AFTER_MINUTE,
    MIN_DELTA, MAX_IV_PERCENTILE
)

class OptionsSignalGenerator:
    """Generate options trading signals"""
    
    def __init__(self, strategy_pool, technical_analyzer, options_chain_fetcher):
        self.strategy_pool = strategy_pool
        self.technical_analyzer = technical_analyzer
        self.options_chain = options_chain_fetcher
    
    def generate_signal(self, index_data, market_context, spot_price, current_time=None):
        """
        Generate options trading signal
        
        Args:
            index_data: NIFTY index price data (for technical analysis)
            market_context: market conditions, news, etc.
            spot_price: current NIFTY spot price
            current_time: optional datetime for backtesting (uses now() if None)
        
        Returns:
            dict: {
                'action': 'BUY_CALL'/'BUY_PUT'/'HOLD',
                'confidence': 0-100,
                'reason': str,
                'selected_option': dict (option data with strike, premium, greeks),
                'spot_price': float
            }
        """
        
        # Check if we should trade (time-based filter)
        if not self._can_trade_now(current_time):
            return {
                'action': 'HOLD',
                'confidence': 0,
                'reason': f'No trades after {NO_TRADE_AFTER_HOUR}:{NO_TRADE_AFTER_MINUTE:02d}',
                'selected_option': None,
                'spot_price': spot_price
            }
        
        # Get strategy consensus
        consensus = self.strategy_pool.get_consensus_signal(index_data, market_context)
        
        # Map equity signals to options signals
        if consensus['action'] == 'BUY':
            direction = 'BULLISH'
            option_action = 'BUY_CALL'
        elif consensus['action'] == 'SELL':
            direction = 'BEARISH'
            option_action = 'BUY_PUT'
        else:
            return {
                'action': 'HOLD',
                'confidence': consensus['confidence'],
                'reason': consensus['reason'],
                'selected_option': None,
                'spot_price': spot_price,
                'signals': consensus.get('signals', [])  # Pass through individual strategy signals
            }
        
        # Fetch options chain
        chain_data = self.options_chain.fetch_option_chain(spot_price)
        
        # Select best strike (ATM or OTM1)
        selected_option = self.options_chain.select_best_strike(
            chain_data, direction, strategy='ATM'
        )
        
        if not selected_option:
            return {
                'action': 'HOLD',
                'confidence': 0,
                'reason': 'No suitable option found',
                'selected_option': None,
                'spot_price': spot_price
            }
        
        # Apply options-specific filters
        filter_result = self._apply_options_filters(selected_option, consensus['confidence'])
        
        if not filter_result['passed']:
            return {
                'action': 'HOLD',
                'confidence': 0,
                'reason': filter_result['reason'],
                'selected_option': selected_option,
                'spot_price': spot_price
            }
        
        # Adjust confidence based on Greeks
        final_confidence = self._adjust_confidence_by_greeks(
            selected_option, consensus['confidence']
        )
        
        return {
            'action': option_action,
            'confidence': final_confidence,
            'reason': consensus['reason'],
            'selected_option': selected_option,
            'spot_price': spot_price,
            'chain_data': chain_data,
            'signals': consensus.get('signals', [])  # Pass through individual strategy signals
        }
    
    def _can_trade_now(self, current_time=None):
        """Check if current time allows trading"""
        if current_time is None:
            current_time = datetime.now()
        
        # Extract time if datetime object
        if isinstance(current_time, datetime):
            current_time = current_time.time()
        
        cutoff_time = time(NO_TRADE_AFTER_HOUR, NO_TRADE_AFTER_MINUTE)
        return current_time < cutoff_time
    
    def _apply_options_filters(self, option_data, base_confidence):
        """
        Apply options-specific filters
        Returns: {'passed': bool, 'reason': str}
        """
        
        # Filter 1: Delta check (ensure good directional exposure)
        delta = abs(option_data.get('delta', 0))
        if delta < MIN_DELTA:
            return {
                'passed': False,
                'reason': f'Delta too low: {delta:.2f} (min: {MIN_DELTA})'
            }
        
        # Filter 2: IV check (don't buy expensive options)
        # For now, we'll use a simple IV threshold
        # In production, compare against IV percentile
        iv = option_data.get('iv', 0)
        if iv > 0.40:  # 40% IV is quite high
            return {
                'passed': False,
                'reason': f'IV too high: {iv*100:.1f}% (expensive option)'
            }
        
        # Filter 3: Premium check (avoid very cheap options - likely to expire worthless)
        premium = option_data.get('ltp', 0)
        if premium < 10:
            return {
                'passed': False,
                'reason': f'Premium too low: ₹{premium:.2f} (high risk)'
            }
        
        # Filter 4: Moneyness check (prefer ATM or slight OTM)
        moneyness = option_data.get('moneyness', 'OTM')
        if moneyness not in ['ATM', 'OTM']:
            # ITM options are expensive and have less leverage
            pass  # Allow ITM for now
        
        return {'passed': True, 'reason': 'All filters passed'}
    
    def _adjust_confidence_by_greeks(self, option_data, base_confidence):
        """Adjust confidence based on Greeks quality"""
        
        confidence = base_confidence
        
        # Boost confidence for good delta
        delta = abs(option_data.get('delta', 0))
        if delta > 0.50:
            confidence += 5  # Strong directional exposure
        elif delta > 0.40:
            confidence += 2
        
        # Reduce confidence for high theta
        theta = abs(option_data.get('theta', 0))
        premium = option_data.get('ltp', 1)
        theta_percent = (theta / premium) * 100 if premium > 0 else 0
        
        if theta_percent > 10:
            confidence -= 5  # High time decay risk
        elif theta_percent > 5:
            confidence -= 2
        
        # Boost confidence for ATM options (best risk/reward)
        if option_data.get('moneyness') == 'ATM':
            confidence += 3
        
        return min(100, max(0, confidence))
    
    def should_exit_position(self, position, current_option_data, index_data, market_context):
        """
        Determine if we should exit an options position
        
        Returns: (should_exit, reason)
        """
        
        # Get current signal
        spot_price = index_data['close'].iloc[-1]
        signal = self.generate_signal(index_data, market_context, spot_price)
        
        # Exit if opposite signal with high confidence
        position_type = position['option_type']
        
        if position_type == 'CE' and signal['action'] == 'BUY_PUT' and signal['confidence'] > 70:
            return True, "Strong bearish signal (holding call)"
        
        if position_type == 'PE' and signal['action'] == 'BUY_CALL' and signal['confidence'] > 70:
            return True, "Strong bullish signal (holding put)"
        
        # Let paper trading engine handle stop loss, take profit, theta decay
        return False, ""
