import os
import json
from pathlib import Path

from dotenv import load_dotenv


# Load environment variables from .env
load_dotenv()


def load_config(config_path: str = "config.json") -> dict:
    """
    Load configuration from JSON and inject secrets from .env.

    Preserves original behavior while adding secure secret handling.
    """
    path = Path(config_path)

    if not path.exists():
        raise FileNotFoundError(f"Config file not found: {config_path}")

    with path.open("r", encoding="utf-8") as f:
        config = json.load(f)

    # --- Inject secrets from .env ---
    config["api_key"] = os.getenv("BITMART_API_KEY")
    config["api_secret"] = os.getenv("BITMART_API_SECRET")
    config["api_memo"] = os.getenv("BITMART_API_MEMO")

    config["telegram_bot_token"] = os.getenv("TELEGRAM_BOT_TOKEN")
    config["telegram_chat_id"] = os.getenv("TELEGRAM_CHAT_ID")

    return config


def reload_config(config_path: str = "config.json") -> dict:
    """
    Reload config at runtime.
    """
    return load_config(config_path)


def normalize_pair(raw_pair: str) -> str:
    """
    Normalize trading pair format.

    Supports:
    - SOL_USDT
    - SOL/USDT
    """
    if not raw_pair:
        raise ValueError("Pair cannot be empty.")

    raw_pair = raw_pair.upper().strip()

    if "/" in raw_pair:
        return raw_pair

    if "_" in raw_pair:
        return raw_pair.replace("_", "/")

    raise ValueError(
        f"Invalid pair format: {raw_pair}, expected 'BASE/QUOTE' or 'BASE_QUOTE'"
    )
