"""
AngelOne API Integration
"""
from SmartApi import SmartConnect
import pyotp
from config.config import (
    ANGELONE_API_KEY, ANGELONE_CLIENT_ID, 
    ANGELONE_PASSWORD, ANGELONE_TOTP_SECRET
)

class AngelOneAPI:
    """Wrapper for AngelOne SmartAPI"""
    
    def __init__(self):
        self.api_key = ANGELONE_API_KEY
        self.client_id = ANGELONE_CLIENT_ID
        self.password = ANGELONE_PASSWORD
        self.totp_secret = ANGELONE_TOTP_SECRET
        self.smart_api = None
        self.auth_token = None
        self.feed_token = None
    
    def login(self):
        """Login to AngelOne"""
        try:
            self.smart_api = SmartConnect(api_key=self.api_key)
            
            # Generate TOTP
            totp = pyotp.TOTP(self.totp_secret).now() if self.totp_secret else None
            
            # Login
            data = self.smart_api.generateSession(
                self.client_id,
                self.password,
                totp
            )
            
            if data['status']:
                self.auth_token = data['data']['jwtToken']
                self.feed_token = data['data']['feedToken']
                print("✅ Successfully logged in to AngelOne")
                return True
            else:
                print(f"❌ Login failed: {data['message']}")
                return False
                
        except Exception as e:
            print(f"❌ Login error: {e}")
            return False
    
    def get_profile(self):
        """Get user profile"""
        try:
            return self.smart_api.getProfile(self.auth_token)
        except Exception as e:
            print(f"Error getting profile: {e}")
            return None
    
    def get_ltp(self, exchange, symbol, token):
        """Get last traded price"""
        try:
            return self.smart_api.ltpData(exchange, symbol, token)
        except Exception as e:
            print(f"Error getting LTP: {e}")
            return None
    
    def place_order(self, order_params):
        """
        Place order
        order_params = {
            'variety': 'NORMAL',
            'tradingsymbol': 'SBIN-EQ',
            'symboltoken': '3045',
            'transactiontype': 'BUY',
            'exchange': 'NSE',
            'ordertype': 'MARKET',
            'producttype': 'INTRADAY',
            'duration': 'DAY',
            'quantity': '1'
        }
        """
        try:
            return self.smart_api.placeOrder(order_params)
        except Exception as e:
            print(f"Error placing order: {e}")
            return None
    
    def get_order_book(self):
        """Get all orders"""
        try:
            return self.smart_api.orderBook()
        except Exception as e:
            print(f"Error getting order book: {e}")
            return None
    
    def get_positions(self):
        """Get current positions"""
        try:
            return self.smart_api.position()
        except Exception as e:
            print(f"Error getting positions: {e}")
            return None
    
    def logout(self):
        """Logout from AngelOne"""
        try:
            self.smart_api.terminateSession(self.client_id)
            print("✅ Logged out from AngelOne")
        except Exception as e:
            print(f"Error during logout: {e}")
