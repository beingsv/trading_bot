# 📊 Options Backtesting Guide

## What is Backtesting?

Backtesting lets you train your bot on historical data. Instead of waiting for live market, you can:
- ✅ Test on past dates
- ✅ Train bot quickly
- ✅ See what would have happened
- ✅ Improve strategies
- ✅ Build confidence before live trading

## 🚀 How to Use

### Single Day Backtest
```bash
source venv/bin/activate
python backtest_options.py 2026-04-22
```

This will:
1. Fetch NIFTY data from April 22, 2026
2. Simulate options chain for that day
3. Run through the day candle-by-candle
4. Generate signals and execute trades
5. Show results at end
6. Bot learns from those trades

### Multiple Days Backtest
```bash
python backtest_options.py 2026-04-01 2026-04-22
```

This will backtest every trading day from April 1 to April 22.

## 📊 Example Output

```
🤖 Initializing Options Backtester...
✅ Backtester initialized

🔐 Logging into AngelOne...
✅ Login successful!

============================================================
📅 BACKTESTING: 2026-04-22
============================================================

📊 Fetching NIFTY data for 22 April 2026...
✅ Fetched 78 candles for 2026-04-22

🌍 Market Condition: BULL_TRENDING
💰 Starting Capital: ₹10,000

────────────────────────────────────────────────────────────
🔍 Scan #1 - 09:20 AM
💹 NIFTY: ₹24,125.50
📦 Open Positions: 0/2
📡 Signal: BUY_CALL (72%)
💼 24100 CE @ ₹185.50
✅ BUY 1 lot NIFTY 24100 CE @ ₹185.50
   Delta: 0.54 | Theta: -15.20 | Charges: ₹25.50
   Capital: ₹5,451.00

────────────────────────────────────────────────────────────
🔍 Scan #15 - 11:35 AM
💹 NIFTY: ₹24,285.00
📦 Open Positions: 1/2
🚪 Exiting: Take profit hit at 42.3%
🟢 SELL 1 lot NIFTY 24100 CE @ ₹263.80
   P&L: ₹1,901.50 (41.0%) | Held: 135min | Charges: ₹55.20
   Capital: ₹11,901.50

============================================================
⏰ End of Day - Closing All Positions
============================================================

============================================================
📊 BACKTEST RESULTS
============================================================
💰 Starting Capital: ₹10,000.00
💰 Ending Capital: ₹11,901.50
📈 Total P&L: ₹1,901.50
📊 ROI: 19.02%
📝 Total Trades: 3
✅ Winning Trades: 2
❌ Losing Trades: 1
🎯 Win Rate: 66.7%
💵 Avg P&L per Trade: ₹633.83
============================================================
```

## 💡 Use Cases

### 1. Train Before Live Trading
```bash
# Train on last 10 days
python backtest_options.py 2026-04-10 2026-04-22
```

Bot will:
- Execute 10-30 trades
- Learn patterns
- Adjust strategy weights
- Build experience

### 2. Test Strategy Changes
```bash
# Modify config/config.py (change thresholds, etc.)
# Then backtest to see impact
python backtest_options.py 2026-04-22
```

### 3. Find Best Parameters
```bash
# Try different settings:
# - Confidence threshold (65% vs 70%)
# - Stop loss (20% vs 25%)
# - Position size (30% vs 40%)

# Backtest each and compare results
```

### 4. Validate Bot Logic
```bash
# Before going live, backtest recent days
python backtest_options.py 2026-04-20 2026-04-22

# Check:
# - Win rate > 50%
# - Positive P&L
# - Reasonable trade count
```

## 📈 What Gets Trained

When you backtest, the bot learns:

1. **Strategy Performance**
   - Which strategies work better
   - Adjusts weights accordingly
   - Stores in database

2. **Market Patterns**
   - Bull vs Bear vs Sideways
   - Best times to trade
   - Risk/reward ratios

3. **Trade Execution**
   - Entry timing
   - Exit timing
   - Position sizing

4. **Risk Management**
   - Stop loss effectiveness
   - Take profit levels
   - Daily loss limits

## ⚠️ Important Notes

### Limitations:

1. **Simulated Options Data**
   - Options premiums calculated using Black-Scholes
   - Not actual historical options prices
   - Greeks are theoretical

2. **No Slippage**
   - Assumes instant execution
   - Real trading has delays
   - Prices may move

3. **Perfect Information**
   - Backtesting uses actual data
   - Live trading has uncertainty
   - Results may differ

4. **News Sentiment**
   - Set to neutral (0) in backtest
   - Real trading uses live news
   - May affect signals

### Best Practices:

✅ **Do:**
- Backtest multiple days (10-20)
- Compare different parameters
- Check win rate and P&L
- Use recent dates (last month)
- Verify bot logic works

❌ **Don't:**
- Over-optimize on one day
- Expect exact same results live
- Ignore risk management
- Skip paper trading after backtest
- Trade real money immediately

## 🎯 Recommended Workflow

### Week 1: Training
```bash
# Day 1-2: Backtest last 10 days
python backtest_options.py 2026-04-10 2026-04-22

# Day 3-4: Adjust parameters based on results
# Edit config/config.py

# Day 5: Backtest again to verify improvements
python backtest_options.py 2026-04-15 2026-04-22
```

### Week 2: Validation
```bash
# Day 1-3: Paper trade live (3 days)
python run_options_bot.py

# Day 4-5: Compare backtest vs paper trading
# Check if results are similar
```

### Week 3+: Live Trading
```bash
# If paper trading successful:
# - Win rate > 50%
# - Positive P&L
# - Consistent performance

# Consider live trading with small capital
```

## 📊 Interpreting Results

### Good Results:
- ✅ Win rate: 50-60%
- ✅ ROI: 5-15% per day
- ✅ Trades: 2-5 per day
- ✅ Avg P&L: Positive
- ✅ Max drawdown: < 10%

### Warning Signs:
- ❌ Win rate: < 40%
- ❌ ROI: Negative
- ❌ Trades: 0 or 10+
- ❌ Avg P&L: Negative
- ❌ Max drawdown: > 20%

### What to Adjust:

**If win rate low:**
- Increase confidence threshold (65% → 70%)
- Tighten filters (delta, IV)
- Reduce trade frequency

**If no trades:**
- Lower confidence threshold (65% → 60%)
- Loosen filters
- Check market condition

**If too many losses:**
- Tighten stop loss (25% → 20%)
- Increase take profit (40% → 50%)
- Check strategy weights

## 🔧 Advanced Usage

### Custom Date Range
```bash
# Last week
python backtest_options.py 2026-04-15 2026-04-22

# Last month
python backtest_options.py 2026-03-22 2026-04-22

# Specific volatile day
python backtest_options.py 2026-04-10
```

### Compare Strategies
```bash
# Backtest with all 3 strategies
python backtest_options.py 2026-04-22

# Disable one strategy in code
# Backtest again
# Compare results
```

### Optimize Parameters
```bash
# Try confidence 65%
# Edit config.py: MIN_CONFIDENCE = 65
python backtest_options.py 2026-04-22

# Try confidence 70%
# Edit config.py: MIN_CONFIDENCE = 70
python backtest_options.py 2026-04-22

# Compare which is better
```

## 📝 Tips

1. **Start with recent dates** - Last 1-2 weeks
2. **Backtest 10-20 days** - Build good sample size
3. **Check consistency** - Win rate should be stable
4. **Compare to paper trading** - Results should align
5. **Don't over-optimize** - Focus on robustness
6. **Use as training** - Bot learns from backtest
7. **Verify logic** - Make sure bot behaves correctly

## 🎉 Summary

Backtesting is your bot's training ground:
- ✅ Fast learning (days in minutes)
- ✅ No risk (simulated trades)
- ✅ Build confidence
- ✅ Optimize parameters
- ✅ Validate strategies

**Use it before live trading!**

---

*Happy Backtesting! 📊*
