"""
Market Conditions Detector - Identify current market state
"""
import numpy as np

class MarketConditionDetector:
    """Detect and classify market conditions"""
    
    def __init__(self):
        self.current_condition = 'UNKNOWN'
    
    def detect_condition(self, nifty_data, market_data):
        """
        Detect current market condition
        
        Returns: 'BULL_TRENDING', 'BEAR_TRENDING', 'SIDEWAYS', 'HIGH_VOLATILITY'
        """
        
        if nifty_data.empty or len(nifty_data) < 20:
            return 'UNKNOWN'
        
        # Calculate metrics
        returns = nifty_data['close'].pct_change()
        volatility = returns.std() * np.sqrt(252)  # Annualized
        
        # Trend detection
        sma_20 = nifty_data['close'].rolling(20).mean().iloc[-1]
        sma_50 = nifty_data['close'].rolling(50).mean().iloc[-1] if len(nifty_data) >= 50 else sma_20
        current_price = nifty_data['close'].iloc[-1]
        
        # Price change
        price_change_20d = ((current_price - nifty_data['close'].iloc[-20]) / nifty_data['close'].iloc[-20]) * 100
        
        # Determine condition
        if volatility > 0.25:  # High volatility
            condition = 'HIGH_VOLATILITY'
        elif current_price > sma_20 > sma_50 and price_change_20d > 3:
            condition = 'BULL_TRENDING'
        elif current_price < sma_20 < sma_50 and price_change_20d < -3:
            condition = 'BEAR_TRENDING'
        else:
            condition = 'SIDEWAYS'
        
        self.current_condition = condition
        
        return {
            'condition': condition,
            'volatility': volatility,
            'price_change_20d': price_change_20d,
            'trend_strength': abs(price_change_20d)
        }
    
    def get_fii_dii_sentiment(self, fii_dii_data):
        """Analyze FII/DII activity"""
        if not fii_dii_data:
            return 'NEUTRAL'
        
        # Parse FII/DII data and determine sentiment
        # This is a placeholder - actual implementation depends on data structure
        
        return 'NEUTRAL'
    
    def get_global_market_impact(self, global_data):
        """Assess global market impact on Indian markets"""
        
        # Check US markets, Asian markets, crude oil, etc.
        # This is a placeholder
        
        return {
            'us_markets': 'NEUTRAL',
            'asian_markets': 'NEUTRAL',
            'crude_oil': 'NEUTRAL',
            'overall_impact': 'NEUTRAL'
        }
    
    def should_trade_today(self, market_context):
        """Determine if conditions are favorable for trading"""
        
        condition = market_context.get('condition', 'UNKNOWN')
        volatility = market_context.get('volatility', 0)
        news_sentiment = market_context.get('news_sentiment', {}).get('sentiment_score', 0)
        
        # Don't trade in extreme conditions
        if condition == 'HIGH_VOLATILITY' and volatility > 0.35:
            return False, "Volatility too high"
        
        if news_sentiment < -0.7:
            return False, "Extremely negative market sentiment"
        
        if condition == 'UNKNOWN':
            return False, "Unable to determine market condition"
        
        return True, "Conditions favorable for trading"
