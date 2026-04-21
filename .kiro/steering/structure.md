---
inclusion: auto
---

# Project Structure

## Directory Organization

```
intra-trading-bot/
├── config/              # Configuration and credentials
├── data/                # Data fetching and storage
├── analysis/            # Market analysis modules
├── strategies/          # Trading strategy system
├── trading/             # Trade execution engines
├── learning/            # ML and feedback loops
├── main.py             # Bot orchestrator (entry point)
└── requirements.txt    # Python dependencies
```

## Module Responsibilities

### config/
- `config.py` - Central configuration (API keys, trading params, watchlist)
- `.env` - Environment variables (credentials, secrets)
- `.env.example` - Template for environment setup

### data/
- `fetcher.py` - Fetch market data from AngelOne, NSE, news sources
- `storage.py` - Database operations (SQLite)

### analysis/
- `technical.py` - Technical indicators (RSI, MACD, Bollinger Bands, etc.)
- `news_sentiment.py` - News scraping and sentiment analysis

### strategies/
- `base_strategy.py` - Abstract base class for all strategies
- `predefined.py` - 6 predefined trading strategies
- `strategy_pool.py` - Strategy management and selection

### trading/
- `angelone_api.py` - AngelOne API wrapper
- `paper_trading.py` - Paper trading engine with virtual capital
- `signal_generator.py` - Consensus signal generation

### learning/
- `feedback_loop.py` - Learn from trade outcomes
- `market_conditions.py` - Detect market regime (bull/bear/sideways)

## Architecture Patterns

### Strategy Pattern
All trading strategies inherit from `BaseStrategy` abstract class:
- Must implement `generate_signal(data, market_context)` method
- Returns dict with `action`, `confidence`, `reason`
- Tracks own performance metrics

### Data Flow
1. `DataFetcher` pulls market data
2. `analysis/` modules process data
3. `StrategyPool` generates signals from multiple strategies
4. `SignalGenerator` creates weighted consensus
5. `PaperTradingEngine` executes trades
6. `FeedbackLoop` updates strategy performance

### Configuration Management
- Use `config/config.py` for constants and parameters
- Use `.env` for secrets (never commit)
- All modules import from `config.config`

## Coding Conventions

### Class Design
- Use descriptive class names (e.g., `PaperTradingEngine`, `DataFetcher`)
- Keep classes focused on single responsibility
- Use docstrings for all classes and public methods

### Error Handling
- Wrap external API calls in try-except blocks
- Print error messages with context
- Return None or empty DataFrame on failure

### Data Structures
- Use pandas DataFrame for OHLCV data
- Use dict for signals: `{'action': str, 'confidence': float, 'reason': str}`
- Use dict for market context and metadata

### Constants
- Define all magic numbers in `config/config.py`
- Use UPPER_CASE for constants
- Group related constants together
