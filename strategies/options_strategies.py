"""
Options Trading Strategies (Simplified - 3 Core Strategies)
"""

from strategies.base_strategy import BaseStrategy

class DirectionalOptionsStrategy(BaseStrategy):
    """
    Buy Call if bullish, Buy Put if bearish
    Based on technical indicators (RSI, MACD, trend)
    IMPROVED: More realistic thresholds
    """
    
    def __init__(self):
        super().__init__("Directional_Options")
    
    def generate_signal(self, data, market_context):
        if data.empty or len(data) < 50:
            return {'action': 'HOLD', 'confidence': 0, 'reason': 'Insufficient data'}
        
        # Get technical indicators
        rsi = data['RSI_14'].iloc[-1] if 'RSI_14' in data.columns else 50
        macd = data['MACD'].iloc[-1] if 'MACD' in data.columns else 0
        macd_signal = data['MACD_signal'].iloc[-1] if 'MACD_signal' in data.columns else 0
        
        # Trend analysis
        sma_20 = data['SMA_20'].iloc[-1] if 'SMA_20' in data.columns else data['close'].iloc[-1]
        sma_50 = data['SMA_50'].iloc[-1] if 'SMA_50' in data.columns else data['close'].iloc[-1]
        current_price = data['close'].iloc[-1]
        
        # Price momentum (last 5 candles)
        recent_prices = data['close'].iloc[-5:]
        price_change = ((recent_prices.iloc[-1] - recent_prices.iloc[0]) / recent_prices.iloc[0]) * 100
        
        # BULLISH Signals (Buy Call)
        bullish_score = 0
        reasons = []
        
        # RSI - More lenient thresholds
        if rsi < 45:  # Changed from 40
            bullish_score += 20
            reasons.append(f"RSI oversold ({rsi:.1f})")
        elif rsi < 50:
            bullish_score += 10
        
        # MACD
        if macd > macd_signal:
            bullish_score += 20
            reasons.append("MACD bullish")
        
        # Trend
        if current_price > sma_20:
            bullish_score += 15
            reasons.append("Above SMA20")
            if sma_20 > sma_50:
                bullish_score += 15
                reasons.append("Uptrend")
        
        # Momentum
        if price_change > 0.2:  # 0.2% up in last 5 candles
            bullish_score += 20
            reasons.append(f"Momentum up ({price_change:.2f}%)")
        
        # BEARISH Signals (Buy Put)
        bearish_score = 0
        bear_reasons = []
        
        # RSI
        if rsi > 55:  # Changed from 60
            bearish_score += 20
            bear_reasons.append(f"RSI overbought ({rsi:.1f})")
        elif rsi > 50:
            bearish_score += 10
        
        # MACD
        if macd < macd_signal:
            bearish_score += 20
            bear_reasons.append("MACD bearish")
        
        # Trend
        if current_price < sma_20:
            bearish_score += 15
            bear_reasons.append("Below SMA20")
            if sma_20 < sma_50:
                bearish_score += 15
                bear_reasons.append("Downtrend")
        
        # Momentum
        if price_change < -0.2:  # 0.2% down
            bearish_score += 20
            bear_reasons.append(f"Momentum down ({price_change:.2f}%)")
        
        # Decision
        if bullish_score > 50 and bullish_score > bearish_score:
            return {
                'action': 'BUY_CALL',
                'confidence': min(bullish_score, 85),
                'reason': ', '.join(reasons)
            }
        elif bearish_score > 50 and bearish_score > bullish_score:
            return {
                'action': 'BUY_PUT',
                'confidence': min(bearish_score, 85),
                'reason': ', '.join(bear_reasons)
            }
        else:
            return {
                'action': 'HOLD',
                'confidence': max(bullish_score, bearish_score),
                'reason': 'No clear directional signal'
            }


class BreakoutOptionsStrategy(BaseStrategy):
    """
    Buy Call on support breakout, Buy Put on resistance breakdown
    Uses support/resistance + volume confirmation
    """
    
    def __init__(self):
        super().__init__("Breakout_Options")
    
    def generate_signal(self, data, market_context):
        if data.empty or len(data) < 20:
            return {'action': 'HOLD', 'confidence': 0, 'reason': 'Insufficient data'}
        
        # Check for S/R data
        if 'support' not in data.columns or 'resistance' not in data.columns:
            return {'action': 'HOLD', 'confidence': 0, 'reason': 'Missing S/R data'}
        
        current_price = data['close'].iloc[-1]
        prev_price = data['close'].iloc[-2]
        support = data['support'].iloc[-1]
        resistance = data['resistance'].iloc[-1]
        
        # Volume confirmation
        current_volume = data['volume'].iloc[-1] if 'volume' in data.columns else 0
        avg_volume = data['volume'].iloc[-20:].mean() if 'volume' in data.columns else 1
        volume_surge = current_volume > (avg_volume * 1.5)
        
        # Breakout above resistance (Buy Call)
        if prev_price <= resistance and current_price > resistance:
            confidence = 75 if volume_surge else 60
            return {
                'action': 'BUY_CALL',
                'confidence': confidence,
                'reason': f'Breakout above resistance ₹{resistance:.0f}' + 
                         (' with volume' if volume_surge else '')
            }
        
        # Breakdown below support (Buy Put)
        if prev_price >= support and current_price < support:
            confidence = 75 if volume_surge else 60
            return {
                'action': 'BUY_PUT',
                'confidence': confidence,
                'reason': f'Breakdown below support ₹{support:.0f}' +
                         (' with volume' if volume_surge else '')
            }
        
        # Near resistance (potential rejection - Buy Put)
        dist_to_resistance = ((resistance - current_price) / current_price) * 100
        if 0 < dist_to_resistance < 0.3:  # Within 0.3%
            return {
                'action': 'BUY_PUT',
                'confidence': 55,
                'reason': f'Near resistance ₹{resistance:.0f}, potential rejection'
            }
        
        # Near support (potential bounce - Buy Call)
        dist_to_support = ((current_price - support) / current_price) * 100
        if 0 < dist_to_support < 0.3:  # Within 0.3%
            return {
                'action': 'BUY_CALL',
                'confidence': 55,
                'reason': f'Near support ₹{support:.0f}, potential bounce'
            }
        
        return {'action': 'HOLD', 'confidence': 50, 'reason': 'No breakout signal'}


class VWAPOptionsStrategy(BaseStrategy):
    """
    Trade based on VWAP (institutional price level)
    Buy Call when price bounces off VWAP from below
    Buy Put when price rejects VWAP from above
    """
    
    def __init__(self):
        super().__init__("VWAP_Options")
    
    def generate_signal(self, data, market_context):
        if data.empty or len(data) < 10:
            return {'action': 'HOLD', 'confidence': 0, 'reason': 'Insufficient data'}
        
        if 'vwap' not in data.columns:
            return {'action': 'HOLD', 'confidence': 0, 'reason': 'Missing VWAP data'}
        
        current_price = data['close'].iloc[-1]
        prev_price = data['close'].iloc[-2]
        vwap = data['vwap'].iloc[-1]
        
        # Distance from VWAP
        dist_from_vwap = ((current_price - vwap) / vwap) * 100
        prev_dist = ((prev_price - vwap) / vwap) * 100
        
        # Bounce off VWAP from below (Buy Call)
        if prev_dist < -0.2 and dist_from_vwap > -0.1:
            return {
                'action': 'BUY_CALL',
                'confidence': 70,
                'reason': f'Bounce off VWAP ₹{vwap:.0f} from below'
            }
        
        # Rejection at VWAP from above (Buy Put)
        if prev_dist > 0.2 and dist_from_vwap < 0.1:
            return {
                'action': 'BUY_PUT',
                'confidence': 70,
                'reason': f'Rejection at VWAP ₹{vwap:.0f} from above'
            }
        
        # Strong above VWAP (Buy Call)
        if dist_from_vwap > 0.5:
            return {
                'action': 'BUY_CALL',
                'confidence': 60,
                'reason': f'Strong above VWAP ₹{vwap:.0f}'
            }
        
        # Strong below VWAP (Buy Put)
        if dist_from_vwap < -0.5:
            return {
                'action': 'BUY_PUT',
                'confidence': 60,
                'reason': f'Weak below VWAP ₹{vwap:.0f}'
            }
        
        return {'action': 'HOLD', 'confidence': 50, 'reason': 'Price near VWAP, no clear signal'}


class MomentumOptionsStrategy(BaseStrategy):
    """
    Simple momentum strategy - trades on strong price movement
    More aggressive, generates more trades for learning
    PAPER TRADING MODE: Extra aggressive for testing
    """
    
    def __init__(self):
        super().__init__("Momentum_Options")
    
    def generate_signal(self, data, market_context):
        if data.empty or len(data) < 10:
            return {'action': 'HOLD', 'confidence': 0, 'reason': 'Insufficient data'}
        
        # Calculate momentum over different periods
        current_price = data['close'].iloc[-1]
        
        # 3-candle momentum (15 minutes)
        price_3 = data['close'].iloc[-3]
        momentum_3 = ((current_price - price_3) / price_3) * 100
        
        # 5-candle momentum (25 minutes)
        price_5 = data['close'].iloc[-5]
        momentum_5 = ((current_price - price_5) / price_5) * 100
        
        # 10-candle momentum (50 minutes)
        price_10 = data['close'].iloc[-10]
        momentum_10 = ((current_price - price_10) / price_10) * 100
        
        # Volume check
        current_volume = data['volume'].iloc[-1] if 'volume' in data.columns else 0
        avg_volume = data['volume'].iloc[-10:].mean() if 'volume' in data.columns else 1
        high_volume = current_volume > avg_volume
        
        # BULLISH Momentum (Buy Call)
        # PAPER TRADING: Lower thresholds for more trades
        if momentum_3 > 0.08 or momentum_5 > 0.15:  # Lowered from 0.15/0.25
            confidence = 60
            if momentum_3 > 0.08 and momentum_5 > 0.15:
                confidence = 70  # Both confirm
            if high_volume:
                confidence += 5
            
            return {
                'action': 'BUY_CALL',
                'confidence': min(confidence, 85),
                'reason': f'Bullish momentum: 3c={momentum_3:.2f}%, 5c={momentum_5:.2f}%'
            }
        
        # BEARISH Momentum (Buy Put)
        if momentum_3 < -0.08 or momentum_5 < -0.15:  # Lowered from -0.15/-0.25
            confidence = 60
            if momentum_3 < -0.08 and momentum_5 < -0.15:
                confidence = 70  # Both confirm
            if high_volume:
                confidence += 5
            
            return {
                'action': 'BUY_PUT',
                'confidence': min(confidence, 85),
                'reason': f'Bearish momentum: 3c={momentum_3:.2f}%, 5c={momentum_5:.2f}%'
            }
        
        # Moderate momentum signals (even lower threshold for paper trading)
        if momentum_5 > 0.05:  # Lowered from 0.1
            return {
                'action': 'BUY_CALL',
                'confidence': 52,
                'reason': f'Moderate bullish momentum: {momentum_5:.2f}%'
            }
        
        if momentum_5 < -0.05:  # Lowered from -0.1
            return {
                'action': 'BUY_PUT',
                'confidence': 52,
                'reason': f'Moderate bearish momentum: {momentum_5:.2f}%'
            }
        
        return {'action': 'HOLD', 'confidence': 50, 'reason': 'No momentum signal'}


class CandlePatternOptionsStrategy(BaseStrategy):
    """
    Professional candle pattern recognition strategy
    Identifies: Hammer, Shooting Star, Engulfing, Doji, etc.
    """
    
    def __init__(self):
        super().__init__("Candle_Pattern_Options")
    
    def generate_signal(self, data, market_context):
        if data.empty or len(data) < 3:
            return {'action': 'HOLD', 'confidence': 0, 'reason': 'Insufficient data'}
        
        # Get last 3 candles
        current = data.iloc[-1]
        prev = data.iloc[-2]
        prev2 = data.iloc[-3] if len(data) >= 3 else prev
        
        # Calculate candle properties
        current_body = abs(current['close'] - current['open'])
        current_range = current['high'] - current['low']
        current_upper_wick = current['high'] - max(current['open'], current['close'])
        current_lower_wick = min(current['open'], current['close']) - current['low']
        
        prev_body = abs(prev['close'] - prev['open'])
        prev_range = prev['high'] - prev['low']
        
        # Avoid division by zero
        if current_range == 0 or prev_range == 0:
            return {'action': 'HOLD', 'confidence': 50, 'reason': 'No price movement'}
        
        # Pattern detection
        patterns = []
        confidence = 50
        action = 'HOLD'
        
        # 1. BULLISH HAMMER (Buy Call)
        # Small body at top, long lower wick (2x body), small upper wick
        if (current_lower_wick > current_body * 2 and 
            current_upper_wick < current_body * 0.3 and
            current['close'] > current['open']):  # Green candle
            patterns.append('Bullish Hammer')
            action = 'BUY_CALL'
            confidence = 65
        
        # 2. SHOOTING STAR (Buy Put)
        # Small body at bottom, long upper wick (2x body), small lower wick
        if (current_upper_wick > current_body * 2 and 
            current_lower_wick < current_body * 0.3 and
            current['close'] < current['open']):  # Red candle
            patterns.append('Shooting Star')
            action = 'BUY_PUT'
            confidence = 65
        
        # 3. BULLISH ENGULFING (Buy Call)
        # Current green candle completely engulfs previous red candle
        if (prev['close'] < prev['open'] and  # Previous red
            current['close'] > current['open'] and  # Current green
            current['open'] < prev['close'] and  # Opens below prev close
            current['close'] > prev['open']):  # Closes above prev open
            patterns.append('Bullish Engulfing')
            action = 'BUY_CALL'
            confidence = 70
        
        # 4. BEARISH ENGULFING (Buy Put)
        # Current red candle completely engulfs previous green candle
        if (prev['close'] > prev['open'] and  # Previous green
            current['close'] < current['open'] and  # Current red
            current['open'] > prev['close'] and  # Opens above prev close
            current['close'] < prev['open']):  # Closes below prev open
            patterns.append('Bearish Engulfing')
            action = 'BUY_PUT'
            confidence = 70
        
        # 5. DOJI (Indecision - usually reversal)
        # Very small body (< 10% of range), equal wicks
        if current_body < current_range * 0.1:
            # Check trend before doji
            if prev['close'] > prev['open'] and prev2['close'] > prev2['open']:
                # Uptrend + Doji = potential reversal down
                patterns.append('Doji (Bearish Reversal)')
                action = 'BUY_PUT'
                confidence = 60
            elif prev['close'] < prev['open'] and prev2['close'] < prev2['open']:
                # Downtrend + Doji = potential reversal up
                patterns.append('Doji (Bullish Reversal)')
                action = 'BUY_CALL'
                confidence = 60
        
        # 6. THREE WHITE SOLDIERS (Buy Call)
        # Three consecutive green candles with higher closes
        if (current['close'] > current['open'] and
            prev['close'] > prev['open'] and
            prev2['close'] > prev2['open'] and
            current['close'] > prev['close'] > prev2['close']):
            patterns.append('Three White Soldiers')
            action = 'BUY_CALL'
            confidence = 75
        
        # 7. THREE BLACK CROWS (Buy Put)
        # Three consecutive red candles with lower closes
        if (current['close'] < current['open'] and
            prev['close'] < prev['open'] and
            prev2['close'] < prev2['open'] and
            current['close'] < prev['close'] < prev2['close']):
            patterns.append('Three Black Crows')
            action = 'BUY_PUT'
            confidence = 75
        
        # 8. MORNING STAR (Buy Call)
        # 3-candle pattern: Red, Small body, Green
        if (prev2['close'] < prev2['open'] and  # First red
            prev_body < prev_range * 0.3 and  # Middle small
            current['close'] > current['open'] and  # Last green
            current['close'] > (prev2['open'] + prev2['close']) / 2):  # Closes above midpoint
            patterns.append('Morning Star')
            action = 'BUY_CALL'
            confidence = 75
        
        # 9. EVENING STAR (Buy Put)
        # 3-candle pattern: Green, Small body, Red
        if (prev2['close'] > prev2['open'] and  # First green
            prev_body < prev_range * 0.3 and  # Middle small
            current['close'] < current['open'] and  # Last red
            current['close'] < (prev2['open'] + prev2['close']) / 2):  # Closes below midpoint
            patterns.append('Evening Star')
            action = 'BUY_PUT'
            confidence = 75
        
        # Return signal
        if patterns:
            return {
                'action': action,
                'confidence': confidence,
                'reason': f"Pattern: {', '.join(patterns)}"
            }
        
        return {'action': 'HOLD', 'confidence': 50, 'reason': 'No candle pattern detected'}


def get_options_strategies():
    """Return all options strategies"""
    return [
        # DirectionalOptionsStrategy(),  # Disabled for paper trading
        # BreakoutOptionsStrategy(),      # Disabled for paper trading
        # VWAPOptionsStrategy(),          # Disabled for paper trading
        MomentumOptionsStrategy(),       # Pure price momentum
        CandlePatternOptionsStrategy()   # Professional candle patterns
    ]
