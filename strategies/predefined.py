"""
Predefined Trading Strategies
"""
from strategies.base_strategy import BaseStrategy
import numpy as np

class RSIStrategy(BaseStrategy):
    """RSI-based mean reversion strategy"""
    
    def __init__(self):
        super().__init__("RSI_Strategy")
        self.oversold = 35  # More sensitive
        self.overbought = 65  # More sensitive
    
    def generate_signal(self, data, market_context):
        if data.empty or 'RSI' not in data.columns:
            return {'action': 'HOLD', 'confidence': 0, 'reason': 'Insufficient data'}
        
        rsi = data['RSI'].iloc[-1]
        
        if rsi < self.oversold:
            return {'action': 'BUY', 'confidence': 70, 'reason': f'RSI oversold at {rsi:.2f}'}
        elif rsi > self.overbought:
            return {'action': 'SELL', 'confidence': 70, 'reason': f'RSI overbought at {rsi:.2f}'}
        
        return {'action': 'HOLD', 'confidence': 50, 'reason': f'RSI neutral at {rsi:.2f}'}


class MACDStrategy(BaseStrategy):
    """MACD crossover strategy"""
    
    def __init__(self):
        super().__init__("MACD_Strategy")
    
    def generate_signal(self, data, market_context):
        if data.empty or 'MACD_12_26_9' not in data.columns:
            return {'action': 'HOLD', 'confidence': 0, 'reason': 'Insufficient data'}
        
        macd = data['MACD_12_26_9'].iloc[-1]
        signal = data['MACDs_12_26_9'].iloc[-1]
        prev_macd = data['MACD_12_26_9'].iloc[-2]
        prev_signal = data['MACDs_12_26_9'].iloc[-2]
        
        # Bullish crossover
        if prev_macd < prev_signal and macd > signal:
            return {'action': 'BUY', 'confidence': 75, 'reason': 'MACD bullish crossover'}
        
        # Bearish crossover
        if prev_macd > prev_signal and macd < signal:
            return {'action': 'SELL', 'confidence': 75, 'reason': 'MACD bearish crossover'}
        
        return {'action': 'HOLD', 'confidence': 50, 'reason': 'No MACD crossover'}


class MovingAverageCrossover(BaseStrategy):
    """Moving average crossover strategy"""
    
    def __init__(self):
        super().__init__("MA_Crossover")
    
    def generate_signal(self, data, market_context):
        if data.empty or 'SMA_20' not in data.columns or 'SMA_50' not in data.columns:
            return {'action': 'HOLD', 'confidence': 0, 'reason': 'Insufficient data'}
        
        sma_20 = data['SMA_20'].iloc[-1]
        sma_50 = data['SMA_50'].iloc[-1]
        prev_sma_20 = data['SMA_20'].iloc[-2]
        prev_sma_50 = data['SMA_50'].iloc[-2]
        
        # Golden cross
        if prev_sma_20 < prev_sma_50 and sma_20 > sma_50:
            return {'action': 'BUY', 'confidence': 80, 'reason': 'Golden cross detected'}
        
        # Death cross
        if prev_sma_20 > prev_sma_50 and sma_20 < sma_50:
            return {'action': 'SELL', 'confidence': 80, 'reason': 'Death cross detected'}
        
        return {'action': 'HOLD', 'confidence': 50, 'reason': 'No MA crossover'}


class BollingerBandsStrategy(BaseStrategy):
    """Bollinger Bands mean reversion"""
    
    def __init__(self):
        super().__init__("Bollinger_Bands")
    
    def generate_signal(self, data, market_context):
        if data.empty or 'BBL_20_2.0' not in data.columns:
            return {'action': 'HOLD', 'confidence': 0, 'reason': 'Insufficient data'}
        
        price = data['close'].iloc[-1]
        lower_band = data['BBL_20_2.0'].iloc[-1]
        upper_band = data['BBU_20_2.0'].iloc[-1]
        
        if price < lower_band:
            return {'action': 'BUY', 'confidence': 65, 'reason': 'Price below lower Bollinger Band'}
        elif price > upper_band:
            return {'action': 'SELL', 'confidence': 65, 'reason': 'Price above upper Bollinger Band'}
        
        return {'action': 'HOLD', 'confidence': 50, 'reason': 'Price within Bollinger Bands'}


class TrendFollowingStrategy(BaseStrategy):
    """Multi-indicator trend following"""
    
    def __init__(self):
        super().__init__("Trend_Following")
    
    def generate_signal(self, data, market_context):
        if data.empty or len(data) < 50:
            return {'action': 'HOLD', 'confidence': 0, 'reason': 'Insufficient data'}
        
        # Check multiple trend indicators
        price = data['close'].iloc[-1]
        sma_20 = data['SMA_20'].iloc[-1]
        sma_50 = data['SMA_50'].iloc[-1]
        
        trend_score = 0
        
        # Price above MAs
        if price > sma_20:
            trend_score += 1
        if price > sma_50:
            trend_score += 1
        if sma_20 > sma_50:
            trend_score += 1
        
        # ADX for trend strength
        if 'ADX_14' in data.columns and data['ADX_14'].iloc[-1] > 25:
            trend_score += 1
        
        if trend_score >= 3:
            return {'action': 'BUY', 'confidence': 70, 'reason': f'Strong uptrend (score: {trend_score})'}
        elif trend_score <= 1:
            return {'action': 'SELL', 'confidence': 70, 'reason': f'Strong downtrend (score: {trend_score})'}
        
        return {'action': 'HOLD', 'confidence': 50, 'reason': 'Weak trend'}


class NewsSentimentStrategy(BaseStrategy):
    """News sentiment-based strategy"""
    
    def __init__(self):
        super().__init__("News_Sentiment")
    
    def generate_signal(self, data, market_context):
        sentiment = market_context.get('news_sentiment', {})
        sentiment_score = sentiment.get('sentiment_score', 0)
        
        if sentiment_score > 0.3:
            return {'action': 'BUY', 'confidence': 60, 'reason': f'Positive news sentiment: {sentiment_score:.2f}'}
        elif sentiment_score < -0.3:
            return {'action': 'SELL', 'confidence': 60, 'reason': f'Negative news sentiment: {sentiment_score:.2f}'}
        
        return {'action': 'HOLD', 'confidence': 40, 'reason': 'Neutral news sentiment'}


class CandlestickPatternStrategy(BaseStrategy):
    """Advanced candlestick pattern recognition strategy"""
    
    def __init__(self):
        super().__init__("Candlestick_Patterns")
        
        # Pattern weights (based on reliability)
        self.bullish_patterns = {
            'morning_star': 85,
            'three_white_soldiers': 80,
            'bullish_engulfing': 75,
            'piercing_pattern': 70,
            'hammer': 65,
            'bullish_harami': 60,
            'dragonfly_doji': 60,
            'bullish_marubozu': 70
        }
        
        self.bearish_patterns = {
            'evening_star': 85,
            'three_black_crows': 80,
            'bearish_engulfing': 75,
            'dark_cloud_cover': 70,
            'shooting_star': 65,
            'bearish_harami': 60,
            'gravestone_doji': 60,
            'bearish_marubozu': 70
        }
        
        self.neutral_patterns = {
            'doji': 50,
            'spinning_top': 50,
            'inside_bar': 55
        }
    
    def generate_signal(self, data, market_context):
        if data.empty or len(data) < 3:
            return {'action': 'HOLD', 'confidence': 0, 'reason': 'Insufficient data'}
        
        # Import here to avoid circular dependency
        from analysis.technical import TechnicalAnalyzer
        analyzer = TechnicalAnalyzer()
        
        # Detect patterns
        patterns = analyzer.detect_patterns(data)
        
        # Calculate bullish score
        bullish_score = 0
        bullish_found = []
        for pattern, confidence in self.bullish_patterns.items():
            if patterns.get(pattern, False):
                bullish_score += confidence
                bullish_found.append(pattern.replace('_', ' ').title())
        
        # Calculate bearish score
        bearish_score = 0
        bearish_found = []
        for pattern, confidence in self.bearish_patterns.items():
            if patterns.get(pattern, False):
                bearish_score += confidence
                bearish_found.append(pattern.replace('_', ' ').title())
        
        # Volume confirmation (if available)
        volume_boost = 1.0
        if 'volume' in data.columns and len(data) >= 20:
            avg_volume = data['volume'].rolling(20).mean().iloc[-1]
            current_volume = data['volume'].iloc[-1]
            if current_volume > avg_volume * 1.5:
                volume_boost = 1.2  # 20% boost for high volume
        
        # Apply volume boost
        bullish_score *= volume_boost
        bearish_score *= volume_boost
        
        # Determine action
        if bullish_score > bearish_score and bullish_score > 60:
            confidence = min(bullish_score, 90)  # Cap at 90%
            patterns_str = ', '.join(bullish_found[:2])  # Show top 2
            reason = f"Bullish patterns: {patterns_str}"
            if volume_boost > 1.0:
                reason += " (High volume confirmation)"
            return {'action': 'BUY', 'confidence': confidence, 'reason': reason}
        
        elif bearish_score > bullish_score and bearish_score > 60:
            confidence = min(bearish_score, 90)
            patterns_str = ', '.join(bearish_found[:2])
            reason = f"Bearish patterns: {patterns_str}"
            if volume_boost > 1.0:
                reason += " (High volume confirmation)"
            return {'action': 'SELL', 'confidence': confidence, 'reason': reason}
        
        # Check for neutral/indecision patterns
        neutral_found = [p for p in self.neutral_patterns if patterns.get(p, False)]
        if neutral_found:
            return {'action': 'HOLD', 'confidence': 50, 
                   'reason': f"Indecision pattern: {neutral_found[0].replace('_', ' ').title()}"}
        
        return {'action': 'HOLD', 'confidence': 45, 'reason': 'No significant patterns detected'}


# Factory to get all predefined strategies
def get_all_strategies():
    """Return list of all predefined strategies"""
    return [
        RSIStrategy(),
        MACDStrategy(),
        MovingAverageCrossover(),
        BollingerBandsStrategy(),
        TrendFollowingStrategy(),
        NewsSentimentStrategy(),
        CandlestickPatternStrategy()  # New 7th strategy!
    ]
