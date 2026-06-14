import math


def convert_step_to_precision(step):
    """
    Convert an exchange precision step into decimal places.

    Example:
    0.0001 -> 4
    0.01   -> 2
    1      -> 0
    """
    if step and step < 1:
        return abs(int(round(-math.log10(step))))

    return 0


def clamp(value, minimum, maximum):
    """
    Clamp a value between a minimum and maximum.
    """
    return max(minimum, min(value, maximum))


def safe_float(value, default=0.0):
    """
    Safely convert a value to float.
    """
    try:
        return float(value)
    except Exception:
        return default


def safe_int(value, default=0):
    """
    Safely convert a value to int.
    """
    try:
        return int(value)
    except Exception:
        return default
