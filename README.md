# 🤖 BitBot

> Modular, adaptive crypto trading bot built on CCXT with real-time execution, risk management, and Telegram control.

---

## 🚀 Overview

BitBot is a modular trading system designed for:

* ⚙️ Clean architecture and maintainability
* 📈 Real-time market execution
* 🧠 Strategy flexibility with RSI/SMA and predictive logic
* 🔐 Secure configuration using `.env`
* 💬 Remote control via Telegram

---

## ✨ Features

* 🔁 Continuous trading loop with configurable intervals
* 🎯 Dynamic Take-Profit / Stop-Loss (TP/SL)
* 📊 Volatility-aware trade logic
* 🧠 RSI + SMA strategy engine
* 🔮 Predictive trading mode
* 🛡️ Risk management with reserve protection and trade limits
* 💼 Portfolio tracking with drawdown monitoring
* 🧾 CSV trade logging
* 💬 Telegram command interface
* 🔄 Hot config reload

Full feature list: see [`features.md`](features.md)

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
```

### 2. Run BitBot

BitBot includes a helper script that automatically:

* Creates a virtual environment
* Installs dependencies
* Generates `config.json` if missing
* Generates `.env` if missing
* Launches the bot

```bash
./run.sh
```

### 3. First-Time Setup

On first run, the script will create:

* `config.json` from `config.example.json`
* `.env` from `env.example`

Edit `.env` before running the bot with real credentials:

```bash
nano .env
```

Example `.env`:

```env
BITMART_API_KEY=your_api_key
BITMART_API_SECRET=your_api_secret
BITMART_API_MEMO=your_api_memo

TELEGRAM_BOT_TOKEN=your_telegram_token
TELEGRAM_CHAT_ID=your_chat_id
```

After saving, run again:

```bash
./run.sh
```

---

## ▶️ Manual Run

If you prefer to run without the helper script:

```bash
python main.py
```

---

## 🧪 Manual Setup

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python main.py
```

---

## 💬 Telegram Commands

| Command          | Description                 |
| ---------------- | --------------------------- |
| `/pause`         | ⏸ Pause trading             |
| `/resume`        | ▶️ Resume trading           |
| `/status`        | 📊 Show live status         |
| `/config`        | 🧾 Show safe configuration  |
| `/rebase`        | 🔄 Reset TP/SL              |
| `/set key value` | ⚙️ Update config at runtime |
| `/buy`           | 🛒 Manual buy               |
| `/sell`          | 📉 Manual sell              |
| `/portfolio`     | 💼 Show portfolio value     |
| `/quote SYMBOL`  | 📡 Fetch market data        |
| `/lottery`       | 🎯 Utility feature          |
| `/help`          | ❓ Help menu                 |

---

## 🔐 Security

* API keys are stored in `.env`
* `config.json` is ignored by Git
* `config.example.json` is provided as a safe template
* `.gitignore` protects local secrets and runtime files

Never commit real exchange keys, Telegram tokens, or production configuration files.

---

## 📊 Example Output

```text
🔗 Trading Pair: SOL/USDT
💰 Balances: 0.000000 SOL | 0.024555 USDT
📈 Price: 67.376600
📊 Volatility: 0.000473 | Prediction: hold
🔒 TP: 68.419600 | ⚠️ SL: 66.806000
⏱ Uptime: 0:00:03
```

---

## 🧠 Strategy

Default strategy:

* RSI period: `14`
* SMA period: `20`
* Momentum crossover logic
* Predictive mode configurable via `config.json`

---

## 🔌 Exchange Support

BitBot is currently developed and tested using the **BitMart exchange** through CCXT.

Because the exchange layer is modular, BitBot can be adapted to other CCXT-supported centralized cryptocurrency exchanges, including:

* Binance
* Coinbase
* Kraken
* KuCoin
* Other CCXT-compatible crypto exchanges

> Note: Each exchange has different trading rules, including precision, minimum order size, rate limits, authentication, and symbol formats. Always test carefully before live trading.

---

## 🖥️ Environment Requirements

BitBot is designed to run in a lightweight Python environment with minimal dependencies.

### Supported Environment

* **Operating System**

  * Linux tested on Fedora
  * macOS should work
  * Windows via WSL recommended

* **Python Version**

  * Python 3.9+
  * Python 3.10 or newer recommended

* **Package Manager**

  * `pip`

### Core Dependencies

Installed via `requirements.txt`:

* `ccxt` — exchange integration
* `requests` — HTTP communication
* `numpy` — indicators and calculations
* `python-dotenv` — environment variable management

### System Requirements

* Internet connection
* Valid exchange API credentials
* Optional Telegram bot token for remote control

---

## 🛠️ Development

Run syntax checks:

```bash
python -m py_compile $(find . -name "*.py")
```

---

## 🗺️ Roadmap

* [ ] Multi-pair trading
* [ ] Trailing TP/SL
* [ ] PostgreSQL trade logging
* [ ] Dynamic web dashboard
* [ ] Backtesting module
* [ ] Strategy registry
* [ ] Enterprise deployment profile

---

## 📄 License

MIT License. See [`LICENSE`](LICENSE).

---

## ⚠️ Disclaimer

This software is for educational purposes only.

Cryptocurrency trading involves significant risk. Use at your own discretion. No financial advice is provided.

---

## 👤 Author

Michael Dietz
GitHub: [qualitypro](https://github.com/qualitypro)

---

💡 Built for adaptive, data-driven crypto trading.

