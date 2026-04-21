"""
Signal Generator - Combine all analysis to generate trading signals
"""

class SignalGenerator:
    """Generate buy/sell signals from multiple sources"""
    
    def __init__(self, strategy_pool, technical_analyzer, news_analyzer):
        self.strategy_pool = strategy_pool
        self.technical_analyzer = technical_analyzer
        self.news_analyzer = news_analyzer
    
    def generate_signal(self, symbol, data, market_context):
        """
        Generate comprehensive trading signal
        
        Returns:
            dict: {
                'action': 'BUY'/'SELL'/'HOLD',
                'confidence': 0-100,
                'reason': str,
                'technical_score': float,
                'sentiment_score': float,
                'strategy_consensus': dict
            }
        """
        
        # Get strategy consensus
        consensus = self.strategy_pool.get_consensus_signal(data, market_context)
        
        # Get technical analysis score
        technical_score = self.technical_analyzer.get_signal_strength(data)
        
        # Get news sentiment
        news_sentiment = market_context.get('news_sentiment', {}).get('sentiment_score', 0)
        
        # Combine scores (more weight to strategies during backtest)
        final_score = (
            consensus['confidence'] * 0.6 +  # 60% weight to strategy consensus
            (technical_score + 50) * 0.3 +    # 30% weight to technical (normalized)
            (news_sentiment * 50 + 50) * 0.1  # 10% weight to news (normalized)
        )
        
        # Determine action
        action = consensus['action']
        
        # Override if market sentiment is very negative
        if news_sentiment < -0.5 and action == 'BUY':
            action = 'HOLD'
            reason = "Overridden: Very negative market sentiment"
        elif news_sentiment > 0.5 and action == 'SELL':
            action = 'HOLD'
            reason = "Overridden: Very positive market sentiment"
        else:
            reason = consensus['reason']
        
        return {
            'action': action,
            'confidence': final_score,
            'reason': reason,
            'technical_score': technical_score,
            'sentiment_score': news_sentiment,
            'strategy_consensus': consensus,
            'market_context': market_context
        }
    
    def should_exit_position(self, symbol, position, current_price, data, market_context):
        """Determine if we should exit an existing position"""
        
        # Check stop loss / take profit
        entry_price = position['entry_price']
        pnl_percent = ((current_price - entry_price) / entry_price) * 100
        
        # Get current signal
        signal = self.generate_signal(symbol, data, market_context)
        
        # Exit conditions
        if signal['action'] == 'SELL' and signal['confidence'] > 70:
            return True, "Strong sell signal"
        
        if pnl_percent < -2:  # Stop loss
            return True, f"Stop loss: {pnl_percent:.2f}%"
        
        if pnl_percent > 5:  # Take profit
            return True, f"Take profit: {pnl_percent:.2f}%"
        
        # Trend reversal
        trend = self.technical_analyzer.get_trend(data)
        if trend == 'DOWNTREND':
            return True, "Trend reversal detected"
        
        return False, ""
