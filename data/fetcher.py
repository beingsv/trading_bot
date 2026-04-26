"""
Data Fetcher - Fetch market data from various sources
"""
import pandas as pd
from datetime import datetime, timedelta
import requests
from config.config import ANGELONE_API_KEY, NEWS_API_KEY, INDEX_CONFIG
import time

class DataFetcher:
    """Fetch data from AngelOne and other sources"""
    
    def __init__(self, angelone_api):
        """
        Initialize with AngelOneAPI object
        angelone_api: AngelOneAPI instance (not SmartConnect directly)
        """
        self.angelone_api = angelone_api
        
    def fetch_historical_data(self, symbol, token, interval="FIVE_MINUTE", days=2, to_date=None):
        """
        Fetch historical OHLCV data for options trading
        
        Args:
            symbol: Trading symbol (e.g., 'NIFTY')
            token: Symbol token from INDEX_CONFIG
            interval: Candle timeframe - ONE_MINUTE, FIVE_MINUTE, FIFTEEN_MINUTE,
                     THIRTY_MINUTE, ONE_HOUR, ONE_DAY
            days: Number of days of history
            to_date: End date (default: now)
        
        Returns:
            DataFrame with OHLCV data
        """
        try:
            # Check if logged in
            if not self.angelone_api or not self.angelone_api.smart_api:
                print(f"  ⚠️  AngelOne not logged in")
                return pd.DataFrame()
            
            if to_date is None:
                to_date = datetime.now()
            
            from_date = to_date - timedelta(days=days)
            
            print(f"  📡 API Call:")
            print(f"     Symbol: {symbol}")
            print(f"     Token: {token}")
            print(f"     Interval: {interval}")
            print(f"     From: {from_date.strftime('%Y-%m-%d %H:%M')}")
            print(f"     To: {to_date.strftime('%Y-%m-%d %H:%M')}")
            
            # Add small delay to avoid rate limiting
            time.sleep(0.2)
            
            # AngelOne API call for historical data
            hist_data = self.angelone_api.smart_api.getCandleData({
                "exchange": "NSE",
                "symboltoken": token,
                "interval": interval,
                "fromdate": from_date.strftime("%Y-%m-%d %H:%M"),
                "todate": to_date.strftime("%Y-%m-%d %H:%M")
            })
            
            print(f"  📥 API Response Status: {hist_data.get('status') if hist_data else 'None'}")
            
            if hist_data and hist_data.get('status'):
                data_count = len(hist_data.get('data', []))
                print(f"  📊 Received {data_count} candles")
                
                if data_count == 0:
                    print(f"  ⚠️  API returned 0 candles")
                    print(f"  💡 This might be a holiday or weekend")
                    return pd.DataFrame()
            
            if hist_data and hist_data.get('status') and hist_data.get('data'):
                df = pd.DataFrame(
                    hist_data['data'], 
                    columns=['timestamp', 'open', 'high', 'low', 'close', 'volume']
                )
                
                # Convert timestamp to datetime
                df['timestamp'] = pd.to_datetime(df['timestamp'])
                
                # Convert price columns to float
                for col in ['open', 'high', 'low', 'close']:
                    df[col] = df[col].astype(float)
                
                df['volume'] = df['volume'].astype(int)
                
                return df
            else:
                print(f"  ⚠️  No data returned for {symbol}")
                if hist_data:
                    print(f"  📋 Full response: {hist_data}")
                return pd.DataFrame()
            
        except Exception as e:
            print(f"  ⚠️  Error fetching historical data for {symbol}: {e}")
            import traceback
            traceback.print_exc()
            return pd.DataFrame()
    
    def get_historical_data(self, symbol, days=365, interval="ONE_DAY"):
        """
        Legacy method - kept for compatibility
        Now redirects to fetch_historical_data with token lookup
        """
        # For options trading, use fetch_historical_data instead
        print(f"⚠️  Warning: get_historical_data is deprecated. Use fetch_historical_data with token parameter.")
        return pd.DataFrame()
    
    def get_live_price(self, symbol, token):
        """
        Get current market price
        
        Args:
            symbol: Trading symbol
            token: Symbol token
        """
        try:
            if not self.angelone_api or not self.angelone_api.smart_api:
                return None
            
            # Add small delay
            time.sleep(0.1)
            
            ltp = self.angelone_api.smart_api.ltpData("NSE", symbol, token)
            
            if ltp and ltp.get('status') and ltp.get('data'):
                return float(ltp['data']['ltp'])
            return None
        except Exception as e:
            print(f"  ⚠️  Error fetching live price for {symbol}: {e}")
            return None
    
    def get_market_depth(self, symbol):
        """Get order book depth"""
        try:
            if not self.angelone_api or not self.angelone_api.smart_api:
                return None
                
            return self.angelone_api.smart_api.getMarketData("NSE", symbol, "")
        except Exception as e:
            print(f"Error fetching market depth: {e}")
            return None
    
    def get_fii_dii_data(self):
        """Fetch FII/DII activity data"""
        # Scrape from NSE or use API
        try:
            url = "https://www.nseindia.com/api/fiidiiTradeReact"
            headers = {'User-Agent': 'Mozilla/5.0'}
            response = requests.get(url, headers=headers)
            return response.json()
        except Exception as e:
            print(f"Error fetching FII/DII data: {e}")
            return None
    
    def get_index_data(self, index_name):
        """Fetch index data (Nifty, Sensex, etc.)"""
        try:
            if not self.angelone_api or not self.angelone_api.smart_api:
                return None
                
            # Fetch index data from AngelOne
            return self.angelone_api.smart_api.ltpData("NSE", index_name, "")
        except Exception as e:
            print(f"Error fetching index data: {e}")
            return None
    
    def get_currency_data(self):
        """Fetch USD/INR and crude oil prices"""
        try:
            # Fetch currency data
            usdinr = self.get_live_price("USDINR")
            return {'USDINR': usdinr}
        except Exception as e:
            print(f"Error fetching currency data: {e}")
            return None
