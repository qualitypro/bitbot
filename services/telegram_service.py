import json
import random
import statistics
import time

import requests

from config.config_loader import normalize_pair


WHITE_MIN = 1
WHITE_MAX = 69
WHITE_COUNT = 5
RED_MIN = 1
RED_MAX = 26

NY_RESULTS_URL = "https://data.ny.gov/resource/d6yy-54nr.json"


class TelegramService:
    def __init__(self, config: dict):
        self.config = config
        self.enabled = config.get("telegram_enabled", True)
        self.token = config.get("telegram_bot_token")
        self.chat_id = config.get("telegram_chat_id")
        self.update_offset = 0
        self.features_file = config.get("features_file", "features.md")
        self.features_text = self.load_features()

    def send(self, text: str):
        if not self.enabled or not self.token or not self.chat_id:
            return

        url = f"https://api.telegram.org/bot{self.token}/sendMessage"
        payload = {
            "chat_id": self.chat_id,
            "text": text,
            "parse_mode": "Markdown",
        }

        try:
            requests.post(url, data=payload, timeout=15)
        except Exception as e:
            print(f"⚠️ Exception sending telegram message: {e}")

    def load_features(self):
        try:
            with open(self.features_file, "r", encoding="utf-8") as f:
                return f.read()
        except Exception:
            return "No features file found."

    def send_feature_messages(self):
        for chunk in [
            self.features_text[i : i + 4000]
            for i in range(0, len(self.features_text), 4000)
        ]:
            self.send(chunk)

    def command_handler(self, engine):
        sensitive_keys = [
            "api_key",
            "api_secret",
            "api_memo",
            "password",
            "telegram_bot_token",
            "telegram_chat_id",
        ]

        while True:
            try:
                url = f"https://api.telegram.org/bot{self.token}/getUpdates"
                params = {
                    "offset": self.update_offset + 1,
                    "timeout": 10,
                }

                resp = requests.get(url, params=params, timeout=15)
                updates = resp.json()

                if not updates.get("ok"):
                    time.sleep(1)
                    continue

                for update in updates.get("result", []):
                    self.update_offset = update["update_id"]

                    message = update.get("message")
                    if not message:
                        continue

                    chat_id = message["chat"]["id"]
                    if str(chat_id) != str(self.chat_id):
                        continue

                    text = message.get("text", "")
                    if not text.startswith("/"):
                        continue

                    args = text.strip().split()
                    command = args[0].lower().split("@")[0]
                    command_args = args[1:]

                    if command == "/pause":
                        engine.pause()
                        self.send("⏸ Bot paused.")

                    elif command == "/resume":
                        engine.resume()
                        self.send("▶️ Bot resumed.")

                    elif command == "/status":
                        self.send_status(engine)

                    elif command == "/features":
                        self.send_feature_messages()

                    elif command == "/rebase":
                        engine.rebase()
                        self.send("🔄 TP/SL rebased manually.")

                    elif command == "/buy":
                        if engine.bot_paused:
                            self.send("⚠️ Bot is paused. Cannot execute buy.")
                        else:
                            amount = engine.manual_buy()
                            self.send(
                                f"🛒 Buy order placed for {amount} "
                                f"{engine.base_asset} at price {engine.last_price}"
                            )

                    elif command == "/sell":
                        if engine.bot_paused:
                            self.send("⚠️ Bot is paused. Cannot execute sell.")
                        else:
                            amount = engine.manual_sell()
                            self.send(
                                f"📉 Sell order placed for {amount} "
                                f"{engine.base_asset} at price {engine.last_price}"
                            )

                    elif command == "/set":
                        if len(command_args) < 2:
                            self.send("⚠️ Usage: /set key value")
                            continue

                        response = self.handle_set_command(engine, command_args)
                        self.send(response)

                    elif command == "/portfolio":
                        value = engine.portfolio_status()
                        self.send(
                            f"💼 Portfolio Value: {value:.6f} {engine.quote_asset}"
                        )

                    elif command == "/config":
                        safe_config = {
                            k: v
                            for k, v in engine.config.items()
                            if k not in sensitive_keys
                        }
                        pretty_json = json.dumps(safe_config, indent=2)
                        self.send(f"*Current Config:*\n```json\n{pretty_json}\n```")

                    elif command == "/quote":
                        self.handle_quote_command(engine, command_args)

                    elif command == "/lottery":
                        self.handle_lottery_command()

                    elif command == "/help":
                        self.send_help()

                    else:
                        self.send("⚠️ Unknown command. Use /help for list.")

            except Exception as e:
                print(f"⚠️ Telegram polling error: {e}")
                time.sleep(5)

    def send_status(self, engine):
        asset_bal, quote_bal = engine.exchange_client.fetch_balance()
        price_data = engine.exchange_client.fetch_price()
        current_price = price_data.get("last", engine.last_price or 0)

        portfolio_val = engine.portfolio.calculate_value(
            asset_bal,
            quote_bal,
            current_price,
        )
        drawdown = engine.portfolio.update_max_drawdown(portfolio_val)
        volatility = engine.exchange_client.fetch_volatility()
        prediction = engine.strategy.predict_next_trade(engine.last_price or 0)
        last_trade_str = engine.portfolio.get_time_since_last_trade()

        output = engine.format_console_output(
            asset_bal=asset_bal,
            quote_bal=quote_bal,
            portfolio_val=portfolio_val,
            drawdown=drawdown,
            price_data=price_data,
            volatility=volatility,
            prediction=prediction,
            last_trade_str=last_trade_str,
        )

        self.send(output)

    def handle_set_command(self, engine, args):
        key = args[0].lower()
        value = " ".join(args[1:]).strip()

        if key == "pair":
            try:
                old_base_asset = engine.base_asset

                new_pair = normalize_pair(value)
                new_base, new_quote = new_pair.split("/")

                engine.config["pair"] = new_pair
                engine.exchange_client.set_pair(new_pair)

                engine.pair = engine.exchange_client.pair
                engine.base_asset = new_base
                engine.quote_asset = new_quote

                engine.tp = 0.0
                engine.sl = 0.0
                engine.locked_tp_sl = False
                engine.last_price = None
                engine.portfolio.reset_daily_metrics()

                try:
                    balances = engine.exchange_client.exchange.fetch_balance()
                    free_old_base = balances.get(old_base_asset, {}).get("free", 0.0)

                    if free_old_base and free_old_base > 0.01:
                        self.send(
                            f"⚠️ Leftover balance of {free_old_base:.6f} "
                            f"{old_base_asset} detected after pair change. "
                            f"Consider selling or consolidating."
                        )
                except Exception as e:
                    print(f"⚠️ Error fetching balance for leftover check: {e}")

                return (
                    f"✅ Pair changed to {engine.pair} with "
                    f"Price precision {engine.exchange_client.price_precision} "
                    f"and Amount precision {engine.exchange_client.amount_precision}."
                )

            except Exception as e:
                return f"⚠️ Error setting pair: {e}"

        if key == "prediction_mode":
            if value.lower() in ["mechanical", "predictive"]:
                engine.config["prediction_mode"] = value.lower()
                engine.strategy.config = engine.config
                return f"🔁 Prediction mode set to: *{value.lower()}*"

            return "⚠️ Invalid mode. Use 'mechanical' or 'predictive'."

        if key in engine.config:
            old_value = engine.config.get(key)

            try:
                if isinstance(old_value, bool):
                    engine.config[key] = value.lower() in ["true", "1", "yes"]
                elif isinstance(old_value, int):
                    engine.config[key] = int(value)
                elif isinstance(old_value, float):
                    engine.config[key] = float(value)
                else:
                    engine.config[key] = value

                engine.strategy.config = engine.config
                engine.risk.config = engine.config

                return f"✅ Config key '{key}' set to {engine.config[key]}"

            except Exception:
                engine.config[key] = value
                return f"✅ Config key '{key}' set to {value}"

        return f"⚠️ Unknown config key '{key}'."

    def handle_quote_command(self, engine, command_args):
        if len(command_args) < 1:
            self.send("⚠️ Usage: /quote SYMBOL")
            return

        symbol_input = command_args[0].upper()

        try:
            markets = engine.exchange_client.exchange.load_markets()

            if "/" not in symbol_input:
                symbol = symbol_input + "/" + engine.quote_asset
            else:
                symbol = symbol_input

            if symbol not in markets:
                self.send(f"⚠️ Symbol {symbol} not found on exchange.")
                return

            market_info = markets[symbol]

            price_step = (
                market_info["precision"].get("price")
                or market_info.get("limits", {}).get("price", {}).get("min", 0.000001)
            )
            amount_step = (
                market_info["precision"].get("amount")
                or market_info.get("limits", {}).get("amount", {}).get("min", 1)
            )

            price_precision_local = engine.exchange_client.convert_step_to_precision(
                price_step
            )
            amount_precision_local = engine.exchange_client.convert_step_to_precision(
                amount_step
            )

            ticker = engine.exchange_client.exchange.fetch_ticker(symbol)

            price_data = {
                "last": round(ticker["last"], price_precision_local),
                "open": round(ticker["open"], price_precision_local),
                "percentage": ticker.get("percentage", 0.0) or 0.0,
                "high": round(ticker["high"], price_precision_local),
                "low": round(ticker["low"], price_precision_local),
                "bid": round(ticker["bid"], price_precision_local),
                "ask": round(ticker["ask"], price_precision_local),
                "base_volume": ticker.get("baseVolume", 0.0) or 0.0,
                "quote_volume": ticker.get("quoteVolume", 0.0) or 0.0,
            }

            window = int(engine.config.get("volatility_window_minutes", 60))
            since = engine.exchange_client.exchange.milliseconds() - window * 60 * 1000

            ohlcv = engine.exchange_client.exchange.fetch_ohlcv(
                symbol,
                timeframe="1m",
                since=since,
                limit=window,
            )

            closes = [candle[4] for candle in ohlcv if candle[4] is not None]

            if len(closes) >= 2:
                returns = [
                    (closes[i] - closes[i - 1]) / closes[i - 1]
                    for i in range(1, len(closes))
                ]
                volatility_local = (
                    statistics.stdev(returns) if len(returns) > 1 else 0.0
                )
            else:
                volatility_local = 0.0

            change_pct = price_data["percentage"]

            if change_pct >= 1.0:
                sentiment = "BUY ✅📈"
            elif change_pct <= -1.0:
                sentiment = "SELL ❌📉"
            else:
                sentiment = "HOLD ⏸️🟡"

            base, quote = symbol.split("/")

            output = (
                f"🔗 Trading Pair: {symbol}\n"
                f"📈 Price: {price_data['last']:.{price_precision_local}f} | "
                f"Open: {price_data['open']:.{price_precision_local}f} | "
                f"24h Change: {change_pct:.2f}%\n"
                f"💹 High: {price_data['high']:.{price_precision_local}f} | "
                f"Low: {price_data['low']:.{price_precision_local}f}\n"
                f"📊 Bid: {price_data['bid']:.{price_precision_local}f} | "
                f"Ask: {price_data['ask']:.{price_precision_local}f}\n"
                f"📊 24h Volume: {price_data['base_volume']:.4f} {base} | "
                f"{price_data['quote_volume']:.4f} {quote}\n"
                f"📊 Volatility: {volatility_local:.6f}\n"
                f"🔢 Decimal Precision: Price({price_precision_local}), "
                f"Amount({amount_precision_local})\n"
                f"📊 Sentiment: {sentiment}"
            )

            self.send(output)

        except Exception as e:
            self.send(f"⚠️ Error fetching quote: {e}")

    def fetch_powerball_history_full(self, limit: int = 5000):
        try:
            params = {
                "$order": "draw_date DESC",
                "$limit": limit,
            }

            resp = requests.get(NY_RESULTS_URL, params=params, timeout=15)

            if resp.status_code == 200:
                return resp.json()

            print(f"[Lottery] Failed to fetch history, status {resp.status_code}")
            return []

        except Exception as e:
            print(f"[Lottery] Error fetching Powerball data: {e}")
            return []

    def build_frequency_maps_from_history(self, history):
        white_freq = {n: 0 for n in range(WHITE_MIN, WHITE_MAX + 1)}
        red_freq = {n: 0 for n in range(RED_MIN, RED_MAX + 1)}

        for draw in history:
            try:
                winning_numbers = draw.get("winning_numbers", "")

                if not winning_numbers:
                    continue

                parts = winning_numbers.split()

                if len(parts) < WHITE_COUNT + 1:
                    continue

                whites = [int(x) for x in parts[:WHITE_COUNT]]
                red = int(parts[-1])

                for w in whites:
                    if WHITE_MIN <= w <= WHITE_MAX:
                        white_freq[w] += 1

                if RED_MIN <= red <= RED_MAX:
                    red_freq[red] += 1

            except Exception:
                continue

        return white_freq, red_freq

    def generate_powerball_smart_full(
        self,
        white_freq,
        red_freq,
        randomness_factor: float = 0.35,
    ):
        if not white_freq:
            whites = sorted(random.sample(range(WHITE_MIN, WHITE_MAX + 1), WHITE_COUNT))
            red = random.randint(RED_MIN, RED_MAX)
            return whites, red

        weighted_count = int(WHITE_COUNT * (1 - randomness_factor))
        weighted_count = max(1, min(WHITE_COUNT - 1, weighted_count))

        pool = list(white_freq.keys())
        weights = [white_freq[n] for n in pool]

        weighted_picks = set()

        while len(weighted_picks) < weighted_count and pool:
            pick = random.choices(pool, weights=weights, k=1)[0]
            weighted_picks.add(pick)

            idx = pool.index(pick)
            pool.pop(idx)
            weights.pop(idx)

        remaining_needed = WHITE_COUNT - len(weighted_picks)

        if pool:
            random_picks = set(random.sample(pool, remaining_needed))
        else:
            random_picks = set()

        whites = sorted(weighted_picks.union(random_picks))

        if red_freq and random.random() < (1 - randomness_factor):
            red = random.choices(
                list(red_freq.keys()),
                weights=list(red_freq.values()),
                k=1,
            )[0]
        else:
            red = random.randint(RED_MIN, RED_MAX)

        return whites, red

    def handle_lottery_command(self):
        history = self.fetch_powerball_history_full()

        if not history:
            self.send("⚠️ Could not fetch Powerball history. Try again later.")
            return

        white_freq, red_freq = self.build_frequency_maps_from_history(history)
        whites, red = self.generate_powerball_smart_full(white_freq, red_freq)

        msg = (
            "🎯 World-Saving Powerball (all history)\n"
            f"White balls: {', '.join(map(str, whites))}\n"
            f"Powerball: {red}\n"
            "Good luck — may the odds be ever in your favor. 🍀"
        )

        self.send(msg)

    def send_help(self):
        help_text = (
            "/pause - Pause the bot\n"
            "/resume - Resume the bot\n"
            "/status - Show current status\n"
            "/features - List bot features\n"
            "/rebase - Recalculate TP/SL\n"
            "/buy - Manual buy\n"
            "/sell - Manual sell\n"
            "/set key value - Change config key\n"
            "/portfolio - Show portfolio value\n"
            "/config - Show current config (without secrets)\n"
            "/quote SYMBOL - Show market data and sentiment\n"
            "/lottery - Generate Powerball numbers from full history\n"
            "/help - Show this message"
        )

        self.send(help_text)
