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

```text
bitbot/
├── core/        # Trading engine, portfolio, risk management
├── exchange/    # CCXT exchange integration layer
├── strategy/    # Trading strategies
├── services/    # Telegram integration and logging
├── utils/       # Indicators, helpers, time utilities
├── data/        # Trade logging and data handling
├── config/      # Configuration loader
└── main.py      # Entry point
```

---

## ⚙️ Installation & Quick Start

### 1. Clone the Repository

```bash
git clone https://github.com/qualitypro/bitbot.git
cd bitbot
2. Run BitBot (One Command) 🚀

BitBot includes a helper script that automatically:

Creates a virtual environment
Installs dependencies
Generates config.json (if missing)
Generates .env (if missing)
Launches the bot
./run.sh
⚠️ First-Time Setup Required

On first run, the script will create:

config.json from config.example.json
.env from env.example

You must edit .env before running again:

nano .env

Add your credentials:

BITMART_API_KEY=your_api_key
BITMART_API_SECRET=your_api_secret
BITMART_API_MEMO=your_api_memo

TELEGRAM_BOT_TOKEN=your_telegram_token
TELEGRAM_CHAT_ID=your_chat_id

After saving, run again:

./run.sh
▶️ Manual Run (Optional)

If you prefer to run without the script:

python main.py
🧪 Manual Setup (Advanced)
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
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

MIT License

Copyright (c) 2026 qualitypro

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.

⚠️ Disclaimer

This software is for educational purposes only.
Trading cryptocurrency involves risk. Use at your own discretion.

👤 Author

Michael Dietz
GitHub: https://github.com/qualitypro

💡 Built for adaptive, data-driven crypto trading.
