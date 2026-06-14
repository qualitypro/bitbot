import csv


class TradeLogger:
    """
    CSV trade logger.

    This preserves the original log_trade() behavior:
    timestamp, trade_type, amount, price, success, reason
    """

    def __init__(self, trade_log_file: str = "trade_log.csv"):
        self.trade_log_file = trade_log_file

    def log_trade(
        self,
        timestamp: str,
        trade_type: str,
        amount: float,
        price: float,
        success: bool,
        reason: str = "",
    ):
        try:
            with open(self.trade_log_file, "a", newline="", encoding="utf-8") as csvfile:
                writer = csv.writer(csvfile)
                writer.writerow(
                    [timestamp, trade_type, amount, price, success, reason]
                )
        except Exception as e:
            print(f"⚠️ Exception logging trade: {e}")
