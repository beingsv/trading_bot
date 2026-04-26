"""
Options Greeks Calculator
Calculate Delta, Gamma, Theta, Vega for options pricing
"""

import numpy as np
from scipy.stats import norm
import math

class OptionsGreeksCalculator:
    """Calculate options Greeks using Black-Scholes model"""
    
    def __init__(self):
        self.risk_free_rate = 0.065  # 6.5% (India RBI rate 2026)
    
    def calculate_greeks(self, spot_price, strike_price, days_to_expiry, 
                        implied_volatility, option_type='CE'):
        """
        Calculate all Greeks for an option
        
        Args:
            spot_price: Current index price
            strike_price: Option strike price
            days_to_expiry: Days until expiry
            implied_volatility: IV (as decimal, e.g., 0.15 for 15%)
            option_type: 'CE' (call) or 'PE' (put)
        
        Returns:
            dict with delta, gamma, theta, vega, premium
        """
        
        if days_to_expiry <= 0:
            # Expiry day - intrinsic value only
            if option_type == 'CE':
                intrinsic = max(0, spot_price - strike_price)
            else:
                intrinsic = max(0, strike_price - spot_price)
            
            return {
                'premium': intrinsic,
                'delta': 1.0 if intrinsic > 0 else 0.0,
                'gamma': 0.0,
                'theta': 0.0,
                'vega': 0.0,
                'intrinsic_value': intrinsic,
                'time_value': 0.0
            }
        
        # Time to expiry in years
        T = days_to_expiry / 365.0
        
        # Black-Scholes calculations
        d1 = (np.log(spot_price / strike_price) + 
              (self.risk_free_rate + 0.5 * implied_volatility ** 2) * T) / \
             (implied_volatility * np.sqrt(T))
        
        d2 = d1 - implied_volatility * np.sqrt(T)
        
        # Calculate Greeks
        if option_type == 'CE':
            # Call option
            delta = norm.cdf(d1)
            premium = (spot_price * norm.cdf(d1) - 
                      strike_price * np.exp(-self.risk_free_rate * T) * norm.cdf(d2))
            intrinsic = max(0, spot_price - strike_price)
        else:
            # Put option
            delta = -norm.cdf(-d1)
            premium = (strike_price * np.exp(-self.risk_free_rate * T) * norm.cdf(-d2) - 
                      spot_price * norm.cdf(-d1))
            intrinsic = max(0, strike_price - spot_price)
        
        # Common Greeks
        gamma = norm.pdf(d1) / (spot_price * implied_volatility * np.sqrt(T))
        theta = (-(spot_price * norm.pdf(d1) * implied_volatility) / (2 * np.sqrt(T)) -
                self.risk_free_rate * strike_price * np.exp(-self.risk_free_rate * T) * 
                (norm.cdf(d2) if option_type == 'CE' else norm.cdf(-d2)))
        theta = theta / 365  # Per day
        vega = spot_price * norm.pdf(d1) * np.sqrt(T) / 100  # Per 1% change in IV
        
        time_value = premium - intrinsic
        
        return {
            'premium': max(0, premium),
            'delta': delta,
            'gamma': gamma,
            'theta': theta,
            'vega': vega,
            'intrinsic_value': intrinsic,
            'time_value': max(0, time_value),
            'iv': implied_volatility
        }
    
    def estimate_iv_from_premium(self, spot_price, strike_price, days_to_expiry,
                                 market_premium, option_type='CE', initial_guess=0.20):
        """
        Estimate implied volatility from market premium (Newton-Raphson method)
        """
        
        if days_to_expiry <= 0:
            return 0.0
        
        iv = initial_guess
        max_iterations = 50
        tolerance = 0.0001
        
        for i in range(max_iterations):
            greeks = self.calculate_greeks(spot_price, strike_price, days_to_expiry, iv, option_type)
            calculated_premium = greeks['premium']
            vega = greeks['vega']
            
            diff = calculated_premium - market_premium
            
            if abs(diff) < tolerance:
                return iv
            
            if vega == 0:
                break
            
            # Newton-Raphson update
            iv = iv - diff / (vega * 100)
            
            # Keep IV in reasonable range
            iv = max(0.05, min(1.0, iv))
        
        return iv
    
    def get_moneyness(self, spot_price, strike_price, option_type='CE'):
        """
        Determine if option is ITM, ATM, or OTM
        """
        diff_percent = abs((spot_price - strike_price) / spot_price) * 100
        
        if diff_percent < 0.5:
            return 'ATM'
        
        if option_type == 'CE':
            if spot_price > strike_price:
                return 'ITM'
            else:
                return 'OTM'
        else:  # PE
            if spot_price < strike_price:
                return 'ITM'
            else:
                return 'OTM'
    
    def calculate_breakeven(self, strike_price, premium, option_type='CE'):
        """Calculate breakeven price for the option"""
        if option_type == 'CE':
            return strike_price + premium
        else:
            return strike_price - premium
