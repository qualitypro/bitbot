import ccxt
import datetime
import math
import statistics
import time

from config.config_loader import normalize_pair
from data.trade_logger import TradeLogger


class BitmartClient:
    def __init__(self, config: dict):
        self.config = config

        self.api_key = config.get("api_key")
        self.api_secret = config.get("api_secret")
        self.api_memo = config.get("api_memo")

        self.pair = normalize_pair(config["pair"])
        self.base_asset, self.quote_asset = self.pair.split("/")

        self.exchange = ccxt.bitmart(
            {
                "apiKey": self.api_key,
                "secret": self.api_secret,
                "uid": self.api_memo,
                "enableRateLimit": True,
            }
        )

        self.trade_logger = TradeLogger(config.get("trade_log", "trade_log.csv"))

        self.price_precision = 6
        self.amount_precision = 6

        self.balance_cache = None
        self.balance_cache_time = 0

        self._load_market_metadata()

    def convert_step_to_precision(self, step):
        if step and step < 1:
            return abs(int(round(-math.log10(step))))
        return 0

    def _load_market_metadata(self):
        try:
            markets = self.exchange.load_markets()

            if self.pair not in markets:
                raise ValueError(f"Pair {self.pair} not available on BitMart.")

            market = markets[self.pair]

            price_step = (
                market["precision"].get("price")
                or market.get("limits", {}).get("price", {}).get("min", 0.000001)
            )
            amount_step = (
                market["precision"].get("amount")
                or market.get("limits", {}).get("amount", {}).get("min", 1)
            )

            self.price_precision = self.convert_step_to_precision(price_step)
            self.amount_precision = self.convert_step_to_precision(amount_step)

            print(
                f"ℹ️ Auto-detected precision: "
                f"Price={self.price_precision}, Amount={self.amount_precision}"
            )

        except Exception as e:
            print(f"⚠️ Failed to auto-detect precision, using default: {e}")
            self.price_precision = 6
            self.amount_precision = 6

    def set_pair(self, pair: str):
        self.pair = normalize_pair(pair)
        self.base_asset, self.quote_asset = self.pair.split("/")
        self.balance_cache = None
        self.balance_cache_time = 0
        self._load_market_metadata()

    def get_natural_exchange_time(self):
        try:
            server_time = self.exchange.fetch_time()
            dt = datetime.datetime.fromtimestamp(
                server_time / 1000,
                datetime.timezone.utc,
            )
            return dt.strftime("%B %-d, %Y at %H:%M:%S UTC")
        except Exception:
            return datetime.datetime.utcnow().strftime(
                "%B %-d, %Y at %H:%M:%S UTC"
            )

    def fetch_balance(self):
        now_ts = time.time()
        ttl = self.config.get("balance_cache_ttl_seconds", 60)

        if self.balance_cache and now_ts - self.balance_cache_time < ttl:
            return self.balance_cache

        try:
            balances = self.exchange.fetch_balance()

            asset_bal = balances.get(self.base_asset, {}).get("free", 0.0)
            quote_bal = balances.get(self.quote_asset, {}).get("free", 0.0)

            self.balance_cache = (asset_bal, quote_bal)
            self.balance_cache_time = now_ts

            return asset_bal, quote_bal

        except Exception as e:
            print(f"⚠️ Exception fetching balance: {e}")
            return 0.0, 0.0

    def fetch_price(self):
        try:
            ticker = self.exchange.fetch_ticker(self.pair)

            return {
                "last": round(ticker["last"], self.price_precision),
                "open": round(ticker["open"], self.price_precision),
                "percentage": ticker.get("percentage", 0.0) or 0.0,
                "high": round(ticker["high"], self.price_precision),
                "low": round(ticker["low"], self.price_precision),
                "bid": round(ticker["bid"], self.price_precision),
                "ask": round(ticker["ask"], self.price_precision),
                "base_volume": ticker.get("baseVolume", 0.0) or 0.0,
                "quote_volume": ticker.get("quoteVolume", 0.0) or 0.0,
            }

        except Exception as e:
            print(f"⚠️ Exception fetching price: {e}")
            return {
                "last": 0.0,
                "open": 0.0,
                "percentage": 0.0,
                "high": 0.0,
                "low": 0.0,
                "bid": 0.0,
                "ask": 0.0,
                "base_volume": 0.0,
                "quote_volume": 0.0,
            }

    def fetch_volatility(self):
        try:
            window = int(self.config.get("volatility_window_minutes", 60))
            since = self.exchange.milliseconds() - window * 60 * 1000

            ohlcv = self.exchange.fetch_ohlcv(
                self.pair,
                timeframe="1m",
                since=since,
                limit=window,
            )

            closes = [candle[4] for candle in ohlcv if candle[4] is not None]

            if len(closes) < 2:
                return 0.0

            returns = [
                (closes[i] - closes[i - 1]) / closes[i - 1]
                for i in range(1, len(closes))
            ]

            return statistics.stdev(returns) if len(returns) > 1 else 0.0

        except Exception as e:
            print(f"⚠️ Exception fetching volatility: {e}")
            return 0.0

    def fetch_ohlcv(self, pair=None, timeframe="5m", limit=50, since=None):
        symbol = normalize_pair(pair) if pair else self.pair

        return self.exchange.fetch_ohlcv(
            symbol,
            timeframe=timeframe,
            since=since,
            limit=limit,
        )

    def place_order(self, side: str, amount: float, price: float):
        if side == "buy":
            return self.exchange.create_limit_buy_order(
                self.pair,
                amount,
                price,
            )

        return self.exchange.create_limit_sell_order(
            self.pair,
            amount,
            price,
        )
