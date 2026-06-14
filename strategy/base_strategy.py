from abc import ABC, abstractmethod


class BaseStrategy(ABC):
    """
    Base strategy interface for BitBot.

    All strategy modules should implement:
    - get_signal()
    - predict_next_trade()

    This keeps strategy behavior pluggable while preserving
    the original bot's signal flow.
    """

    def __init__(self, exchange_client, config: dict):
        self.exchange_client = exchange_client
        self.config = config

    @abstractmethod
    def get_signal(self) -> str:
        """
        Return one of:
        - buy
        - sell
        - hold
        """
        pass

    def predict_next_trade(self, current_price: float) -> str:
        """
        Human-readable prediction/status text for Telegram /status.

        Child strategies may override this.
        """
        return "HOLD"
