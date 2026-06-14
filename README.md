# 🤖 BitBot

> Modular, adaptive crypto trading bot built on CCXT with real-time execution, risk management, and Telegram control.

---

## 🚀 Overview

BitBot is a fully modular trading system designed for:

- ⚙️ Clean architecture and maintainability  
- 📈 Real-time market execution  
- 🧠 Strategy flexibility (RSI/SMA + predictive logic)  
- 🔒 Secure configuration using `.env`  
- 💬 Remote control via Telegram  

---

## ✨ Features

- 🔁 Continuous trading loop with configurable intervals  
- 🎯 Dynamic Take-Profit / Stop-Loss (TP/SL)  
- 📊 Volatility-aware trade logic  
- 🧠 RSI + SMA strategy engine  
- 🔮 Predictive trading mode  
- 🛡️ Risk management (reserve protection, trade limits)  
- 💼 Portfolio tracking with drawdown monitoring  
- 🧾 CSV trade logging  
- 💬 Telegram command interface  
- 🔄 Hot config reload  

📋 Full feature list: see [`features.md`](features.md)

---

## 🧩 Architecture
bitbot/
├── core/ # Trading engine, portfolio, risk
├── exchange/ # CCXT exchange integration
├── strategy/ # Trading strategies
├── services/ # Telegram + logging
├── utils/ # Indicators, helpers, time
├── data/ # Trade logging
├── config/ # Config loader
├── main.py # Entry point
---

## ⚙️ Installation

### 1. Clone the repo

```bash
git clone https://github.com/qualitypro/bitbot.git
cd bitbot
2. Install dependencies
pip install ccxt requests numpy python-dotenv
3. Configure environment

Create your config and environment files:

cp config.example.json config.json
cp env.example .env

Edit .env:

BITMART_API_KEY=your_key
BITMART_API_SECRET=your_secret
BITMART_API_MEMO=your_memo

TELEGRAM_BOT_TOKEN=your_token
TELEGRAM_CHAT_ID=your_chat_id
▶️ Running the Bot
python main.py
💬 Telegram Commands
Command	Description
/pause	⏸ Pause trading
/resume	▶️ Resume trading
/status	📊 Show live status
/config	🧾 Show config
/rebase	🔄 Reset TP/SL
/set key value	⚙️ Update config
/buy	🛒 Manual buy
/sell	📉 Manual sell
/portfolio	💼 Portfolio value
/quote SYMBOL	📡 Market data
/lottery	🎯 Utility feature
/help	❓ Help menu
🔐 Security
🔒 API keys stored in .env (never commit secrets)
🧾 config.example.json provided for safe templates
🚫 .gitignore protects sensitive files
📊 Example Output
🔗 Trading Pair: SOL/USDT
💰 Balances: 0.000000 SOL | 0.024555 USDT
📈 Price: 67.376600
📊 Volatility: 0.000473 | Prediction: hold
🔒 TP: 68.419600 | ⚠️ SL: 66.806000
⏱ Uptime: 0:00:03
🧠 Strategy

Default strategy:

RSI (14)
SMA (20)
Momentum crossover logic
Predictive mode optional via config
🛠️ Development

Run syntax check:

python -m py_compile $(find . -name "*.py")
🚀 Roadmap
 Multi-pair trading
 Trailing TP/SL
 Backtesting module
 Strategy marketplace
 Web dashboard
📄 License

TBD (MIT recommended)

⚠️ Disclaimer

This software is for educational purposes only.
Trading cryptocurrency involves risk. Use at your own discretion.

👤 Author

Michael Dietz
GitHub: https://github.com/qualitypro

💡 Built for adaptive, data-driven crypto trading.
