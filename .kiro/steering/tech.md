---
inclusion: auto
---

# Technology Stack

## Core Technologies

- Python 3.x
- SQLite database (trading_bot.db)
- AngelOne SmartAPI for market data and trading
- NewsAPI for sentiment analysis

## Key Libraries

### Market Data & Trading
- `smartapi-python` - AngelOne API client
- `pandas`, `numpy`, `scipy` - Data processing

### Technical Analysis
- `ta-lib` - Technical indicators (requires system installation)
- `pandas-ta` - Additional technical analysis

### Machine Learning
- `scikit-learn` - Strategy learning
- `tensorflow`, `keras` - Deep learning models

### Sentiment Analysis
- `newsapi-python` - News fetching
- `newspaper3k` - Article scraping
- `textblob` - Basic sentiment
- `transformers` - Advanced NLP

### Utilities
- `python-dotenv` - Environment configuration
- `requests`, `beautifulsoup4` - Web scraping
- `schedule` - Task scheduling
- `pytz` - Timezone handling

## Common Commands

### Setup
```bash
# Install dependencies
pip install -r requirements.txt

# Install TA-Lib (macOS)
brew install ta-lib

# Install TA-Lib (Ubuntu)
sudo apt-get install ta-lib

# Configure environment
cp config/.env.example config/.env
# Edit config/.env with API credentials
```

### Running
```bash
# Run the bot
python main.py
```

### Development
```bash
# No test suite currently defined
# No build/compile steps required (Python)
```

## Configuration

- Environment variables: `config/.env`
- Bot parameters: `config/config.py`
- Database: `data/trading_bot.db` (auto-created)
- Logs: `logs/` directory
