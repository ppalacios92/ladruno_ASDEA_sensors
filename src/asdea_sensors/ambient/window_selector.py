"""Automatic window selection.

Splits the signal into fixed-length windows and keeps the ones whose STA/LTA
ratio stays inside ``[vmin, vmax]`` (quiet, stationary windows). (Ported from
AmbientSoilPeriod window_selector.)
"""


def compute(fs, time, signal, ratio, vent, vmin, vmax):
    """Select stationary windows by STA/LTA thresholds.

    Parameters
    ----------
    fs : float
        Sampling frequency in Hz.
    time : np.ndarray
        Time vector in seconds.
    signal : np.ndarray
        Input signal (1-D).
    ratio : np.ndarray
        STA/LTA ratio of the signal.
    vent : float
        Window length in seconds.
    vmin, vmax : float
        Accepted STA/LTA range; a window is kept only if all its samples fall
        inside ``(vmin, vmax)``.

    Returns
    -------
    tuple
        ``(MT, MV, positions, win_ids)`` window time/signal matrices and ids.
    """
    raise NotImplementedError
