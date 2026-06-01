"""Window service: turn a start + length (or two bounds) into a sample range.

The windows are lazy: they only store the bounds. Reading happens later and
honours the window, so cutting a window never touches the data.
"""

from datetime import timedelta

import pandas as pd

# Multipliers from a unit suffix to seconds.
_UNIT_SECONDS = {
    "h": 3600.0,
    "hour": 3600.0,
    "hours": 3600.0,
    "hr": 3600.0,
    "m": 60.0,
    "min": 60.0,
    "mins": 60.0,
    "minute": 60.0,
    "minutes": 60.0,
    "s": 1.0,
    "sec": 1.0,
    "secs": 1.0,
    "second": 1.0,
    "seconds": 1.0,
}


def parse_duration(length):
    """Convert a duration into seconds.

    Parameters
    ----------
    length : str or float
        "60min", "300sec", "2hour", "90s", "1.5h", or a number of seconds.

    Returns
    -------
    float
        Duration in seconds.
    """
    # A plain number is already seconds.
    if isinstance(length, (int, float)):
        return float(length)

    text = str(length).strip().lower()

    # Split the leading numeric part from the trailing unit suffix.
    split = len(text)
    for i, ch in enumerate(text):
        if ch.isalpha():
            split = i
            break

    number = text[:split].strip()
    unit = text[split:].strip()

    if number == "":
        raise ValueError("duration has no numeric part: %r" % (length,))

    value = float(number)

    if unit == "":
        return value

    if unit not in _UNIT_SECONDS:
        raise ValueError("unknown duration unit: %r" % (unit,))

    return value * _UNIT_SECONDS[unit]


def _resolve_time(index, device, when):
    """Resolve ``when`` into an absolute timestamp.

    ``when`` may be an ISO string, a datetime, or an integer sample index
    counted from the start of the first indexed file.
    """
    # Integer sample index: offset from the first file's start time.
    if isinstance(when, int) and not isinstance(when, bool):
        if not index.files:
            raise ValueError("index has no files to resolve a sample position")
        start = index.files[0][0]
        dt = index.dt if index.dt is not None else 0.0
        return pd.Timestamp(start) + timedelta(seconds=when * dt)

    # Strings and datetimes are parsed by pandas.
    return pd.Timestamp(pd.to_datetime(when))


def window_from_start(index, device, start, length):
    """Return the ``(t0, t1)`` bounds for a start plus a duration.

    Parameters
    ----------
    index : H5Index
        Index used to resolve absolute time into sample positions.
    device : str
    start : str, datetime or int
        Window start (ISO string, datetime, or sample index).
    length : str or float
        Duration, see :func:`parse_duration`.
    """
    t0 = _resolve_time(index, device, start)
    t1 = t0 + timedelta(seconds=parse_duration(length))
    return t0, t1


def window_from_bounds(index, device, t0, t1):
    """Return the ``(t0, t1)`` bounds resolved from explicit start/end times."""
    a = _resolve_time(index, device, t0)
    b = _resolve_time(index, device, t1)
    return a, b
