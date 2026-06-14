import datetime
import threading

from config.config_loader import load_config
from exchange.bitmart_client import BitmartClient
from strategy.rsi_sma_strategy import RSISMAStrategy
from core.trading_engine import TradingEngine
from services.telegram_service import TelegramService
from services.logging_service import get_logger


def main():
    logger = get_logger("bitbot")
    config = load_config("config.json")

    start_time = datetime.datetime.now(datetime.timezone.utc)

    exchange_client = BitmartClient(config)
    telegram_service = TelegramService(config)

    strategy = RSISMAStrategy(
        exchange_client=exchange_client,
        config=config,
    )

    engine = TradingEngine(
        config=config,
        exchange_client=exchange_client,
        strategy=strategy,
        telegram_service=telegram_service,
        start_time=start_time,
    )

    if config.get("telegram_enabled", True):
        telegram_thread = threading.Thread(
            target=telegram_service.command_handler,
            args=(engine,),
            daemon=True,
        )
        telegram_thread.start()
        logger.info("Telegram command handler started.")

    try:
        engine.trading_loop()
    except KeyboardInterrupt:
        logger.info("🛑 Bot stopped by user.")
        print("🛑 Bot stopped by user.")


if __name__ == "__main__":
    main()
