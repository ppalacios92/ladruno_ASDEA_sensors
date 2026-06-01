"""Automatic window selection.

Splits the signal into fixed-length windows and keeps the ones whose STA/LTA
ratio stays inside ``[vmin, vmax]`` (quiet, stationary windows). (Ported from
AmbientSoilPeriod window_selector.)
"""

import numpy as np


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
    np_samples = int(fs * vent)
    end_index = len(time) - 2 * np_samples + 1

    MT = []
    MV = []
    positions = []
    win_ids = []

    for i, a in enumerate(range(0, end_index + 1, np_samples)):
        segment = ratio[a:a + np_samples]
        if segment.shape[0] < np_samples:
            continue
        if np.all((segment > vmin) & (segment < vmax)):
            MT.append(time[a:a + np_samples])
            MV.append(signal[a:a + np_samples])
            positions.append(a)
            win_ids.append(i)

    MT = np.column_stack(MT) if MT else np.empty((np_samples, 0))
    MV = np.column_stack(MV) if MV else np.empty((np_samples, 0))
    positions = np.array(positions)
    win_ids = np.array(win_ids)

    return MT, MV, positions, win_ids
