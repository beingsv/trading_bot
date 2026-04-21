# 🎛️ Dual Mode Trading Bot Guide

## Two Operating Modes

Your bot now supports TWO data modes:

### 1. MOCK DATA MODE (Testing)
- Uses randomly generated fake market data
- Fast, no API limits
- Perfect for testing bot logic
- Good for learning how the bot works
- **NOT useful for real trading preparation**

### 2. REAL DATA MODE (Production)
- Fetches actual market data from AngelOne
- Real prices, real movements
- Bot learns real market patterns
- Ready for live trading
- Uses AngelOne API (requires login)

---

## 🔧 How to Switch Modes

Edit `config/config.py`:

```python
# Data Source Mode
USE_MOCK_DATA = True   # For testing with fake data
USE_MOCK_DATA = False  # For real market data
```

---

## 📊 Current Setup

**Trading Mode:** Paper Trading (Virtual Money)
**Data Mode:** Mock Data (Fake Prices)

This means:
- ✅ No real money at risk
- ✅ Bot logic is being tested
- ❌ Not learning real market patterns
- ❌ Not ready for live trading

---

## 🎯 Recommended Workflow

### Phase 1: Test Bot Logic (NOW)
```python
PAPER_TRADING = True
USE_MOCK_DATA = True
```
- Run bot to test if everything works
- Check if strategies execute correctly
- Verify safety features work
- Test dashboard and graphs

### Phase 2: Learn Real Markets (TOMORROW)
```python
PAPER_TRADING = True
USE_MOCK_DATA = False
```
- Bot fetches real AngelOne data
- Analyzes actual market movements
- Learns real patterns
- Still uses virtual money (safe)
- Run for 1-2 months

### Phase 3: Live Trading (LATER)
```python
PAPER_TRADING = False
USE_MOCK_DATA = False
```
- Only after consistent profits in Phase 2
- Bot trades with real money
- Start with small capital
- Monitor closely

---

## 📈 Dashboard Indicators

All dashboards now show data source:

**Learning Dashboard:**
```
🧠 BOT LEARNING DASHBOARD
📊 Data Source: MOCK DATA
```

**Performance Graphs:**
```
📊 GENERATING PERFORMANCE GRAPHS
📊 Data Source: REAL-TIME ANGELONE
```

**Bot Startup:**
```
🚀 STARTING CONTINUOUS TRADING BOT
📝 Mode: PAPER TRADING
📊 Data Source: MOCK DATA
```

---

## ⚠️ Important Notes

### Mock Data Mode:
- Prices are random (₹1,000 - ₹3,000)
- No correlation with real market
- Volume is random
- News sentiment still real (from NewsAPI)
- Good for: Testing bot logic
- Bad for: Learning to trade

### Real Data Mode:
- Requires AngelOne login
- Uses API calls (within limits)
- Actual market prices
- Real volume data
- Real price movements
- Good for: Trading preparation
- Bad for: Quick testing (slower)

---

## 🚀 Quick Start

### Test Right Now (Mock Data):
```bash
# config/config.py
USE_MOCK_DATA = True

# Run bot
python run_bot_continuous.py
```

Bot will:
- Start immediately
- Use fake data
- Test all strategies
- Show you how it works
- No API limits

### Tomorrow Morning (Real Data):
```bash
# config/config.py
USE_MOCK_DATA = False

# Run bot
python run_bot_continuous.py
```

Bot will:
- Login to AngelOne
- Fetch real market data
- Analyze actual prices
- Learn real patterns
- Still paper trade (safe)

---

## 🎓 What You'll Learn

### From Mock Data:
- How strategies work
- How signals are generated
- How learning system works
- How safety features work
- Bot's decision-making process

### From Real Data:
- Which strategies work in real markets
- Best times to trade
- Stock-specific patterns
- Market condition impacts
- Actual win rates and P&L

---

## 💡 Pro Tips

1. **Start with Mock Data** - Test everything works
2. **Switch to Real Data** - Learn real patterns
3. **Run for 1 month** - Gather enough data
4. **Review Performance** - Check win rate > 60%
5. **Go Live** - Only when confident

---

## 🔍 How to Verify Mode

Check bot startup message:
```
📊 Data Source: MOCK DATA        ← Testing mode
📊 Data Source: REAL-TIME ANGELONE  ← Production mode
```

Check dashboard:
```
📊 Data Source: MOCK DATA        ← Learning from fake data
📊 Data Source: REAL-TIME ANGELONE  ← Learning from real data
```

---

## ❓ FAQ

**Q: Can I run both modes simultaneously?**
A: No, choose one mode at a time.

**Q: Will mock data trades affect real data performance?**
A: No, they're stored separately in the database.

**Q: Should I delete mock data before switching to real?**
A: Not necessary, but you can for cleaner analytics.

**Q: How do I know if real data is working?**
A: Check prices match actual market prices on NSE/BSE.

**Q: Can I switch modes mid-day?**
A: Yes, but restart the bot after changing config.

---

## 🎯 Your Next Steps

1. ✅ Run bot NOW with mock data (test everything)
2. ✅ Check dashboard and graphs work
3. ✅ Verify strategies execute
4. ✅ Tomorrow: Switch to real data
5. ✅ Let bot learn for 1 month
6. ✅ Review performance
7. ✅ Go live when ready

---

**Current Status:** Ready to test with mock data!
**Next Milestone:** Switch to real data tomorrow morning.

