"""
Options Chain Data Fetcher
Fetch and parse options chain data from AngelOne
"""

import pandas as pd
from datetime import datetime, timedelta
from config.config import INDEX_CONFIG, PRIMARY_INDEX
from analysis.options_greeks import OptionsGreeksCalculator

class OptionsChainFetcher:
    """Fetch and analyze options chain data"""
    
    def __init__(self, angelone_api):
        self.api = angelone_api
        self.greeks_calc = OptionsGreeksCalculator()
        self.index_config = INDEX_CONFIG[PRIMARY_INDEX]
    
    def get_current_expiry(self):
        """Get the nearest weekly expiry date (Thursday for NIFTY)"""
        today = datetime.now()
        
        # Find next Thursday (NIFTY expiry)
        days_ahead = 3 - today.weekday()  # Thursday = 3
        if days_ahead <= 0:  # If today is Thursday or later
            days_ahead += 7
        
        expiry_date = today + timedelta(days=days_ahead)
        return expiry_date.strftime('%d%b%y').upper()  # Format: 24APR26
    
    def get_atm_strike(self, spot_price):
        """Get ATM strike price based on spot price"""
        strike_gap = self.index_config['strike_gap']
        atm_strike = round(spot_price / strike_gap) * strike_gap
        return atm_strike
    
    def get_strike_range(self, spot_price, num_strikes=5):
        """
        Get range of strikes around ATM
        
        Returns:
            list: [ATM-2, ATM-1, ATM, ATM+1, ATM+2]
        """
        atm = self.get_atm_strike(spot_price)
        strike_gap = self.index_config['strike_gap']
        
        strikes = []
        for i in range(-num_strikes, num_strikes + 1):
            strikes.append(atm + (i * strike_gap))
        
        return strikes
    
    def fetch_option_chain(self, spot_price):
        """
        Fetch options chain for current expiry
        
        Returns:
            dict: {
                'spot_price': float,
                'expiry': str,
                'days_to_expiry': int,
                'atm_strike': int,
                'options': [
                    {
                        'strike': int,
                        'call': {...},  # CE data with Greeks
                        'put': {...}    # PE data with Greeks
                    }
                ]
            }
        """
        
        expiry = self.get_current_expiry()
        atm_strike = self.get_atm_strike(spot_price)
        strikes = self.get_strike_range(spot_price, num_strikes=3)
        
        # Calculate days to expiry
        expiry_date = datetime.strptime(expiry, '%d%b%y')
        days_to_expiry = (expiry_date - datetime.now()).days
        
        options_data = []
        
        for strike in strikes:
            # For paper trading, we'll simulate option premiums
            # In live trading, fetch from AngelOne API
            
            call_data = self._simulate_option_data(
                spot_price, strike, days_to_expiry, 'CE'
            )
            
            put_data = self._simulate_option_data(
                spot_price, strike, days_to_expiry, 'PE'
            )
            
            options_data.append({
                'strike': strike,
                'call': call_data,
                'put': put_data
            })
        
        return {
            'spot_price': spot_price,
            'expiry': expiry,
            'days_to_expiry': days_to_expiry,
            'atm_strike': atm_strike,
            'options': options_data,
            'timestamp': datetime.now()
        }
    
    def _simulate_option_data(self, spot_price, strike, days_to_expiry, option_type):
        """
        Simulate option data for paper trading
        In live trading, replace with actual API call
        """
        
        # Estimate IV based on moneyness (realistic values)
        moneyness = self.greeks_calc.get_moneyness(spot_price, strike, option_type)
        
        if moneyness == 'ATM':
            iv = 0.15 + (0.05 * (7 - days_to_expiry) / 7)  # Higher IV near expiry
        elif moneyness == 'OTM':
            iv = 0.12 + (0.08 * (7 - days_to_expiry) / 7)
        else:  # ITM
            iv = 0.18 + (0.04 * (7 - days_to_expiry) / 7)
        
        # Calculate Greeks and premium
        greeks = self.greeks_calc.calculate_greeks(
            spot_price, strike, days_to_expiry, iv, option_type
        )
        
        # Add market data
        greeks.update({
            'strike': strike,
            'option_type': option_type,
            'ltp': greeks['premium'],  # Last traded price
            'bid': greeks['premium'] * 0.98,  # Simulate bid-ask spread
            'ask': greeks['premium'] * 1.02,
            'volume': 10000 if moneyness == 'ATM' else 5000,  # Simulate volume
            'oi': 50000 if moneyness == 'ATM' else 25000,  # Open interest
            'moneyness': moneyness
        })
        
        return greeks
    
    def select_best_strike(self, chain_data, direction, strategy='ATM'):
        """
        Select best strike based on strategy
        
        Args:
            chain_data: Options chain data
            direction: 'BULLISH' or 'BEARISH'
            strategy: 'ATM', 'OTM1', 'OTM2'
        
        Returns:
            dict: Selected option data
        """
        
        atm_strike = chain_data['atm_strike']
        strike_gap = self.index_config['strike_gap']
        
        # Determine target strike
        if strategy == 'ATM':
            target_strike = atm_strike
        elif strategy == 'OTM1':
            if direction == 'BULLISH':
                target_strike = atm_strike + strike_gap
            else:
                target_strike = atm_strike - strike_gap
        elif strategy == 'OTM2':
            if direction == 'BULLISH':
                target_strike = atm_strike + (2 * strike_gap)
            else:
                target_strike = atm_strike - (2 * strike_gap)
        else:
            target_strike = atm_strike
        
        # Find the option
        for option in chain_data['options']:
            if option['strike'] == target_strike:
                if direction == 'BULLISH':
                    return option['call']
                else:
                    return option['put']
        
        # Fallback to ATM
        for option in chain_data['options']:
            if option['strike'] == atm_strike:
                if direction == 'BULLISH':
                    return option['call']
                else:
                    return option['put']
        
        return None
