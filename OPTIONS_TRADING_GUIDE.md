# NIFTY Options Trading Bot - Complete Guide

## 🎯 What Changed

Your bot has been completely transformed from **equity trading** to **options trading**:

### Before (Equity):
- Traded 10 stocks (ITC, SBIN, RELIANCE, etc.)
- Buy/sell shares
- 2% stop loss, 5% profit target
- Could hold positions
- 10 complex strategies

### After (Options):
- Trades NIFTY 50 index options only
- Buy Call (bullish) or Buy Put (bearish)
- 25% stop loss, 40% profit target
- Must exit by 3:15 PM (intraday only)
- 3 simplified strategies

---

## 📁 New File Structure

### New Files Created:
```
analysis/options_greeks.py          # Calculate Delta, Gamma, Theta, Vega
data/options_chain.py               # Fetch options chain, select strikes
strategies/options_strategies.py    # 3 options strategies
trading/options_paper_trading.py    # Options paper trading engine
trading/options_signal_generator.py # Generate BUY_CALL/BUY_PUT signals
run_options_bot.py                  # Main bot runner (USE THIS)
test_options_system.py              # Test all components
OPTIONS_TRADING_GUIDE.md            # This file
```

### Modified Files:
```
config/config.py                    # Options configuration
strategies/strategy_pool.py         # Auto-loads options strategies
requirements.txt                    # Added scipy
PROJECT_STATUS.md                   # Updated roadmap
```

### Old Files (Not Used Anymore):
```
run_bot_continuous.py               # Old equity bot
backtest_and_train.py               # Old equity backtest
strategies/predefined.py            # Old equity strategies (10 strategies)
```

---

## 🚀 How to Run

### Step 1: Install New Dependency
```bash
pip install scipy
```

### Step 2: Test the System
```bash
python test_options_system.py
```

This will verify:
- ✅ Config is correct
- ✅ Greeks calculator works
- ✅ Options chain fetcher works
- ✅ Strategies work
- ✅ Paper trading works
- ✅ Signal generator works

### Step 3: Run the Bot
```bash
python run_options_bot.py
```

The bot will:
1. Login to AngelOne
2. Wait for market open (9:15 AM)
3. Scan every 5 minutes
4. Generate BUY_CALL or BUY_PUT signals
5. Execute trades if confidence > 65%
6. Monitor positions for exit
7. Force exit all at 3:15 PM
8. Show daily summary

---

## 💡 How It Works

### Trading Logic:

**1. Fetch NIFTY Data**
- Gets 5-minute candles for NIFTY index
- Calculates RSI, MACD, Support/Resistance, VWAP

**2. Generate Signal (3 Strategies Vote)**

**Directional Strategy:**
- RSI < 40 + MACD bullish + Price > SMA = BUY CALL
- RSI > 60 + MACD bearish + Price < SMA = BUY PUT

**Breakout Strategy:**
- Price breaks above resistance = BUY CALL
- Price breaks below support = BUY PUT

**VWAP Strategy:**
- Price bounces off VWAP from below = BUY CALL
- Price rejects VWAP from above = BUY PUT

**3. Select Strike**
- Fetch options chain (all strikes, premiums, Greeks)
- Select ATM (at-the-money) or OTM1 (1 strike out)
- Best risk/reward ratio

**4. Apply Filters**
- ✅ Delta > 0.35 (good directional exposure)
- ✅ IV < 40% (not too expensive)
- ✅ Premium > ₹10 (avoid very cheap options)
- ✅ Time < 2:30 PM (avoid theta decay)
- ✅ Confidence > 65% (high conviction only)

**5. Execute Trade**
- Buy 1 lot (25 contracts for NIFTY)
- Cost: ~₹4,000 per position
- Max 2 positions (₹8,000 total)

**6. Monitor & Exit**
- Check every 5 minutes
- Exit if:
  - 40% profit (₹1,600 gain)
  - 25% loss (₹1,000 loss)
  - Theta > 15% of premium (time decay)
  - 3:15 PM (market close)
  - Opposite signal with high confidence

---

## 📊 Example Trade

**Scenario: Bullish Signal**

```
Time: 10:30 AM
NIFTY Spot: ₹24,000
Signal: BUY CALL (Confidence: 72%)
Reason: RSI oversold + MACD bullish + breakout above resistance

Selected Option:
- Strike: 24,000 CE (ATM)
- Premium: ₹150
- Delta: 0.52
- Theta: -8
- IV: 18%

Trade Execution:
- Buy 1 lot (25 contracts)
- Cost: ₹150 × 25 = ₹3,750
- Charges: ₹45
- Total: ₹3,795

Exit Scenarios:
1. Target: ₹210 (40% profit = ₹1,500)
2. Stop: ₹112 (25% loss = ₹950)
3. Time: 3:15 PM (force exit)

Actual Exit: 12:45 PM
- Exit Premium: ₹195 (30% profit)
- Proceeds: ₹195 × 25 = ₹4,875
- Charges: ₹40
- Net P&L: ₹4,875 - ₹40 - ₹3,795 = ₹1,040 ✅
```

---

## ⚙️ Configuration

All settings in `config/config.py`:

### Capital & Risk:
```python
INITIAL_CAPITAL = 10000          # ₹10,000 starting capital
POSITION_SIZE_PERCENT = 40       # 40% per trade (₹4,000)
MAX_POSITIONS = 2                # Max 2 positions
MAX_DAILY_LOSS = 500             # Stop at ₹500 loss
```

### Options Settings:
```python
STOP_LOSS_PERCENT = 25.0         # 25% stop loss
TAKE_PROFIT_PERCENT = 40.0       # 40% profit target
MAX_THETA_PERCENT = 15.0         # Exit if theta > 15%
MIN_DELTA = 0.35                 # Minimum delta
```

### Time Rules:
```python
NO_TRADE_AFTER_HOUR = 14         # No new trades after 2:30 PM
NO_TRADE_AFTER_MINUTE = 30
EXIT_ALL_BY_HOUR = 15            # Exit all by 3:15 PM
EXIT_ALL_BY_MINUTE = 15
INTRADAY_ONLY = True             # No overnight holding
```

### Index Config:
```python
PRIMARY_INDEX = 'NIFTY'          # Trade NIFTY options
LOT_SIZE = 25                    # 1 lot = 25 contracts
STRIKE_GAP = 50                  # ₹50 between strikes
EXPIRY_DAY = 'Thursday'          # Weekly expiry
```

---

## 📈 Expected Performance

### Realistic Expectations:

**Week 1 (Learning Phase):**
- Trades: 5-10
- Win Rate: 40-50%
- P&L: -₹200 to +₹500
- Goal: Understand system behavior

**Month 1 (Stabilization):**
- Trades: 20-40
- Win Rate: 50-55%
- P&L: +₹500 to +₹1,500
- Goal: Consistent execution

**Month 3 (Optimization):**
- Trades: 60-120
- Win Rate: 55-60%
- P&L: +₹2,000 to +₹4,000
- Goal: Profitable system

### Why Options Are Different:

**Advantages:**
- ✅ High leverage (control ₹24,000 with ₹4,000)
- ✅ Limited risk (max loss = premium paid)
- ✅ Can profit in any direction (calls or puts)
- ✅ Defined risk/reward

**Challenges:**
- ❌ Time decay (theta eats premium daily)
- ❌ Volatility risk (IV changes affect price)
- ❌ Can go to zero (if wrong direction)
- ❌ Must exit by 3:15 PM (no overnight)

---

## 🛡️ Safety Features

### Built-in Protections:

1. **Daily Loss Limit**
   - Stops trading at ₹500 loss
   - Prevents catastrophic losses

2. **Position Limits**
   - Max 2 positions (₹8,000 exposure)
   - Prevents over-trading

3. **Time-based Filters**
   - No trades after 2:30 PM
   - Avoids theta decay risk

4. **Greeks Filters**
   - Delta > 0.35 (good exposure)
   - Theta < 15% (manageable decay)
   - IV < 40% (not overpriced)

5. **Confidence Threshold**
   - Only trades with 65%+ confidence
   - Reduces low-quality trades

6. **Forced Exit**
   - All positions closed at 3:15 PM
   - No overnight risk

---

## 🔧 Troubleshooting

### Bot won't start:
```bash
# Check scipy is installed
pip install scipy

# Check config
python test_options_system.py
```

### No trades generated:
- Check confidence threshold (may be too high)
- Check time (no trades after 2:30 PM)
- Check filters (delta, IV, premium)
- Market may be sideways (fewer signals)

### Too many trades:
- Increase confidence threshold to 70-75%
- Tighten filters (delta > 0.40, IV < 30%)
- Reduce strategies (comment out one)

### High losses:
- Check stop loss is working (25%)
- Check theta decay monitoring
- May need to adjust entry criteria
- Consider paper trading longer

---

## 📚 Key Concepts

### Options Basics:

**Call Option (CE):**
- Right to BUY at strike price
- Buy when bullish (expect price to go UP)
- Profit if spot > strike + premium

**Put Option (PE):**
- Right to SELL at strike price
- Buy when bearish (expect price to go DOWN)
- Profit if spot < strike - premium

### Strike Selection:

**ATM (At-The-Money):**
- Strike = Spot price
- Highest delta (~0.50)
- Best risk/reward
- Most liquid

**OTM (Out-of-The-Money):**
- Call: Strike > Spot
- Put: Strike < Spot
- Lower delta (~0.30-0.40)
- Cheaper but riskier

**ITM (In-The-Money):**
- Call: Strike < Spot
- Put: Strike > Spot
- Higher delta (~0.60-0.80)
- Expensive, less leverage

### Greeks:

**Delta:**
- How much option price changes per ₹1 move in NIFTY
- Delta 0.50 = ₹0.50 move for every ₹1 NIFTY move
- Higher delta = more directional exposure

**Theta:**
- Time decay per day
- Theta -8 = option loses ₹8 per day
- Accelerates near expiry

**Vega:**
- Sensitivity to volatility (IV)
- High vega = price changes with IV
- Important during news events

**IV (Implied Volatility):**
- Market's expectation of future volatility
- High IV = expensive options
- Low IV = cheap options

---

## 🎓 Tips for Success

### Do's:
✅ Start with paper trading (₹10,000)
✅ Monitor first week closely
✅ Keep a trading journal
✅ Review daily summaries
✅ Adjust parameters gradually
✅ Focus on win rate > 50%
✅ Exit losing trades quickly
✅ Let winners run (to 40%)

### Don'ts:
❌ Don't trade with real money immediately
❌ Don't ignore stop losses
❌ Don't hold overnight
❌ Don't trade after 2:30 PM
❌ Don't buy very cheap options (<₹10)
❌ Don't buy high IV options (>40%)
❌ Don't revenge trade after losses

---

## 📞 Next Steps

### Immediate:
1. Run `python test_options_system.py`
2. Verify all tests pass
3. Run `python run_options_bot.py` tomorrow morning
4. Monitor first day closely

### This Week:
1. Paper trade for 5 days
2. Review daily summaries
3. Check win rate and P&L
4. Adjust confidence threshold if needed

### This Month:
1. Aim for 20-40 trades
2. Target 50%+ win rate
3. Positive net P&L
4. Understand system behavior

### After 3 Months:
1. If consistently profitable (55%+ win rate)
2. Consider scaling up capital
3. Add BANKNIFTY options
4. Explore advanced strategies

---

## 🚨 Important Notes

### Paper Trading:
- Bot uses **simulated options data**
- Premiums calculated using Black-Scholes
- Greeks are theoretical
- For live trading, need real options chain API

### Live Trading (Future):
- Requires real options chain data
- Need to integrate AngelOne options API
- Test thoroughly in paper mode first
- Start with small capital (₹10,000-25,000)

### Limitations:
- Simulated data may not match real market
- No slippage or liquidity issues modeled
- Assumes instant execution
- Greeks are theoretical

---

## 📊 Monitoring

### Daily Checklist:
- [ ] Check bot started successfully
- [ ] Verify login to AngelOne
- [ ] Monitor first trade execution
- [ ] Check position management
- [ ] Verify exits at 3:15 PM
- [ ] Review daily summary
- [ ] Check win rate trend

### Weekly Review:
- [ ] Total trades executed
- [ ] Win rate percentage
- [ ] Average P&L per trade
- [ ] Best performing strategy
- [ ] Worst performing strategy
- [ ] Adjust parameters if needed

---

## 🎉 Summary

You now have a complete **NIFTY Options Trading Bot** that:

✅ Trades options instead of stocks
✅ Uses 3 simplified strategies
✅ Calculates Greeks (Delta, Theta, Vega)
✅ Selects optimal strikes (ATM/OTM)
✅ Manages risk (25% SL, 40% TP)
✅ Exits by 3:15 PM (intraday only)
✅ Tracks performance and learns

**Ready to trade!** 🚀

Run: `python run_options_bot.py`

---

*Version 2.0 - Options Trading*
*Last Updated: April 23, 2026*
