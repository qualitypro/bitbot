import numpy as np


def calculate_rsi(prices, period: int = 14):
    """
    Calculate RSI (Relative Strength Index).

    Extracted from original bot logic.
    """
    if len(prices) < period + 1:
        return None

    deltas = np.diff(prices)
    seed = deltas[:period]

    up = seed[seed >= 0].sum() / period
    down = -seed[seed < 0].sum() / period

    if down == 0:
        return 100.0

    rs = up / down
    rsi = 100.0 - (100.0 / (1.0 + rs))

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

        if down == 0:
            return 100.0

        rs = up / down
        rsi = 100.0 - (100.0 / (1.0 + rs))

    return rsi


def calculate_sma(prices, period: int = 20):
    """
    Simple Moving Average.
    """
    if len(prices) < period:
        return None

    return float(np.mean(prices[-period:]))


def calculate_returns(closes):
    """
    Percentage returns between consecutive closes.
    """
    if len(closes) < 2:
        return []

    return [
        (closes[i] - closes[i - 1]) / closes[i - 1]
        for i in range(1, len(closes))
        if closes[i - 1] != 0
    ]


def calculate_volatility(closes):
    """
    Standard deviation of returns (volatility proxy).
    """
    returns = calculate_returns(closes)

    if len(returns) < 2:
        return 0.0

    return float(np.std(returns))
