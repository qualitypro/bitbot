import time

import numpy as np

from strategy.base_strategy import BaseStrategy


class RSISMAStrategy(BaseStrategy):
    """
    RSI/SMA strategy extracted from the original ccxt_trading_bot.py.

    Preserves:
    - safe_fetch_ohlcv()
    - calculate_rsi()
    - calculate_sma()
    - get_rsi_sma_signal()
    - predict_next_trade()
    """

    def safe_fetch_ohlcv(
        self,
        timeframe: str = "5m",
        limit: int = 50,
        retries: int = 3,
        delay: int = 3,
    ):
        for attempt in range(retries):
            try:
                return self.exchange_client.fetch_ohlcv(
                    timeframe=timeframe,
                    limit=limit,
                )
            except Exception as e:
                print(f"⚠️ Attempt {attempt + 1} to fetch OHLCV failed: {e}")
                time.sleep(delay)

        print("❌ All OHLCV fetch attempts failed.")
        return []

    def calculate_rsi(self, prices, period: int = 14):
        deltas = np.diff(prices)
        seed = deltas[:period]

        up = seed[seed >= 0].sum() / period
        down = -seed[seed < 0].sum() / period

        rs = up / down if down != 0 else 0
        rsi = np.zeros_like(prices)
        rsi[:period] = 100.0 - 100.0 / (1.0 + rs)

        for i in range(period, len(prices)):
            delta = deltas[i - 1]

            if delta > 0:
                upval = delta
                downval = 0
            else:
                upval = 0
                downval = -delta

            up = (up * (period - 1) + upval) / period
            down = (down * (period - 1) + downval) / period

            rs = up / down if down != 0 else 0
            rsi[i] = 100.0 - 100.0 / (1.0 + rs)

        return rsi[-1]

    def calculate_sma(self, prices, period: int = 20):
        if len(prices) < period:
            return None

        return np.mean(prices[-period:])

    def get_signal(
        self,
        timeframe: str = "5m",
        rsi_period: int = 14,
        sma_period: int = 20,
    ) -> str:
        ohlcv = self.safe_fetch_ohlcv(
            timeframe=timeframe,
            limit=max(rsi_period, sma_period) + 5,
        )

        if not ohlcv or len(ohlcv) < max(rsi_period, sma_period):
            print("⚠️ Insufficient OHLCV data for RSI/SMA calculation.")
            return "hold"

        closes = [x[4] for x in ohlcv]

        rsi = self.calculate_rsi(np.array(closes), rsi_period)
        sma = self.calculate_sma(closes, sma_period)

        if sma is None:
            return "hold"

        current_price = closes[-1]
        previous_price = closes[-2]

        if rsi < 30 and previous_price < sma and current_price > sma:
            return "buy"

        if rsi > 70 and previous_price > sma and current_price < sma:
            return "sell"

        return "hold"

    def predict_next_trade(self, current_price: float) -> str:
        prediction_mode = self.config.get("prediction_mode", "mechanical")

        if prediction_mode != "predictive":
            return "HOLD (TP/SL only)"

        try:
            ohlcv = self.exchange_client.fetch_ohlcv(
                timeframe="1m",
                limit=100,
            )

            closes = [candle[4] for candle in ohlcv]

            gains = []
            losses = []

            for i in range(1, 15):
                change = closes[-i] - closes[-i - 1]

                if change >= 0:
                    gains.append(change)
                else:
                    losses.append(abs(change))

            avg_gain = sum(gains) / 14
            avg_loss = sum(losses) / 14

            rs = avg_gain / avg_loss if avg_loss != 0 else 0
            rsi = 100 - (100 / (1 + rs))

            sma_short = sum(closes[-5:]) / 5
            sma_long = sum(closes[-20:]) / 20

            if rsi < 30 and sma_short > sma_long:
                return "BUY (RSI+SMA)"

            if rsi > 70 and sma_short < sma_long:
                return "SELL (RSI+SMA)"

            return "HOLD"

        except Exception as e:
            print(f"⚠️ Prediction error: {e}")
            return "HOLD"
