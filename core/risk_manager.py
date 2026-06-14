class RiskManager:
    """
    Handles BitBot risk checks.

    This preserves the original behavior:
    - BitMart minimum notional check
    - reserve-asset protection
    - max trades per day check
    - minimum sell adjustment helper
    """

    def __init__(self, config: dict):
        self.config = config
        self.min_notional = float(config.get("min_notional_usdt", 5.0))

    def is_below_min_notional(self, amount: float, price: float) -> bool:
        return amount * price < self.min_notional

    def get_order_value(self, amount: float, price: float) -> float:
        return amount * price

    def can_trade_today(self, total_trades_today: int) -> bool:
        max_trades = int(self.config.get("max_trades_per_day", 200))
        return total_trades_today < max_trades

    def would_breach_reserve(
        self,
        asset_balance: float,
        amount_to_sell: float,
        reserve_asset: float,
    ) -> bool:
        return (asset_balance - amount_to_sell) < reserve_asset

    def calculate_excess_asset(
        self,
        asset_balance: float,
        reserve_asset: float,
    ) -> float:
        excess = asset_balance - reserve_asset
        return excess if excess > 0 else 0.0

    def adjust_amount_to_min_notional(
        self,
        price: float,
        amount_precision: int,
    ) -> float:
        if not price or price <= 0:
            return 0.0

        return round(self.min_notional / price, amount_precision)

    def validate_price(self, price: float) -> bool:
        return bool(price and price >= 0.000001)
