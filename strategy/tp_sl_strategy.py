from strategy.base_strategy import BaseStrategy


class TPSLStrategy(BaseStrategy):
    """
    TP/SL strategy placeholder.

    In the original ccxt_trading_bot.py, TP/SL is not a standalone signal strategy.
    TP/SL execution is handled directly inside the trading loop:

    - forced sell if price >= TP
    - forced sell if price <= SL
    - buyback after SL
    - rebase TP/SL when unlocked

    In the modular version, that behavior currently lives in core/trading_engine.py.

    This class exists so TP/SL can become a pluggable strategy later without changing
    the project structure.
    """

    def get_signal(self) -> str:
        return "hold"

    def predict_next_trade(self, current_price: float) -> str:
        return "HOLD (TP/SL only)"
