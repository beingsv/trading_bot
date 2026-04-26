"""
Technical Analysis - Calculate indicators and patterns
"""
import pandas as pd
import numpy as np

class TechnicalAnalyzer:
    """Calculate technical indicators"""
    
    def __init__(self):
        pass
    
    def calculate_sma(self, data, period):
        """Simple Moving Average"""
        return data.rolling(window=period).mean()
    
    def calculate_ema(self, data, period):
        """Exponential Moving Average"""
        return data.ewm(span=period, adjust=False).mean()
    
    def calculate_rsi(self, data, period=14):
        """Relative Strength Index"""
        delta = data.diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))
        return rsi
    
    def calculate_macd(self, data, fast=12, slow=26, signal=9):
        """MACD Indicator"""
        ema_fast = self.calculate_ema(data, fast)
        ema_slow = self.calculate_ema(data, slow)
        macd = ema_fast - ema_slow
        signal_line = self.calculate_ema(macd, signal)
        histogram = macd - signal_line
        return macd, signal_line, histogram
    
    def calculate_bollinger_bands(self, data, period=20, std_dev=2):
        """Bollinger Bands"""
        sma = self.calculate_sma(data, period)
        std = data.rolling(window=period).std()
        upper_band = sma + (std * std_dev)
        lower_band = sma - (std * std_dev)
        return upper_band, sma, lower_band
    
    def calculate_atr(self, high, low, close, period=14):
        """Average True Range"""
        tr1 = high - low
        tr2 = abs(high - close.shift())
        tr3 = abs(low - close.shift())
        tr = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
        atr = tr.rolling(window=period).mean()
        return atr
    
    def calculate_all_indicators(self, df):
        """Calculate comprehensive technical indicators"""
        if df.empty or len(df) < 50:
            return df
        
        # Moving Averages
        df['SMA_20'] = self.calculate_sma(df['close'], 20)
        df['SMA_50'] = self.calculate_sma(df['close'], 50)
        df['EMA_12'] = self.calculate_ema(df['close'], 12)
        df['EMA_26'] = self.calculate_ema(df['close'], 26)
        
        # MACD
        macd, signal, histogram = self.calculate_macd(df['close'])
        df['MACD_12_26_9'] = macd
        df['MACDs_12_26_9'] = signal
        df['MACDh_12_26_9'] = histogram
        
        # RSI
        df['RSI'] = self.calculate_rsi(df['close'], 14)
        
        # Bollinger Bands
        upper, middle, lower = self.calculate_bollinger_bands(df['close'], 20)
        df['BBU_20_2.0'] = upper
        df['BBM_20_2.0'] = middle
        df['BBL_20_2.0'] = lower
        
        # ATR (Volatility)
        df['ATR_14'] = self.calculate_atr(df['high'], df['low'], df['close'], 14)
        
        # Volume indicators
        df['OBV'] = (np.sign(df['close'].diff()) * df['volume']).fillna(0).cumsum()
        
        # ADX (simplified version)
        df['ADX_14'] = 25  # Placeholder - simplified
        
        # ✅ NEW: Professional Intraday Features
        df = self.calculate_support_resistance(df)
        df = self.calculate_vwap(df)
        df = self.add_previous_day_levels(df)
        
        return df
    
    def detect_patterns(self, df):
        """Detect candlestick patterns"""
        patterns = {}
        
        if len(df) < 3:
            return patterns
        
        # Get recent candles
        c0 = df.iloc[-1]  # Current
        c1 = df.iloc[-2]  # Previous
        c2 = df.iloc[-3] if len(df) >= 3 else None  # 2 candles ago
        
        # Calculate body and shadow sizes
        body_size = abs(c0['close'] - c0['open'])
        candle_range = c0['high'] - c0['low']
        upper_shadow = c0['high'] - max(c0['open'], c0['close'])
        lower_shadow = min(c0['open'], c0['close']) - c0['low']
        
        # Average body size for reference
        avg_body = df['close'].rolling(10).apply(lambda x: abs(x - df['open'].rolling(10).mean()).mean()).iloc[-1]
        
        # === SINGLE CANDLE PATTERNS ===
        
        # Doji (small body)
        patterns['doji'] = body_size < candle_range * 0.1
        
        # Hammer (bullish reversal at bottom)
        patterns['hammer'] = (
            lower_shadow > body_size * 2 and
            upper_shadow < body_size * 0.3 and
            c0['close'] > c0['open']
        )
        
        # Shooting Star (bearish reversal at top)
        patterns['shooting_star'] = (
            upper_shadow > body_size * 2 and
            lower_shadow < body_size * 0.3 and
            c0['close'] < c0['open']
        )
        
        # Spinning Top (indecision)
        patterns['spinning_top'] = (
            body_size < candle_range * 0.3 and
            upper_shadow > body_size and
            lower_shadow > body_size
        )
        
        # Marubozu (strong momentum, no shadows)
        patterns['bullish_marubozu'] = (
            c0['close'] > c0['open'] and
            upper_shadow < body_size * 0.1 and
            lower_shadow < body_size * 0.1
        )
        
        patterns['bearish_marubozu'] = (
            c0['close'] < c0['open'] and
            upper_shadow < body_size * 0.1 and
            lower_shadow < body_size * 0.1
        )
        
        # Dragonfly Doji (bullish)
        patterns['dragonfly_doji'] = (
            body_size < candle_range * 0.1 and
            lower_shadow > candle_range * 0.6 and
            upper_shadow < candle_range * 0.1
        )
        
        # Gravestone Doji (bearish)
        patterns['gravestone_doji'] = (
            body_size < candle_range * 0.1 and
            upper_shadow > candle_range * 0.6 and
            lower_shadow < candle_range * 0.1
        )
        
        if len(df) < 2:
            return patterns
        
        # === TWO CANDLE PATTERNS ===
        
        prev_body = abs(c1['close'] - c1['open'])
        curr_body = abs(c0['close'] - c0['open'])
        
        # Bullish Engulfing
        patterns['bullish_engulfing'] = (
            c1['close'] < c1['open'] and  # Previous bearish
            c0['close'] > c0['open'] and  # Current bullish
            c0['open'] < c1['close'] and  # Opens below prev close
            c0['close'] > c1['open'] and  # Closes above prev open
            curr_body > prev_body  # Larger body
        )
        
        # Bearish Engulfing
        patterns['bearish_engulfing'] = (
            c1['close'] > c1['open'] and  # Previous bullish
            c0['close'] < c0['open'] and  # Current bearish
            c0['open'] > c1['close'] and  # Opens above prev close
            c0['close'] < c1['open'] and  # Closes below prev open
            curr_body > prev_body  # Larger body
        )
        
        # Piercing Pattern (bullish)
        patterns['piercing_pattern'] = (
            c1['close'] < c1['open'] and  # Previous bearish
            c0['close'] > c0['open'] and  # Current bullish
            c0['open'] < c1['low'] and  # Opens below prev low
            c0['close'] > (c1['open'] + c1['close']) / 2  # Closes above 50%
        )
        
        # Dark Cloud Cover (bearish)
        patterns['dark_cloud_cover'] = (
            c1['close'] > c1['open'] and  # Previous bullish
            c0['close'] < c0['open'] and  # Current bearish
            c0['open'] > c1['high'] and  # Opens above prev high
            c0['close'] < (c1['open'] + c1['close']) / 2  # Closes below 50%
        )
        
        # Harami (reversal)
        patterns['bullish_harami'] = (
            c1['close'] < c1['open'] and  # Previous bearish
            c0['close'] > c0['open'] and  # Current bullish
            c0['open'] > c1['close'] and  # Inside previous body
            c0['close'] < c1['open']
        )
        
        patterns['bearish_harami'] = (
            c1['close'] > c1['open'] and  # Previous bullish
            c0['close'] < c0['open'] and  # Current bearish
            c0['open'] < c1['close'] and  # Inside previous body
            c0['close'] > c1['open']
        )
        
        # Inside Bar
        patterns['inside_bar'] = (
            c0['high'] < c1['high'] and
            c0['low'] > c1['low']
        )
        
        # Outside Bar
        patterns['outside_bar'] = (
            c0['high'] > c1['high'] and
            c0['low'] < c1['low']
        )
        
        # Tweezer Top/Bottom
        patterns['tweezer_top'] = abs(c0['high'] - c1['high']) < candle_range * 0.02
        patterns['tweezer_bottom'] = abs(c0['low'] - c1['low']) < candle_range * 0.02
        
        if c2 is None:
            return patterns
        
        # === THREE CANDLE PATTERNS ===
        
        # Morning Star (bullish reversal)
        patterns['morning_star'] = (
            c2['close'] < c2['open'] and  # First bearish
            abs(c1['close'] - c1['open']) < avg_body * 0.3 and  # Second small
            c0['close'] > c0['open'] and  # Third bullish
            c0['close'] > (c2['open'] + c2['close']) / 2  # Closes above 50% of first
        )
        
        # Evening Star (bearish reversal)
        patterns['evening_star'] = (
            c2['close'] > c2['open'] and  # First bullish
            abs(c1['close'] - c1['open']) < avg_body * 0.3 and  # Second small
            c0['close'] < c0['open'] and  # Third bearish
            c0['close'] < (c2['open'] + c2['close']) / 2  # Closes below 50% of first
        )
        
        # Three White Soldiers (strong bullish)
        patterns['three_white_soldiers'] = (
            c2['close'] > c2['open'] and
            c1['close'] > c1['open'] and
            c0['close'] > c0['open'] and
            c0['close'] > c1['close'] > c2['close'] and
            c0['open'] > c1['open'] > c2['open']
        )
        
        # Three Black Crows (strong bearish)
        patterns['three_black_crows'] = (
            c2['close'] < c2['open'] and
            c1['close'] < c1['open'] and
            c0['close'] < c0['open'] and
            c0['close'] < c1['close'] < c2['close'] and
            c0['open'] < c1['open'] < c2['open']
        )
        
        return patterns
    
    def get_trend(self, df):
        """Determine current trend"""
        if len(df) < 50:
            return 'UNKNOWN'
        
        sma_20 = df['SMA_20'].iloc[-1]
        sma_50 = df['SMA_50'].iloc[-1]
        price = df['close'].iloc[-1]
        
        if price > sma_20 > sma_50:
            return 'UPTREND'
        elif price < sma_20 < sma_50:
            return 'DOWNTREND'
        else:
            return 'SIDEWAYS'
    
    def get_signal_strength(self, df):
        """Calculate overall signal strength (-100 to +100)"""
        if df.empty or len(df) < 50:
            return 0
        
        signals = []
        
        # RSI signal
        rsi = df['RSI'].iloc[-1]
        if pd.notna(rsi):
            if rsi < 30:
                signals.append(50)  # Oversold - buy signal
            elif rsi > 70:
                signals.append(-50)  # Overbought - sell signal
        
        # MACD signal
        if 'MACD_12_26_9' in df.columns and 'MACDs_12_26_9' in df.columns:
            macd = df['MACD_12_26_9'].iloc[-1]
            signal = df['MACDs_12_26_9'].iloc[-1]
            if pd.notna(macd) and pd.notna(signal):
                if macd > signal:
                    signals.append(30)
                else:
                    signals.append(-30)
        
        # Moving average crossover
        if pd.notna(df['SMA_20'].iloc[-1]) and pd.notna(df['SMA_50'].iloc[-1]):
            if df['SMA_20'].iloc[-1] > df['SMA_50'].iloc[-1]:
                signals.append(20)
            else:
                signals.append(-20)
        
        return np.mean(signals) if signals else 0

    # ========================================
    # NEW: Professional Intraday Features
    # ========================================
    
    def calculate_support_resistance(self, df, lookback=20):
        """
        Identify support and resistance levels
        Uses swing highs/lows from recent price action
        """
        if len(df) < lookback:
            df['resistance'] = df['high']
            df['support'] = df['low']
            return df
        
        # Find local maxima (resistance) and minima (support)
        df['resistance'] = df['high'].rolling(window=lookback, center=True).max()
        df['support'] = df['low'].rolling(window=lookback, center=True).min()
        
        # Forward fill NaN values (new pandas syntax)
        df['resistance'] = df['resistance'].ffill().bfill()
        df['support'] = df['support'].ffill().bfill()
        
        # Calculate distance from support/resistance (as percentage)
        df['dist_from_resistance'] = ((df['resistance'] - df['close']) / df['close']) * 100
        df['dist_from_support'] = ((df['close'] - df['support']) / df['close']) * 100
        
        return df
    
    def calculate_vwap(self, df):
        """
        Calculate Volume Weighted Average Price (VWAP)
        Critical for intraday trading - shows institutional average price
        """
        if len(df) < 2:
            df['vwap'] = df['close']
            df['dist_from_vwap'] = 0
            df['above_vwap'] = 1
            return df
        
        # Typical price
        typical_price = (df['high'] + df['low'] + df['close']) / 3
        
        # Cumulative typical price * volume
        cum_vol_price = (typical_price * df['volume']).cumsum()
        
        # Cumulative volume
        cum_volume = df['volume'].cumsum()
        
        # VWAP
        df['vwap'] = cum_vol_price / cum_volume
        
        # Distance from VWAP (as percentage)
        df['dist_from_vwap'] = ((df['close'] - df['vwap']) / df['vwap']) * 100
        
        # Price position relative to VWAP
        df['above_vwap'] = (df['close'] > df['vwap']).astype(int)
        
        return df
    
    def add_previous_day_levels(self, df):
        """
        Add previous day's high, low, close
        These act as psychological support/resistance levels
        """
        if len(df) < 2:
            df['prev_day_high'] = df['high']
            df['prev_day_low'] = df['low']
            df['prev_day_close'] = df['close']
            return df
        
        # Assuming data is sorted by timestamp
        # For intraday, we need to identify day boundaries
        df['date'] = pd.to_datetime(df['timestamp']).dt.date
        
        # Get previous day's levels
        daily_high = df.groupby('date')['high'].max()
        daily_low = df.groupby('date')['low'].min()
        daily_close = df.groupby('date')['close'].last()
        
        # Shift to get previous day
        prev_high = daily_high.shift(1)
        prev_low = daily_low.shift(1)
        prev_close = daily_close.shift(1)
        
        # Map back to intraday data
        df['prev_day_high'] = df['date'].map(prev_high)
        df['prev_day_low'] = df['date'].map(prev_low)
        df['prev_day_close'] = df['date'].map(prev_close)
        
        # Forward fill for first day (new pandas syntax)
        df['prev_day_high'] = df['prev_day_high'].bfill()
        df['prev_day_low'] = df['prev_day_low'].bfill()
        df['prev_day_close'] = df['prev_day_close'].bfill()
        
        # Distance from previous day levels
        df['dist_from_prev_high'] = ((df['prev_day_high'] - df['close']) / df['close']) * 100
        df['dist_from_prev_low'] = ((df['close'] - df['prev_day_low']) / df['close']) * 100
        
        # Clean up
        df = df.drop(['date'], axis=1)
        
        return df
    
    def is_near_support(self, df, threshold=1.0):
        """Check if price is near support (within threshold %)"""
        if 'dist_from_support' not in df.columns:
            return False
        return df['dist_from_support'].iloc[-1] < threshold
    
    def is_near_resistance(self, df, threshold=1.0):
        """Check if price is near resistance (within threshold %)"""
        if 'dist_from_resistance' not in df.columns:
            return False
        return df['dist_from_resistance'].iloc[-1] < threshold
    
    def is_above_vwap(self, df):
        """Check if price is above VWAP (bullish)"""
        if 'above_vwap' not in df.columns:
            return False
        return df['above_vwap'].iloc[-1] == 1
    
    def get_vwap_signal(self, df):
        """
        Get VWAP-based signal
        Returns: 'BULLISH', 'BEARISH', or 'NEUTRAL'
        """
        if 'dist_from_vwap' not in df.columns:
            return 'NEUTRAL'
        
        dist = df['dist_from_vwap'].iloc[-1]
        
        if dist > 0.5:  # Price significantly above VWAP
            return 'BULLISH'
        elif dist < -0.5:  # Price significantly below VWAP
            return 'BEARISH'
        else:
            return 'NEUTRAL'
