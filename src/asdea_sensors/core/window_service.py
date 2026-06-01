"""Window service: turn a start + length (or two bounds) into a sample range.

The windows are lazy: they only store the bounds. Reading happens later and
honours the window, so cutting a window never touches the data.
"""


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
    raise NotImplementedError


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
    raise NotImplementedError


def window_from_bounds(index, device, t0, t1):
    """Return the ``(t0, t1)`` bounds resolved from explicit start/end times."""
    raise NotImplementedError
