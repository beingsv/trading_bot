"""
Data Fetcher - Fetch market data from various sources
"""
import pandas as pd
from datetime import datetime, timedelta
import requests
from config.config import ANGELONE_API_KEY, NEWS_API_KEY

class DataFetcher:
    """Fetch data from AngelOne and other sources"""
    
    def __init__(self, angelone_client):
        self.client = angelone_client
        
    def get_historical_data(self, symbol, days=365):
        """Fetch historical OHLCV data"""
        try:
            to_date = datetime.now()
            from_date = to_date - timedelta(days=days)
            
            # AngelOne API call for historical data
            hist_data = self.client.getCandleData({
                "exchange": "NSE",
                "symboltoken": symbol,
                "interval": "ONE_DAY",
                "fromdate": from_date.strftime("%Y-%m-%d %H:%M"),
                "todate": to_date.strftime("%Y-%m-%d %H:%M")
            })
            
            return pd.DataFrame(hist_data['data'], 
                              columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
        except Exception as e:
            print(f"Error fetching historical data: {e}")
            return pd.DataFrame()
    
    def get_live_price(self, symbol):
        """Get current market price"""
        try:
            ltp = self.client.ltpData("NSE", symbol, "")
            return ltp['data']['ltp']
        except Exception as e:
            print(f"Error fetching live price: {e}")
            return None
    
    def get_market_depth(self, symbol):
        """Get order book depth"""
        try:
            return self.client.getMarketData("NSE", symbol, "")
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
            # Fetch index data from AngelOne
            return self.client.ltpData("NSE", index_name, "")
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
