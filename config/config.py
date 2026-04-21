"""
Configuration for Trading Bot
"""
import os
from dotenv import load_dotenv

load_dotenv()

# AngelOne API Credentials
ANGELONE_API_KEY = os.getenv('ANGELONE_API_KEY', 'your_api_key')
ANGELONE_CLIENT_ID = os.getenv('ANGELONE_CLIENT_ID', 'your_client_id')
ANGELONE_PASSWORD = os.getenv('ANGELONE_PASSWORD', 'your_password')
ANGELONE_TOTP_SECRET = os.getenv('ANGELONE_TOTP_SECRET', '')

# News API
NEWS_API_KEY = os.getenv('NEWS_API_KEY', 'your_news_api_key')

# Trading Parameters
PAPER_TRADING = True  # Set to False for live trading
INITIAL_CAPITAL = 100000  # Virtual money for paper trading
MAX_POSITION_SIZE = 0.1  # Max 10% of capital per trade
STOP_LOSS_PERCENT = 2.0  # 2% stop loss
TAKE_PROFIT_PERCENT = 5.0  # 5% take profit

# Risk Management
MAX_DAILY_LOSS = 5000  # Stop trading if daily loss exceeds ₹5,000
MAX_DAILY_LOSS_PERCENT = 5.0  # Or 5% of capital, whichever is lower
MAX_POSITIONS = 5  # Maximum number of open positions at once
MAX_POSITION_PER_SYMBOL = 1  # Only 1 position per stock
MIN_CAPITAL_TO_TRADE = 10000  # Minimum capital required to continue trading

# Market Hours (IST)
MARKET_OPEN_HOUR = 9
MARKET_OPEN_MINUTE = 15
MARKET_CLOSE_HOUR = 15
MARKET_CLOSE_MINUTE = 30

# Strategy Learning
MIN_TRADES_FOR_EVALUATION = 20  # Minimum trades before evaluating strategy
STRATEGY_EVALUATION_DAYS = 7  # Evaluate strategies weekly
TOP_STRATEGIES_TO_KEEP = 5  # Keep best performing strategies

# Data Storage
DATABASE_PATH = 'data/trading_bot.db'
LOGS_PATH = 'logs/'

# Symbols to Trade
WATCHLIST = [
    'RELIANCE-EQ',
    'TCS-EQ',
    'INFY-EQ',
    'HDFCBANK-EQ',
    'ICICIBANK-EQ',
    'SBIN-EQ',
    'BHARTIARTL-EQ',
    'ITC-EQ',
    'KOTAKBANK-EQ',
    'LT-EQ'
]

# Market Indices to Monitor
INDICES = ['NIFTY', 'BANKNIFTY', 'SENSEX']

# Market Holidays 2026 (NSE)
MARKET_HOLIDAYS = [
    '2026-01-26',  # Republic Day
    '2026-03-14',  # Holi
    '2026-04-02',  # Ram Navami
    '2026-04-10',  # Mahavir Jayanti
    '2026-04-14',  # Dr. Ambedkar Jayanti
    '2026-05-01',  # Maharashtra Day
    '2026-08-15',  # Independence Day
    '2026-08-27',  # Ganesh Chaturthi
    '2026-10-02',  # Gandhi Jayanti
    '2026-10-24',  # Dussehra
    '2026-11-12',  # Diwali
    '2026-11-13',  # Diwali (Balipratipada)
    '2026-11-30',  # Guru Nanak Jayanti
    '2026-12-25',  # Christmas
]
