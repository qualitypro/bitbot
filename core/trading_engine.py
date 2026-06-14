import datetime
import time

from config.config_loader import load_config
from core.portfolio import Portfolio
from core.risk_manager import RiskManager


class TradingEngine:
    def __init__(self, config, exchange_client, strategy, telegram_service, start_time):
        self.config = config
        self.exchange_client = exchange_client
        self.strategy = strategy
        self.telegram = telegram_service
        self.start_time = start_time

        self.portfolio = Portfolio()
        self.risk = RiskManager(config)

        self.pair = exchange_client.pair
        self.base_asset = exchange_client.base_asset
        self.quote_asset = exchange_client.quote_asset

        self.tp = 0.0
        self.sl = 0.0
        self.locked_tp_sl = False

        self.last_price = None
        self.total_trades_today = 0
        self.successful_trades = 0
        self.failed_trades = 0
        self.bot_paused = False
        self.loop_count = 0

        self.buyback_pending = False
        self.buyback_price = 0.0

        self.current_day = datetime.datetime.now(datetime.timezone.utc).date()

        self.config_reload_interval = self.config.get("config_reload_interval_seconds", 3600)
        self.last_reload_time = datetime.datetime.now(datetime.timezone.utc)
        self.next_reload_time = self.last_reload_time + datetime.timedelta(
            seconds=self.config_reload_interval
        )

    def trading_loop(self):
        while True:
            self.loop_count += 1

            self.reload_config_if_needed()

            price_data = self.exchange_client.fetch_price()
            current_price = price_data["last"]
            volatility = self.exchange_client.fetch_volatility()

            if self.last_price is None:
                self.last_price = current_price

            self.daily_reset_check(current_price, volatility)

            if self.bot_paused:
                print("⏸ Bot is paused. Sleeping...")
                time.sleep(self.config.get("trade_interval_seconds", 90))
                continue

            prediction = self.strategy.get_signal()

            asset_bal, quote_bal = self.exchange_client.fetch_balance()
            portfolio_val = self.portfolio.calculate_value(
                asset_bal, quote_bal, current_price
            )
            drawdown = self.portfolio.update_max_drawdown(portfolio_val)
            last_trade_str = self.portfolio.get_time_since_last_trade()

            if not self.locked_tp_sl and self.tp != 0 and self.sl != 0:
                self.locked_tp_sl = True

            self.handle_tp_sell(current_price, asset_bal)
            self.handle_sl_sell(current_price, asset_bal)
            self.handle_buyback(current_price, quote_bal)
            self.handle_predictive_trade(prediction, current_price, asset_bal, quote_bal)

            if not self.locked_tp_sl:
                self.update_tp_sl(current_price, volatility)

            output = self.format_console_output(
                asset_bal=asset_bal,
                quote_bal=quote_bal,
                portfolio_val=portfolio_val,
                drawdown=drawdown,
                price_data=price_data,
                volatility=volatility,
                prediction=prediction,
                last_trade_str=last_trade_str,
            )

            print(output)

            if self.config.get("telegram_enabled", True):
                self.telegram.send(output)

            self.last_price = current_price
            time.sleep(self.config.get("trade_interval_seconds", 90))

    def place_order(self, side, amount, price, reason="Trade executed"):
        total_value = self.risk.get_order_value(amount, price)

        if self.risk.is_below_min_notional(amount, price):
            self.failed_trades += 1
            warning = (
                f"⚠️ Skipped {side.upper()} order: Value too small.\n"
                f"Amount: {amount:.6f} {self.base_asset}\n"
                f"Price: {price:.6f} {self.quote_asset}\n"
                f"Total: {total_value:.2f} USDT "
                f"(Minimum required: {self.risk.min_notional})\n"
                f"Reason: {reason}"
            )
            print(warning)
            self.exchange_client.trade_logger.log_trade(
                datetime.datetime.now(datetime.timezone.utc).isoformat(),
                side,
                amount,
                price,
                False,
                "Below minimum order value",
            )
            self.telegram.send(warning)
            return

        try:
            self.exchange_client.place_order(side, amount, price)

            self.total_trades_today += 1
            self.successful_trades += 1
            self.portfolio.mark_trade()
            self.locked_tp_sl = False

            print(
                f"✅ Placed {side.upper()} order for {amount:.6f} "
                f"{self.base_asset} at {price:.6f} {self.quote_asset} | Reason: {reason}"
            )

            self.exchange_client.trade_logger.log_trade(
                self.portfolio.last_trade_timestamp.isoformat(),
                side,
                amount,
                price,
                True,
                reason,
            )

            self.telegram.send(
                f"✅ {side.upper()} order placed:\n"
                f"Amount: {amount:.6f} {self.base_asset}\n"
                f"Price: {price:.6f} {self.quote_asset}\n"
                f"Reason: {reason}\n"
                f"Total trades today: {self.total_trades_today}"
            )

        except Exception as e:
            self.failed_trades += 1
            err_time = datetime.datetime.now(datetime.timezone.utc).isoformat()

            print(f"❌ Failed to place {side.upper()} order: {e} | Reason: {reason}")

            self.exchange_client.trade_logger.log_trade(
                err_time, side, amount, price, False, str(e)
            )

            self.telegram.send(
                f"❌ Failed {side.upper()} order:\n"
                f"Amount: {amount:.6f} {self.base_asset}\n"
                f"Price: {price:.6f} {self.quote_asset}\n"
                f"Reason: {reason}\n"
                f"Error: {e}"
            )

    def update_tp_sl(self, current_price, volatility):
        if not current_price or current_price <= 0:
            print("⚠️ Skipped TP/SL update due to invalid price data.")
            return

        factor = 1.0 + volatility

        new_tp = round(
            current_price * self.config.get("tp_multiplier", 1.015) * factor,
            self.exchange_client.price_precision,
        )
        new_sl = round(
            current_price * self.config.get("sl_multiplier", 0.992) / factor,
            self.exchange_client.price_precision,
        )

        if new_tp > new_sl and new_tp > 0 and new_sl > 0:
            self.tp = new_tp
            self.sl = new_sl
            print(f"🔒 Updated TP/SL with factor {factor:.2f}: 🚀 TP={self.tp}, ⚠️ SL={self.sl}")
        else:
            print("⚠️ Skipped TP/SL update due to invalid calculation. TP/SL unchanged.")

    def handle_tp_sell(self, current_price, asset_bal):
        if self.tp == 0 or current_price < self.tp:
            return

        reserve_asset = self.config.get("reserve_asset", 175.0)

        if self.bot_paused or asset_bal <= reserve_asset:
            return

        excess = self.risk.calculate_excess_asset(asset_bal, reserve_asset)
        amount_to_sell = round(
            excess * self.config.get("trade_portion", 0.33),
            self.exchange_client.amount_precision,
        )

        if amount_to_sell <= 0:
            return

        if self.risk.would_breach_reserve(asset_bal, amount_to_sell, reserve_asset):
            print(
                f"⛔ Sell would breach reserve. Skipping TP sell. "
                f"Balance: {asset_bal:.6f}, Attempted sell: {amount_to_sell:.6f}, "
                f"Reserve: {reserve_asset}"
            )
            return

        valid_price = self.get_valid_sell_price(current_price, "forced TP sell")
        if not valid_price:
            return

        if self.risk.is_below_min_notional(amount_to_sell, valid_price):
            amount_to_sell = self.risk.adjust_amount_to_min_notional(
                valid_price,
                self.exchange_client.amount_precision,
            )
            print(
                f"⚠️ Adjusted SELL order to meet minimum total.\n"
                f"New Amount: {amount_to_sell:.6f} Assets\n"
                f"Price: {valid_price:.6f} USDT\n"
                f"Total: {amount_to_sell * valid_price:.2f} USDT "
                f"(Minimum required: {self.risk.min_notional})\n"
                f"Reason: Forced sell if price hits TP"
            )

        self.place_order("sell", amount_to_sell, valid_price, "Forced sell if price hits TP")
        self.locked_tp_sl = False
        self.tp = 0.0
        self.sl = 0.0

    def handle_sl_sell(self, current_price, asset_bal):
        if self.sl == 0 or current_price > self.sl:
            return

        reserve_asset = self.config.get("reserve_asset", 175.0)

        if self.bot_paused or asset_bal <= reserve_asset:
            return

        excess = self.risk.calculate_excess_asset(asset_bal, reserve_asset)
        amount_to_sell = round(
            excess * self.config.get("trade_portion", 0.33),
            self.exchange_client.amount_precision,
        )

        if amount_to_sell <= 0:
            return

        if self.risk.would_breach_reserve(asset_bal, amount_to_sell, reserve_asset):
            print(
                f"⛔ Sell would breach reserve. Skipping SL sell. "
                f"Balance: {asset_bal:.6f}, Attempted sell: {amount_to_sell:.6f}, "
                f"Reserve: {reserve_asset}"
            )
            return

        valid_price = self.get_valid_sell_price(current_price, "forced SL sell")
        if not valid_price:
            return

        if self.risk.is_below_min_notional(amount_to_sell, valid_price):
            amount_to_sell = self.risk.adjust_amount_to_min_notional(
                valid_price,
                self.exchange_client.amount_precision,
            )
            print(
                f"⚠️ Adjusted SELL order to meet minimum total.\n"
                f"New Amount: {amount_to_sell:.6f} Assets\n"
                f"Price: {valid_price:.6f} USDT\n"
                f"Total: {amount_to_sell * valid_price:.2f} USDT "
                f"(Minimum required: {self.risk.min_notional})\n"
                f"Reason: Forced sell if price hits SL"
            )

        self.place_order("sell", amount_to_sell, valid_price, "Forced sell if price hits SL")

        self.locked_tp_sl = False
        self.buyback_pending = True
        self.buyback_price = round(self.sl * 0.995, self.exchange_client.price_precision)
        self.tp = 0.0
        self.sl = 0.0

    def handle_buyback(self, current_price, quote_bal):
        if not self.buyback_pending or current_price > self.buyback_price:
            return

        if current_price > 0:
            amount_to_buy = round(
                (quote_bal * 0.5) / current_price,
                self.exchange_client.amount_precision,
            )
        else:
            amount_to_buy = 0.0
            print("⚠️ Cannot calculate buy amount: current price is zero.")

        if amount_to_buy > 0 and not self.bot_paused:
            self.place_order("buy", amount_to_buy, current_price, "Forced Buyback")
            self.buyback_pending = False
            self.locked_tp_sl = False

    def handle_predictive_trade(self, prediction, current_price, asset_bal, quote_bal):
        if self.buyback_pending or self.bot_paused:
            return

        reserve_asset = self.config.get("reserve_asset", 175.0)

        if prediction == "sell" and asset_bal > reserve_asset:
            excess = self.risk.calculate_excess_asset(asset_bal, reserve_asset)
            amount_to_sell = round(
                excess * self.config.get("trade_portion", 0.33),
                self.exchange_client.amount_precision,
            )

            if amount_to_sell <= 0:
                return

            if self.risk.would_breach_reserve(asset_bal, amount_to_sell, reserve_asset):
                print(
                    f"⛔ Sell would breach reserve. Skipping predictive sell. "
                    f"Balance: {asset_bal:.6f}, Attempted sell: {amount_to_sell:.6f}, "
                    f"Reserve: {reserve_asset}"
                )
                return

            if self.risk.can_trade_today(self.total_trades_today):
                self.place_order(
                    "sell",
                    amount_to_sell,
                    current_price,
                    "Predictive logic triggered sell",
                )
                self.locked_tp_sl = False

        elif prediction == "buy":
            if current_price <= 0:
                return

            amount_to_buy = round(
                (quote_bal * self.config.get("trade_portion", 0.33)) / current_price,
                self.exchange_client.amount_precision,
            )

            if amount_to_buy > 0 and self.risk.can_trade_today(self.total_trades_today):
                self.place_order(
                    "buy",
                    amount_to_buy,
                    current_price,
                    "Predictive logic triggered buy",
                )
                self.locked_tp_sl = False

    def get_valid_sell_price(self, current_price, reason):
        valid_price = current_price

        if not self.risk.validate_price(valid_price):
            ticker = self.exchange_client.fetch_price()
            valid_price = ticker.get("bid", 0.0)

        if not self.risk.validate_price(valid_price):
            print(f"⚠️ Skipped SELL order: Invalid price during {reason}. Price={valid_price}")
            return None

        return valid_price

    def daily_reset_check(self, current_price, volatility):
        now_day = datetime.datetime.now(datetime.timezone.utc).date()

        if now_day != self.current_day:
            print("🔄 New day detected, resetting daily counters.")

            self.total_trades_today = 0
            self.successful_trades = 0
            self.failed_trades = 0
            self.portfolio.reset_daily_metrics()
            self.current_day = now_day

            self.update_tp_sl(current_price, volatility)
            print(
                f"📅 TP/SL rebased on new trading day at "
                f"{datetime.datetime.now(datetime.timezone.utc)}"
            )

    def reload_config_if_needed(self):
        now_utc = datetime.datetime.now(datetime.timezone.utc)

        if (now_utc - self.last_reload_time).total_seconds() < self.config_reload_interval:
            return

        print("🔄 Reloading config...")

        try:
            self.config = load_config("config.json")
            self.strategy.config = self.config
            self.risk = RiskManager(self.config)

            self.config_reload_interval = self.config.get(
                "config_reload_interval_seconds",
                self.config_reload_interval,
            )

            if self.config.get("rebase_on_config_reload", False):
                self.locked_tp_sl = False

            self.last_reload_time = now_utc
            self.next_reload_time = self.last_reload_time + datetime.timedelta(
                seconds=self.config_reload_interval
            )

        except Exception as e:
            print(f"⚠️ Error reloading config: {e}")

    def get_uptime(self):
        delta = datetime.datetime.now(datetime.timezone.utc) - self.start_time
        return str(delta).split(".")[0]

    def get_reload_countdown(self):
        delta = self.next_reload_time - datetime.datetime.now(datetime.timezone.utc)

        if delta.total_seconds() < 0:
            return "0m 0s"

        m, s = divmod(int(delta.total_seconds()), 60)
        return f"{m}m {s}s"

    def format_console_output(
        self,
        asset_bal,
        quote_bal,
        portfolio_val,
        drawdown,
        price_data,
        volatility,
        prediction,
        last_trade_str,
    ):
        tp_str = f"{self.tp:.6f}" if self.tp else "0.000000"
        sl_str = f"{self.sl:.6f}" if self.sl else "0.000000"

        prediction_mode_str = self.config.get("prediction_mode", "mechanical").capitalize()

        return (
            f"🔗 Trading Pair: {self.pair}\n"
            f"🕒 Loop #{self.loop_count} | 🕰 Exchange Time: "
            f"{self.exchange_client.get_natural_exchange_time()} | "
            f"Next config reload in {self.get_reload_countdown()}\n"
            f"💰 Balances: {asset_bal:.6f} {self.base_asset} | "
            f"{quote_bal:.6f} {self.quote_asset}\n"
            f"💼 Portfolio: {portfolio_val:.6f} {self.quote_asset} | "
            f"Max Drawdown: {drawdown:.2%}\n"
            f"📈 Price: {price_data['last']:.6f} | Open: {price_data['open']:.6f} | "
            f"24h Change: {price_data['percentage']:.2f}%\n"
            f"💹 High: {price_data['high']:.6f} | Low: {price_data['low']:.6f}\n"
            f"📊 Bid: {price_data['bid']:.6f} | Ask: {price_data['ask']:.6f}\n"
            f"📊 24h Volume: {price_data['base_volume']:.4f} {self.base_asset} | "
            f"{price_data['quote_volume']:.4f} {self.quote_asset}\n"
            f"📊 Volatility: {volatility:.6f} | Prediction: {prediction}\n"
            f"📊 Trades Today: {self.total_trades_today}/"
            f"{self.config.get('max_trades_per_day', 200)} | Last Trade: {last_trade_str}\n"
            f"🔒 TP: {tp_str} | ⚠️ SL: {sl_str}\n"
            f"🧠 Mode: {prediction_mode_str} Strategy\n"
            f"⏱ Uptime: {self.get_uptime()} | ❌ Failed Trades: {self.failed_trades} | "
            f"✅ Successful Trades: {self.successful_trades}\n"
            "------------------------------------------------------------"
        )

    def pause(self):
        self.bot_paused = True

    def resume(self):
        self.bot_paused = False

    def rebase(self):
        price_data = self.exchange_client.fetch_price()
        current_price = price_data.get("last", 0.0)
        volatility = self.exchange_client.fetch_volatility()

        self.locked_tp_sl = False
        self.update_tp_sl(current_price, volatility)

    def manual_buy(self):
        amount_to_buy = round(
            self.config.get("trade_amount_usdt", 10) / (self.last_price or 1),
            self.exchange_client.amount_precision,
        )
        self.place_order("buy", amount_to_buy, self.last_price or 0, "Manual buy via /buy command")
        return amount_to_buy

    def manual_sell(self):
        asset_bal, _ = self.exchange_client.fetch_balance()
        amount_to_sell = round(
            asset_bal * self.config.get("trade_portion", 0.33),
            self.exchange_client.amount_precision,
        )
        self.place_order("sell", amount_to_sell, self.last_price or 0, "Manual sell via /sell command")
        return amount_to_sell

    def portfolio_status(self):
        asset_bal, quote_bal = self.exchange_client.fetch_balance()
        portfolio_val = self.portfolio.calculate_value(
            asset_bal,
            quote_bal,
            self.last_price or 0,
        )
        return portfolio_val
