import datetime


class Portfolio:
    """
    Tracks portfolio value, drawdown, and last-trade timing.

    This modularizes the original globals:
    - initial_portfolio_value
    - max_drawdown
    - last_trade_timestamp
    """

    def __init__(self):
        self.initial_portfolio_value = None
        self.max_drawdown = 0.0
        self.last_trade_timestamp = None

    def calculate_value(self, asset_balance: float, quote_balance: float, current_price: float) -> float:
        return asset_balance * current_price + quote_balance

    def update_max_drawdown(self, portfolio_value: float) -> float:
        if self.initial_portfolio_value is None:
            self.initial_portfolio_value = portfolio_value

        if self.initial_portfolio_value:
            drawdown = (
                self.initial_portfolio_value - portfolio_value
            ) / self.initial_portfolio_value
        else:
            drawdown = 0.0

        if drawdown > self.max_drawdown:
            self.max_drawdown = drawdown

        return self.max_drawdown

    def mark_trade(self):
        self.last_trade_timestamp = datetime.datetime.now(datetime.timezone.utc)

    def get_time_since_last_trade(self) -> str:
        if self.last_trade_timestamp is None:
            return "N/A"

        delta = datetime.datetime.now(datetime.timezone.utc) - self.last_trade_timestamp
        return str(delta).split(".")[0]

    def reset_daily_metrics(self):
        self.initial_portfolio_value = None
        self.max_drawdown = 0.0
