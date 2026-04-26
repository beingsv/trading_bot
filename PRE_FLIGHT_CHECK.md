# ✈️ Pre-Flight Check - Ready to Run!

## ✅ System Status

### 1. Python Environment
- ✅ Python 3.14.4 installed
- ✅ Virtual environment exists (`venv/`)
- ✅ All dependencies installed:
  - ✅ scipy 1.17.1 (for Greeks calculation)
  - ✅ pandas 3.0.2 (for data processing)
  - ✅ numpy 2.4.4 (for calculations)
  - ✅ smartapi-python 1.5.5 (for AngelOne API)

### 2. Configuration
- ✅ API credentials configured in `config/.env`:
  - ✅ ANGELONE_API_KEY
  - ✅ ANGELONE_CLIENT_ID
  - ✅ ANGELONE_PASSWORD
  - ✅ ANGELONE_TOTP_SECRET
  - ✅ NEWS_API_KEY

### 3. Project Structure
- ✅ All options trading files present
- ✅ Old equity files removed
- ✅ Clean directory structure
- ✅ No old database/cache conflicts

### 4. Trading Configuration
- ✅ Trading Type: OPTIONS
- ✅ Index: NIFTY 50
- ✅ Capital: ₹10,000
- ✅ Paper Trading: Enabled
- ✅ Max Positions: 2
- ✅ Daily Loss Limit: ₹500

---

## 🚀 Ready to Run!

### Step 1: Test the System (Optional but Recommended)
```bash
source venv/bin/activate
python test_options_system.py
```

**Expected Output:**
```
🧪 Testing Options Trading System...

1️⃣ Testing Config...
   ✅ Config OK

2️⃣ Testing Options Greeks Calculator...
   ✅ Greeks Calculator OK

3️⃣ Testing Options Chain Fetcher...
   ✅ Options Chain OK

4️⃣ Testing Options Strategies...
   ✅ Strategies OK

5️⃣ Testing Options Paper Trading...
   ✅ Paper Trading OK

6️⃣ Testing Options Signal Generator...
   ✅ Signal Generator OK

✅ ALL TESTS PASSED!
```

### Step 2: Run the Bot
```bash
source venv/bin/activate
python run_options_bot.py
```

**What Will Happen:**
1. Bot logs into AngelOne
2. Waits for market open (9:15 AM)
3. Scans every 5 minutes
4. Generates BUY_CALL or BUY_PUT signals
5. Executes trades if confidence > 65%
6. Monitors positions
7. Exits all positions at 3:15 PM
8. Shows daily summary

---

## 📊 What to Expect

### First Run:
- Bot will create fresh database (`data/trading_bot.db`)
- New logs will be created in `logs/`
- May take 1-2 minutes to fetch initial data
- First scan will happen at 9:15 AM (or immediately if market is open)

### During Trading:
- Scan every 5 minutes
- Console output shows:
  - Current NIFTY spot price
  - Market condition
  - Open positions
  - Signals generated
  - Trades executed
  - P&L updates

### End of Day:
- All positions closed at 3:15 PM
- Daily summary displayed:
  - Total trades
  - Win rate
  - P&L
  - ROI
- Database backed up automatically

---

## 🎯 Trading Parameters

### Entry Criteria:
- ✅ Confidence > 65%
- ✅ Delta > 0.35
- ✅ IV < 40%
- ✅ Premium > ₹10
- ✅ Time < 2:30 PM
- ✅ Max 2 positions

### Exit Criteria:
- 40% profit target
- 25% stop loss
- Theta > 15% of premium
- 3:15 PM market close
- Opposite signal with high confidence

### Risk Management:
- Max loss per trade: ₹1,000 (25% of ₹4,000)
- Max daily loss: ₹500
- Position size: ₹4,000 (40% of capital)
- No overnight holding

---

## 📝 Monitoring Tips

### Watch For:
1. **Login Success** - Should see "✅ Login successful!"
2. **Data Fetching** - Should fetch NIFTY data without errors
3. **Signal Generation** - Should show BUY_CALL/BUY_PUT/HOLD
4. **Trade Execution** - Should show premium, delta, theta
5. **Position Monitoring** - Should check every 5 minutes
6. **Exit Execution** - Should exit at targets or 3:15 PM

### Normal Behavior:
- Many HOLD signals (bot is selective)
- 1-3 trades per day (not every scan)
- Some trades hit stop loss (normal)
- Win rate 40-60% initially
- Improves over time with learning

### Warning Signs:
- ❌ Login fails repeatedly
- ❌ No data fetched
- ❌ All trades losing
- ❌ Positions not exiting
- ❌ Errors in console

---

## 🛑 How to Stop

### During Market Hours:
```
Press Ctrl + C
```
- Bot will show current status
- Positions remain open
- Can restart anytime

### Graceful Shutdown:
- Wait until 3:15 PM
- Bot exits all positions automatically
- Shows daily summary
- Backs up database

---

## 📞 Troubleshooting

### If Login Fails:
1. Check API credentials in `config/.env`
2. Verify TOTP secret is correct
3. Check AngelOne account is active
4. Try logging in manually on AngelOne website

### If No Trades:
- Normal! Bot is selective (confidence > 65%)
- Market may be sideways (fewer signals)
- Check console for HOLD reasons
- May take 1-2 hours for first trade

### If Errors:
1. Check console output for error message
2. Verify all dependencies installed
3. Check internet connection
4. Restart bot

---

## 🎉 You're Ready!

Everything is configured and ready to go. The bot will:

✅ Trade NIFTY options only
✅ Use paper trading (no real money)
✅ Start with ₹10,000 virtual capital
✅ Learn from every trade
✅ Exit all positions by 3:15 PM
✅ Track performance and improve

**Run this command to start:**
```bash
source venv/bin/activate
python run_options_bot.py
```

**Good luck with your options trading! 🚀**

---

*Pre-flight check completed: April 23, 2026*
*All systems GO! ✈️*
