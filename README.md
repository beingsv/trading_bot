# Intra Trading Bot - AI-Powered Indian Market Trading System

## Overview
Self-learning trading bot for Indian markets (AngelOne) that:
- Learns trading strategies from historical data
- Monitors multiple market factors (technical, news, global markets, FII/DII, etc.)
- Performs paper trading with virtual money
- Generates buy/sell signals based on comprehensive analysis
- Continuously learns from trading mistakes and successes

## Features
- **Multi-Factor Analysis**: Technical indicators, news sentiment, global markets, currency, sector trends
- **Strategy Learning**: Evolves and adapts trading strategies based on performance
- **Paper Trading**: Risk-free testing with virtual money
- **Real-time Signals**: Buy/sell/hold recommendations
- **Performance Tracking**: Learns from every trade
- **Market Condition Detection**: Adapts to bull/bear/sideways markets

## Project Structure
```
intra-trading-bot/
├── config/              # Configuration and API keys
├── data/                # Data fetching and storage
├── analysis/            # Market analysis modules
├── strategies/          # Trading strategy system
├── trading/             # Trading execution
├── learning/            # ML and feedback systems
├── main.py             # Bot orchestrator
└── requirements.txt    # Dependencies
```

## Setup
1. Install dependencies: `pip install -r requirements.txt`
2. Configure AngelOne API credentials in `config/config.py`
3. Run: `python main.py`

## Status
🚧 Under Development
