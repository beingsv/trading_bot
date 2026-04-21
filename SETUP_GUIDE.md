# Trading Bot Setup Guide

## Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

Note: `ta-lib` requires system-level installation:
- **macOS**: `brew install ta-lib`
- **Ubuntu**: `sudo apt-get install ta-lib`
- **Windows**: Download from https://www.lfd.uci.edu/~gohlke/pythonlibs/#ta-lib

### 2. Configure API Keys

Copy the example environment file:
```bash
cp config/.env.example config/.env
```

Edit `config/.env` and add your credentials:
- AngelOne API credentials (from https://smartapi.angelbroking.com/)
- News API key (from https://newsapi.org/)

### 3. Run the Bot

```bash
python main.py
```

## How It Works

### 1. Data Collection
- Fetches historical price data from AngelOne
- Monitors real-time market data
- Scrapes news and analyzes sentiment
- Tracks FII/DII activity
- Monitors global markets (US, Asia)

### 2. Analysis
The bot analyzes multiple factors:
- **Technical**: RSI, MACD, Moving Averages, Bollinger Bands, ADX, etc.
- **News Sentiment**: Analyzes Indian market news, company-specific news
- **Market Conditions**: Bull/Bear/Sideways/High Volatility
- **Global Impact**: US markets, crude oil, USD/INR
- **FII/DII Activity**: Foreign and domestic institutional investor flows

### 3. Strategy Learning
- Starts with 6 predefined strategies
- Tests each strategy in paper trading
- Tracks performance (win rate, P&L, risk-reward)
- Learns which strategies work in different market conditions
- Adapts strategy selection based on current market state

### 4. Signal Generation
- Combines all analysis sources
- Generates weighted consensus signal
- Considers:
  - 50% weight to strategy consensus
  - 30% weight to technical indicators
  - 20% weight to news sentiment

### 5. Trade Execution
- **Paper Trading**: Simulates trades with virtual ₹1,00,000
- **Risk Management**: 
  - Max 10% of capital per trade
  - 2% stop loss
  - 5% take profit
- Tracks all trades in database
- Updates strategy performance after each trade

### 6. Learning & Adaptation
- Analyzes every trade (win/loss)
- Identifies patterns in successful trades
- Learns from mistakes
- Adjusts strategy weights based on performance
- Provides actionable recommendations

## Configuration

Edit `config/config.py` to customize:

```python
PAPER_TRADING = True  # Set False for live trading
INITIAL_CAPITAL = 100000  # Virtual money
MAX_POSITION_SIZE = 0.1  # 10% max per trade
STOP_LOSS_PERCENT = 2.0  # 2% stop loss
TAKE_PROFIT_PERCENT = 5.0  # 5% take profit

WATCHLIST = [
    'RELIANCE-EQ',
    'TCS-EQ',
    # Add more symbols
]
```

## Database

All data is stored in SQLite database at `data/trading_bot.db`:
- Price data
- Trade history
- Strategy performance
- Market conditions

## Safety Features

1. **Paper Trading Mode**: Test without risking real money
2. **Stop Loss**: Automatic exit at 2% loss
3. **Take Profit**: Automatic exit at 5% profit
4. **Position Limits**: Max 10% of capital per trade
5. **Market Condition Check**: Won't trade in extreme volatility
6. **Sentiment Override**: Blocks trades against strong market sentiment

## Next Steps

1. Run in paper trading mode for at least 1 month
2. Monitor strategy performance
3. Adjust parameters based on learnings
4. Only switch to live trading after consistent paper trading success
5. Start with small position sizes in live trading

## Important Notes

⚠️ **Risk Warning**: Trading involves risk. This bot is for educational purposes. Always:
- Start with paper trading
- Never invest more than you can afford to lose
- Monitor the bot regularly
- Understand each strategy before using
- Keep stop losses in place

## Support

For issues or questions:
1. Check AngelOne API documentation
2. Review strategy performance in database
3. Check logs for errors
4. Adjust configuration parameters
