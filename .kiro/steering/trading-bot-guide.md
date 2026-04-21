---
title: AI Trading Bot - Complete Implementation Guide
description: Self-learning trading bot for Indian markets with AngelOne integration
tags: [trading, ai, machine-learning, angelone, indian-market, automation]
version: 1.0.0
---

# 🤖 AI Trading Bot - Complete Implementation Guide

## Overview

This is a self-learning AI trading bot for Indian stock markets that:
- Learns from historical data and daily trading
- Uses 6 different trading strategies
- Monitors news sentiment and market conditions
- Executes paper trading with virtual money
- Adapts strategies based on performance
- Provides visual analytics and insights

## 🏗️ Project Structure

```
intraBot/
├── config/
│   ├── config.py              # All configuration settings
│   ├── .env                   # API credentials (secure)
│   └── .env.example           # Template for credentials
├── data/
│   ├── fetcher.py            # Fetch market data from AngelOne
│   ├── storage.py            # Database operations & backups
│   ├── trading_bot.db        # Main database (bot's brain)
│   ├── news_cache.json       # Cached news data
│   └── backups/              # Auto-backups (last 10)
├── analysis/
│   ├── technical.py          # Technical indicators (RSI, MACD, etc.)
│   └── news_sentiment.py    # News sentiment analysis
├── strategies/
│   ├── base_strategy.py      # Strategy template
│   ├── predefined.py         # 6 trading strategies
│   └── strategy_pool.py      # Strategy management & ranking
├── trading/
│   ├── paper_trading.py      # Paper trading engine
│   ├── signal_generator.py   # Buy/sell signal generation
│   └── angelone_api.py       # AngelOne API integration
├── learning/
│   ├── feedback_loop.py      # Learn from trades
│   └── market_conditions.py  # Market state detection
├── main.py                    # Quick daily analysis
├── run_bot_continuous.py      # Continuous monitoring (main)
├── backtest_and_train.py      # Train on historical data
├── learning_dashboard.py      # Text-based insights
├── performance_graphs.py      # Visual analytics
└── requirements.txt           # Python dependencies
```

## 🚀 Quick Start

### 1. Installation

```bash
# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Configuration

```bash
# Copy environment template
cp config/.env.example config/.env

# Edit with your credentials
# - AngelOne API credentials
# - News API key
```

### 3. Initial Training (One-time)

```bash
# Train bot on 6 months historical data
python backtest_and_train.py
```

### 4. Daily Trading

```bash
# Run every trading day (8:30 AM - 9:00 AM)
python run_bot_continuous.py

# Bot runs automatically until 3:30 PM
```

## 📊 Core Features

### 1. Multi-Strategy Trading System

**6 Built-in Strategies:**
- RSI Strategy (Mean reversion)
- MACD Strategy (Momentum)
- Moving Average Crossover (Trend following)
- Bollinger Bands (Volatility)
- Trend Following (Multi-indicator)
- News Sentiment (Fundamental)

**How it works:**
- All strategies analyze each stock
- Each gives BUY/SELL/HOLD signal with confidence
- Bot combines signals with weighted voting
- Better performing strategies get more weight

### 2. Self-Learning System

**Learns at 3 Levels:**

**Immediate (Real-time):**
- After every trade closes
- Updates strategy performance
- Adjusts confidence weights
- Applies to next trade

**Continuous (Every 5 minutes):**
- Monitors which strategies work today
- Adjusts weights dynamically
- Adapts to current market

**Deep (End of day):**
- Analyzes all trades
- Identifies patterns
- Updates strategy rankings
- Saves insights to database

### 3. Technical Analysis

**Indicators Calculated:**
- Moving Averages (SMA 20, 50, EMA 12, 26)
- MACD (12, 26, 9)
- RSI (14 period)
- Bollinger Bands (20, 2σ)
- ATR (Average True Range)
- OBV (On Balance Volume)
- ADX (Trend strength)

**All implemented in pure Python/NumPy** (no external dependencies)

### 4. News Sentiment Analysis

**Sources Monitored:**
- General market news (Nifty, Sensex, economy)
- Global markets (US, Asia, crude oil)
- Stock-specific news
- RBI policy, inflation, FII/DII activity

**Features:**
- Sentiment scoring (-1 to +1)
- Caching (1 hour) to save API calls
- Rate limiting (90 requests/day)
- Graceful degradation if API fails

### 5. Paper Trading Engine

**Capabilities:**
- Virtual ₹1,00,000 starting capital
- Position sizing (max 10% per trade)
- Stop loss (2%) and take profit (5%)
- Real-time P&L tracking
- Complete trade logging

**Risk Management:**
- Max 5 open positions
- Max 1 position per stock
- Daily loss limit (₹5,000 or 5%)
- Minimum capital check (₹10,000)

### 6. Market Monitoring

**Continuous Scanning:**
- Every 5 minutes during market hours
- Monitors all open positions
- Checks stop loss/take profit
- Generates new entry signals
- Updates hourly news sentiment

**Session Management:**
- Auto-login to AngelOne
- Session refresh every 3 hours
- Retry logic on failures
- Handles API errors gracefully

### 7. Safety Features

**8 Critical Protections:**
1. Daily loss limit enforcement
2. Duplicate position prevention
3. Session timeout handling
4. Market holiday detection
5. Error handling & retries
6. Capital management
7. News API caching & rate limiting
8. Database auto-backup

### 8. Analytics & Visualization

**Text Dashboard (`learning_dashboard.py`):**
- Overall performance metrics
- Strategy intelligence rankings
- Market condition insights
- Recent learnings
- Actionable recommendations
- Knowledge base statistics

**Visual Graphs (`performance_graphs.py`):**
- Daily P&L bar chart
- Cumulative returns curve
- Strategy comparison
- Win rate trend
- Trade distribution
- Hourly performance
- Equity curve
- Strategy heatmap

## 🎯 Daily Workflow

### Morning (8:30 AM - 9:00 AM)

```bash
# Activate environment
source venv/bin/activate

# Start bot
python run_bot_continuous.py
```

**Bot automatically:**
- Checks if today is holiday
- Logs into AngelOne
- Fetches morning news
- Waits for market open (9:15 AM)

### Market Hours (9:15 AM - 3:30 PM)

**Every 5 minutes:**
- Scans all 10 stocks in watchlist
- Checks open positions for exit signals
- Generates new entry signals
- Executes trades if confidence > 60%
- Learns from completed trades

**Every hour:**
- Fetches fresh news
- Updates market sentiment
- Adjusts strategy weights

### Market Close (3:30 PM)

**Bot automatically:**
- Closes all intraday positions
- Calculates daily P&L
- Generates performance report
- Shows recommendations
- Stops execution

### Evening (Anytime)

```bash
# View learning insights
python learning_dashboard.py

# Generate visual graphs
python performance_graphs.py
```

## 🛡️ Safety & Risk Management

### Capital Protection

```python
# config/config.py
MAX_DAILY_LOSS = 5000           # Stop at ₹5,000 loss
MAX_DAILY_LOSS_PERCENT = 5.0    # Or 5% of capital
MIN_CAPITAL_TO_TRADE = 10000    # Minimum to continue
```

### Position Limits

```python
MAX_POSITIONS = 5                # Max open positions
MAX_POSITION_PER_SYMBOL = 1     # No duplicates
MAX_POSITION_SIZE = 0.1         # 10% per trade
```

### Stop Loss & Take Profit

```python
STOP_LOSS_PERCENT = 2.0         # Exit at -2%
TAKE_PROFIT_PERCENT = 5.0       # Exit at +5%
```

### Market Holidays

```python
MARKET_HOLIDAYS = [
    '2026-01-26',  # Republic Day
    '2026-03-14',  # Holi
    # ... all NSE holidays
]
```

## 📈 Performance Tracking

### Database Schema

**trades table:**
- Every buy/sell transaction
- Entry/exit prices
- P&L and percentage
- Strategy used
- Timestamp and reason

**strategy_performance table:**
- Win rate per strategy
- Total trades and P&L
- Average profit/loss
- Sharpe ratio
- Last updated timestamp

**market_conditions table:**
- Market state during trades
- News sentiment scores
- Volatility levels
- FII/DII activity

### Backup System

**Auto-backup:**
- Every 10 trades
- Keeps last 10 backups
- Timestamped files
- Located in `data/backups/`

**Manual restore:**
```python
from data.storage import DataStorage
storage = DataStorage()
storage.restore_from_backup()
```

## 🔧 Configuration Guide

### API Credentials

**AngelOne:**
1. Register at https://smartapi.angelbroking.com/
2. Get API Key, Client ID, Password, TOTP Secret
3. Add to `config/.env`

**News API:**
1. Register at https://newsapi.org/
2. Get free API key (100 requests/day)
3. Add to `config/.env`

### Watchlist

```python
# config/config.py
WATCHLIST = [
    'RELIANCE-EQ',
    'TCS-EQ',
    'INFY-EQ',
    # Add more symbols
]
```

### Risk Parameters

Adjust in `config/config.py` based on risk tolerance:
- Conservative: Lower position size, tighter stop loss
- Aggressive: Higher position size, wider stop loss

## 🧠 How Learning Works

### Strategy Weight Adjustment

**Initial State:**
```
All strategies: 1.0x weight (equal)
```

**After 1 week:**
```
MA Crossover: 1.3x (65% win rate)
RSI Strategy: 1.0x (52% win rate)
MACD: 0.7x (45% win rate)
```

**Signal Generation:**
```
MA Crossover says BUY (70% confidence) × 1.3 = 91
RSI says BUY (60% confidence) × 1.0 = 60
MACD says HOLD (50% confidence) × 0.7 = 35

Combined: BUY with 62% confidence
```

### Pattern Recognition

**Bot learns:**
- Which strategies work in bull/bear/sideways markets
- Best trading hours (morning vs afternoon)
- Stock-specific patterns
- News sentiment correlation
- Volatility impact

**Example Learning:**
```
"RSI Strategy works well in BULL_TRENDING market"
"Morning trades (9:15-11:00) more profitable"
"RELIANCE responds well to positive news"
"High volatility hurts mean reversion strategies"
```

## 🎮 Control Commands

### During Execution

**Pause bot:**
```bash
touch PAUSE
# Bot stops scanning, keeps positions
```

**Resume bot:**
```bash
rm PAUSE
# Bot resumes scanning
```

**Stop bot:**
```
Ctrl + C
# Closes positions, shows report, exits
```

### View Analytics

```bash
# Text insights
python learning_dashboard.py

# Visual graphs
python performance_graphs.py

# Quick analysis
python main.py
```

## 🐛 Troubleshooting

### Bot won't start

**Check:**
1. Virtual environment activated?
2. All dependencies installed?
3. API credentials in `.env`?
4. Not a market holiday?

### Session expires mid-day

**Fixed automatically:**
- Bot refreshes every 3 hours
- Retry logic on failures
- Check terminal for refresh messages

### News API limit hit

**Handled gracefully:**
- Bot uses cached news
- Continues trading with technical analysis
- Shows warning in terminal

### Database corruption

**Restore from backup:**
```python
from data.storage import DataStorage
storage = DataStorage()
storage.restore_from_backup()
```

## 📚 Key Files Reference

### Main Execution Files

- `run_bot_continuous.py` - **Use this daily** (continuous monitoring)
- `backtest_and_train.py` - One-time training on historical data
- `main.py` - Quick analysis (runs once, exits)

### Analytics Files

- `learning_dashboard.py` - Text-based insights
- `performance_graphs.py` - Visual charts

### Configuration

- `config/config.py` - All settings
- `config/.env` - API credentials

### Core Logic

- `strategies/predefined.py` - 6 trading strategies
- `trading/signal_generator.py` - Signal combination logic
- `learning/feedback_loop.py` - Learning mechanism

## 🎓 Best Practices

### Before Going Live

1. ✅ Run backtest on historical data
2. ✅ Paper trade for 1 month minimum
3. ✅ Review strategy performance
4. ✅ Understand all safety features
5. ✅ Test with small capital first

### Daily Routine

1. Start bot before 9:15 AM
2. Monitor terminal for first 30 minutes
3. Check positions mid-day
4. Review daily report at 3:30 PM
5. Analyze learnings weekly

### Monthly Maintenance

1. Re-run backtest with latest data
2. Review strategy rankings
3. Adjust risk parameters if needed
4. Check database backups
5. Update holiday calendar

## 🚨 Important Notes

### Paper Trading

- Bot starts in PAPER TRADING mode
- Uses virtual ₹1,00,000
- No real money at risk
- Perfect for learning

### Live Trading

To switch to live trading:
```python
# config/config.py
PAPER_TRADING = False  # Change to False
```

**⚠️ Only after:**
- 1+ month paper trading
- Consistent positive results
- Full understanding of bot behavior

### Data Privacy

- All data stored locally
- No external data sharing
- API keys in `.env` (gitignored)
- Database contains your trading history

### Limitations

- Bot doesn't create new strategies (uses 6 predefined)
- Adjusts weights, not strategy logic
- Requires manual start each day
- Paper trading uses mock data for prices

## 🎯 Success Metrics

### After 1 Week
- Bot should have 20-30 trades
- Win rate around 50-55%
- Understanding market patterns

### After 1 Month
- 100+ trades experience
- Win rate 55-60%
- Clear strategy rankings
- Profitable overall

### After 3 Months
- 300+ trades experience
- Win rate 60%+
- Deep market understanding
- Consistent profitability

## 📞 Support & Resources

### Documentation
- `README.md` - Project overview
- `SETUP_GUIDE.md` - Detailed setup
- `SAFETY_FEATURES.md` - Safety mechanisms
- This file - Complete guide

### Code Structure
- Well-commented code
- Modular design
- Easy to extend
- Type hints where applicable

### Learning Resources
- AngelOne API docs: https://smartapi.angelbroking.com/docs
- News API docs: https://newsapi.org/docs
- Technical indicators: Investopedia

## 🔮 Future Enhancements

### Possible Additions
- Real-time WebSocket data
- More trading strategies
- Options trading support
- Multi-timeframe analysis
- Telegram notifications
- Web dashboard
- Portfolio optimization
- Risk-adjusted position sizing

### Extensibility
- Add new strategies in `strategies/predefined.py`
- Modify indicators in `analysis/technical.py`
- Adjust risk in `config/config.py`
- Custom analytics in dashboard files

---

## Summary

This is a production-ready, self-learning trading bot with:
- ✅ 6 trading strategies
- ✅ Real-time learning
- ✅ News sentiment analysis
- ✅ Complete safety features
- ✅ Visual analytics
- ✅ Auto-backup system
- ✅ Paper trading mode
- ✅ Continuous monitoring

**Ready to use tomorrow!** 🚀

---

*Version 1.0.0 - April 2026*
*Built with Python, Pandas, NumPy, Matplotlib*
*Integrated with AngelOne SmartAPI*
