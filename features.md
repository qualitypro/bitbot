# 🤖 BitBot – Feature Overview

> Modular, adaptive crypto trading bot built on CCXT with real-time execution and Telegram control.

---

## ⚙️ Core Trading Engine
- 🔗 **Flexible Trading Pairs** – Supports configurable pairs (e.g., `SOL/USDT`)
- 🔁 **Continuous Execution Loop** – Runs at defined intervals (`trade_interval_seconds`)
- 🎯 **Dynamic TP/SL** – Configurable take-profit and stop-loss multipliers
- 📊 **Volatility-Aware Logic** – Adjusts TP/SL based on market conditions
- 🔒 **TP/SL Locking** – Prevents mid-cycle recalculations unless triggered

---

## 📈 Market Data & Analysis
- 📡 **Real-Time Market Data** – Powered by CCXT (ticker, bid/ask, volume)
- 📉 **Volatility Tracking** – Rolling OHLCV-based volatility calculation
- 🧠 **RSI + SMA Strategy** – Signal generation (BUY / SELL / HOLD)
- 🔮 **Predictive Mode** – Momentum-based trade signals

---

## 🛠️ Order & Risk Management
- 🧮 **Trade Sizing Control** – Uses `trade_portion` of available balance
- 🛡️ **Reserve Asset Protection** – Prevents full liquidation
- 💰 **Minimum Trade Enforcement** – Avoids orders below exchange limits
- 📆 **Daily Trade Limits** – Controlled via `max_trades_per_day`
- ⚡ **Automated TP/SL Execution** – Forced sell triggers
- 🔁 **Buyback Logic** – Re-entry after stop-loss events
- 🧾 **Trade Logging** – CSV logging (`trade_log.csv`) with full audit trail

---

## 💼 Portfolio Tracking
- 💰 **Live Portfolio Valuation**
- 📉 **Max Drawdown Monitoring**
- ⏱ **Trade Timing Metrics**
- 🟢 **Success / ❌ Failure Tracking**

---

## 💬 Telegram Integration *(Optional)*
- 🧵 **Async Command Handler** – Runs alongside trading loop
- 📊 **Real-Time Status Updates**:
  - 💼 Portfolio value & balances  
  - 📈 Market metrics  
  - 🔒 TP/SL state  
  - 📊 Volatility & prediction  
  - ⏱ Uptime & trade stats  

---

### 🤖 Supported Commands

| Command | Description |
|--------|-------------|
| `/pause` | ⏸ Pause trading |
| `/resume` | ▶️ Resume trading |
| `/status` | 📊 Show live bot status |
| `/config` | 🧾 View current config (safe fields only) |
| `/rebase` | 🔄 Recalculate TP/SL |
| `/features` | 📋 Show feature list |
| `/set key value` | ⚙️ Update config live |
| `/buy` | 🛒 Execute manual buy |
| `/sell` | 📉 Execute manual sell |
| `/portfolio` | 💼 Show portfolio value |
| `/quote SYMBOL` | 📡 Fetch market data |
| `/lottery` | 🎯 Utility: Powerball generator |
| `/help` | ❓ Show command list |

---

## 🧠 Configuration System
- 🗂️ **JSON-Based Config** – `config.json`
- 🔐 **Secure Secrets via `.env`**
- 🔄 **Hot Reload Support** – Reloads at runtime
- ⚙️ **Live Updates via Telegram** (`/set`)
- 🔁 **Optional TP/SL Rebase on Reload**

---

## 🧩 System Architecture
bitbot/
├── core/ # Trading engine, portfolio, risk
├── exchange/ # CCXT integration layer
├── strategy/ # Pluggable trading strategies
├── services/ # Telegram + logging
├── utils/ # Indicators, helpers, time
└── data/ # Trade logging

- 🧵 **Threaded Design** – Trading + Telegram in parallel
- 🎯 **Auto Precision Detection** – From exchange metadata
- 💽 **Balance Caching** – Reduces API load
- 🕒 **Natural Time Display** – Human-readable exchange time

---

## 🚀 Release

**Initial Modular Release**

Refactored from a monolithic trading script into a scalable, maintainable architecture while preserving full functionality.

---

💡 *Built for adaptive, data-driven crypto trading.*
