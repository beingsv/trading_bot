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

# ============================================================
# OPTIONS TRADING CONFIGURATION
# ============================================================

# Trading Mode
PAPER_TRADING = True  # Set to False for live trading
TRADING_TYPE = 'OPTIONS'  # 'OPTIONS' or 'EQUITY'

# Capital & Risk
INITIAL_CAPITAL = 10000  # Virtual money for paper trading
MAX_DAILY_LOSS = 500  # Stop trading if daily loss exceeds ₹500
MAX_DAILY_LOSS_PERCENT = 5.0  # Or 5% of capital
MIN_CAPITAL_TO_TRADE = 2000  # Minimum capital required

# Options-Specific Settings
MAX_POSITIONS = 2  # Maximum open positions (1-2 for ₹10k capital)
MAX_POSITION_PER_SYMBOL = 1  # Only 1 position per index
POSITION_SIZE_PERCENT = 40  # Use 40% of capital per trade (₹4000 per position)

# Options Risk Management
STOP_LOSS_PERCENT = 25.0  # 25% stop loss (options move fast)
TAKE_PROFIT_PERCENT = 40.0  # 40% profit target (options can double quickly)
MAX_THETA_PERCENT = 15.0  # Exit if theta > 15% of premium (time decay)
MIN_DELTA = 0.35  # Minimum delta for directional trades
MAX_IV_PERCENTILE = 70  # Don't buy if IV > 70th percentile (too expensive)

# Intraday Rules
INTRADAY_ONLY = True  # Exit all positions by market close
NO_TRADE_AFTER_HOUR = 14  # Don't enter new trades after 2 PM (theta risk)
NO_TRADE_AFTER_MINUTE = 30
EXIT_ALL_BY_HOUR = 15  # Exit all positions by 3:15 PM
EXIT_ALL_BY_MINUTE = 15

# Brokerage & Charges (Options Trading - AngelOne)
BROKERAGE_PER_TRADE = 20  # Flat ₹20 per executed order
STT_OPTIONS_PERCENT = 0.0625  # 0.0625% on sell side (options)
TRANSACTION_CHARGES_PERCENT = 0.053  # 0.053% (NSE F&O)
GST_PERCENT = 18  # 18% GST on brokerage + transaction charges
SEBI_CHARGES = 10  # ₹10 per crore
STAMP_DUTY_PERCENT = 0.003  # 0.003% on buy side

# Total typical cost per options trade: ~₹40-60 for ₹4,000 position

# Market Hours (IST)
MARKET_OPEN_HOUR = 9
MARKET_OPEN_MINUTE = 15
MARKET_CLOSE_HOUR = 15
MARKET_CLOSE_MINUTE = 30

# Strategy Learning
MIN_TRADES_FOR_EVALUATION = 10  # Minimum trades before evaluating (options trade less frequently)
STRATEGY_EVALUATION_DAYS = 7  # Evaluate strategies weekly
TOP_STRATEGIES_TO_KEEP = 3  # Keep best 3 strategies (simplified)

# Data Storage
DATABASE_PATH = 'data/trading_bot.db'
LOGS_PATH = 'logs/'

# Backup Settings
AUTO_BACKUP_ENABLED = False  # Set to True to enable auto-backup every 10 trades
BACKUP_ON_MARKET_CLOSE = True  # Backup when market closes
BACKUP_KEEP_LAST_N = 10  # Keep last N backups

# ============================================================
# OPTIONS TRADING SYMBOLS
# ============================================================

# Primary Index for Options Trading
PRIMARY_INDEX = 'NIFTY'  # Trade NIFTY 50 options

# Index Details
INDEX_CONFIG = {
    'NIFTY': {
        'symbol': 'NIFTY',
        'token': '99926000',  # NSE NIFTY 50 index token
        'lot_size': 25,  # 1 lot = 25 contracts (updated for 2026)
        'tick_size': 0.05,  # Minimum price movement
        'expiry_day': 'Thursday',  # Weekly expiry
        'strike_gap': 50,  # Strike price gap (₹50)
    },
    'BANKNIFTY': {
        'symbol': 'BANKNIFTY',
        'token': '99926009',  # NSE BANKNIFTY index token
        'lot_size': 15,  # 1 lot = 15 contracts
        'tick_size': 0.05,
        'expiry_day': 'Wednesday',
        'strike_gap': 100,  # Strike price gap (₹100)
    }
}

# Strike Selection
STRIKE_SELECTION = 'ATM'  # 'ATM' (at-the-money), 'OTM1' (1 strike out), 'OTM2' (2 strikes out)
PREFER_STRIKES = ['ATM', 'OTM1']  # Prefer ATM or 1 OTM for best risk/reward

# Expiry Selection
EXPIRY_TYPE = 'WEEKLY'  # 'WEEKLY' or 'MONTHLY'
DAYS_TO_EXPIRY_MIN = 0  # Trade on expiry day (0 DTE)
DAYS_TO_EXPIRY_MAX = 7  # Or up to 7 days (weekly)

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
