# 🤖 NIFTY Options Trading Bot

AI-powered options trading bot for NIFTY 50 index with self-learning capabilities.

## 🎯 What It Does

- Trades NIFTY 50 index options (Calls & Puts)
- Uses 3 technical strategies (Directional, Breakout, VWAP)
- Calculates Greeks (Delta, Gamma, Theta, Vega)
- Intraday trading only (exits by 3:15 PM)
- Paper trading with ₹10,000 virtual capital
- Self-learning from every trade

## 🚀 Quick Start

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Configure API Keys
```bash
cp config/.env.example config/.env
# Edit config/.env with your AngelOne API credentials
```

### 3. Test the System
```bash
python test_options_system.py
```

### 4. Run the Bot
```bash
python run_options_bot.py
```

## 📊 Features

### Options Trading
- ✅ Buy Call (bullish) or Buy Put (bearish)
- ✅ ATM/OTM strike selection
- ✅ Greeks-based filtering (Delta, Theta, IV)
- ✅ 25% stop loss, 40% profit target
- ✅ Forced exit at 3:15 PM (no overnight)

### Technical Analysis
- ✅ RSI, MACD, Moving Averages
- ✅ Support & Resistance detection
- ✅ VWAP (Volume Weighted Average Price)
- ✅ Market condition detection

### Risk Management
- ✅ Max 2 positions (₹4,000 each)
- ✅ Daily loss limit (₹500)
- ✅ No trades after 2:30 PM
- ✅ Greeks monitoring (theta decay)
- ✅ IV filtering (avoid expensive options)

### Self-Learning
- ✅ Learns from every trade
- ✅ Adjusts strategy weights
- ✅ Adapts to market conditions
- ✅ Tracks performance metrics

## 📁 Project Structure

```
intraBot/
├── config/
│   ├── config.py              # All configuration
│   └── .env                   # API credentials
├── data/
│   ├── fetcher.py            # Fetch market data
│   ├── options_chain.py      # Options chain & strike selection
│   └── storage.py            # Database operations
├── analysis/
│   ├── technical.py          # Technical indicators
│   ├── options_greeks.py     # Greeks calculator
│   └── news_sentiment.py     # News analysis
├── strategies/
│   ├── options_strategies.py # 3 options strategies
│   └── strategy_pool.py      # Strategy management
├── trading/
│   ├── options_paper_trading.py      # Paper trading engine
│   ├── options_signal_generator.py   # Signal generation
│   └── angelone_api.py              # AngelOne integration
├── learning/
│   ├── feedback_loop.py      # Learn from trades
│   └── market_conditions.py  # Market detection
├── run_options_bot.py         # Main bot (USE THIS)
├── test_options_system.py     # Test all components
└── OPTIONS_TRADING_GUIDE.md   # Complete guide
```

## ⚙️ Configuration

Edit `config/config.py`:

```python
# Capital & Risk
INITIAL_CAPITAL = 10000          # ₹10,000 starting
POSITION_SIZE_PERCENT = 40       # 40% per trade
MAX_POSITIONS = 2                # Max 2 positions
MAX_DAILY_LOSS = 500             # Stop at ₹500 loss

# Options Settings
STOP_LOSS_PERCENT = 25.0         # 25% stop loss
TAKE_PROFIT_PERCENT = 40.0       # 40% profit target
MIN_DELTA = 0.35                 # Minimum delta
MAX_THETA_PERCENT = 15.0         # Max theta decay

# Time Rules
NO_TRADE_AFTER_HOUR = 14         # No trades after 2:30 PM
EXIT_ALL_BY_HOUR = 15            # Exit all by 3:15 PM
INTRADAY_ONLY = True             # No overnight
```

## 📈 How It Works

### 1. Fetch NIFTY Data
- Gets 5-minute candles for NIFTY index
- Calculates technical indicators

### 2. Generate Signal
- 3 strategies vote (Directional, Breakout, VWAP)
- Combines signals with weighted voting
- Determines BUY_CALL or BUY_PUT

### 3. Select Strike
- Fetches options chain
- Selects ATM or OTM1 strike
- Calculates Greeks (Delta, Theta, Vega)

### 4. Apply Filters
- Delta > 0.35 (good exposure)
- IV < 40% (not expensive)
- Premium > ₹10 (avoid cheap)
- Confidence > 65% (high conviction)

### 5. Execute Trade
- Buy 1 lot (25 contracts)
- Cost: ~₹4,000 per position
- Track Greeks and P&L

### 6. Monitor & Exit
- Check every 5 minutes
- Exit at: 40% profit, 25% loss, high theta, or 3:15 PM

## 💡 Example Trade

```
Time: 10:30 AM
NIFTY Spot: ₹24,000
Signal: BUY CALL (Confidence: 72%)

Selected Option:
- Strike: 24,000 CE (ATM)
- Premium: ₹150
- Delta: 0.52
- Cost: ₹3,750 (25 contracts)

Exit: 12:45 PM @ ₹195
P&L: ₹1,040 profit (27.6%) ✅
```

## 🛡️ Safety Features

1. **Daily Loss Limit** - Stops at ₹500 loss
2. **Position Limits** - Max 2 positions
3. **Time Filters** - No trades after 2:30 PM
4. **Greeks Filters** - Delta, Theta, IV checks
5. **Forced Exit** - All positions closed at 3:15 PM
6. **Confidence Threshold** - Only high-conviction trades

## 📚 Documentation

- `OPTIONS_TRADING_GUIDE.md` - Complete guide with examples
- `PROJECT_STATUS.md` - Development status & roadmap
- `config/config.py` - All configuration options

## 🔧 Troubleshooting

### Bot won't start
```bash
# Install scipy
pip install scipy

# Test system
python test_options_system.py
```

### No trades generated
- Check confidence threshold (may be too high)
- Check time (no trades after 2:30 PM)
- Market may be sideways (fewer signals)

### High losses
- Verify stop loss is working (25%)
- Check theta decay monitoring
- Consider paper trading longer

## 📊 Expected Performance

**Week 1:** 5-10 trades, 40-50% win rate, learn system
**Month 1:** 20-40 trades, 50-55% win rate, stabilize
**Month 3:** 60-120 trades, 55-60% win rate, optimize

## ⚠️ Important Notes

### Paper Trading
- Bot uses simulated options data
- Premiums calculated using Black-Scholes
- For live trading, need real options chain API

### Live Trading (Future)
- Test thoroughly in paper mode first
- Start with small capital (₹10,000-25,000)
- Monitor closely for first week

### Limitations
- Simulated data may differ from real market
- No slippage or liquidity issues modeled
- Assumes instant execution

## 🎓 Learning Resources

### Options Basics
- Call = Right to buy (bullish)
- Put = Right to sell (bearish)
- ATM = Strike equals spot
- Greeks = Risk measures

### Key Concepts
- **Delta:** Directional exposure
- **Theta:** Time decay
- **Vega:** Volatility sensitivity
- **IV:** Implied volatility

## 📞 Support

For issues or questions:
1. Check `OPTIONS_TRADING_GUIDE.md`
2. Review `PROJECT_STATUS.md`
3. Test with `test_options_system.py`

## 📜 License

This is a personal trading bot for educational purposes.

## ⚠️ Disclaimer

Trading options involves substantial risk. This bot is for paper trading and educational purposes only. Past performance does not guarantee future results. Always do your own research and trade responsibly.

---

**Version 2.0 - Options Trading**  
*Built with Python, Pandas, NumPy, SciPy*  
*Integrated with AngelOne SmartAPI*

🚀 Ready to trade NIFTY options!
