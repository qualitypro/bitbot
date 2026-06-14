import datetime


def utc_now():
    """
    Return current UTC datetime.
    """
    return datetime.datetime.now(datetime.timezone.utc)


def utc_today():
    """
    Return current UTC date.
    """
    return utc_now().date()


def format_duration(delta: datetime.timedelta) -> str:
    """
    Format timedelta like original bot output.

    Example:
    1:23:45
    """
    return str(delta).split(".")[0]


def get_uptime(start_time: datetime.datetime) -> str:
    """
    Calculate uptime from bot start time.
    """
    return format_duration(utc_now() - start_time)


def get_reload_countdown(next_reload_time: datetime.datetime) -> str:
    """
    Return countdown until next config reload.

    Original format:
    Xm Ys
    """
    delta = next_reload_time - utc_now()

    if delta.total_seconds() < 0:
        return "0m 0s"

    minutes, seconds = divmod(int(delta.total_seconds()), 60)
    return f"{minutes}m {seconds}s"


def format_exchange_time_from_ms(server_time_ms: int) -> str:
    """
    Convert exchange server timestamp in milliseconds to readable UTC string.
    """
    dt = datetime.datetime.fromtimestamp(
        server_time_ms / 1000,
        datetime.timezone.utc,
    )

    return dt.strftime("%B %-d, %Y at %H:%M:%S UTC")


def fallback_utc_exchange_time() -> str:
    """
    Fallback exchange time when exchange.fetch_time() fails.
    """
    return datetime.datetime.utcnow().strftime("%B %-d, %Y at %H:%M:%S UTC")
