"""Arias intensity and significant duration.

Computes the (normalized) Arias intensity curve, the significant duration
between two thresholds, the total Arias intensity and the destructiveness
potential. (Ported from EarthquakeSignal AriasIntensityAnalyzer.)
"""

import numpy as np


def compute(acc, dt, low=5, high=95):
    """Compute the Arias intensity curve and significant duration.

    Parameters
    ----------
    acc : np.ndarray
        Acceleration in m/s^2.
    dt : float
        Sampling interval in seconds.
    low, high : float, default 5, 95
        Percentages bounding the significant duration.

    Returns
    -------
    dict
        Keys: IA_percent, t_start, t_end, IA_total, pot_dest.
    """
    g = 9.81
    acc = np.asarray(acc, dtype=float)
    t = np.arange(len(acc)) * dt

    # Arias intensity curve (non-normalized), acc already in SI (m/s^2)
    IA = (np.pi / (2 * g)) * np.cumsum(acc ** 2) * dt
    IA_total = IA[-1]

    # Normalized to percent
    if IA_total > 0:
        IA_percent = 100 * IA / IA_total
    else:
        IA_percent = np.zeros_like(IA)

    # Significant duration between low% and high%
    idx_low = np.argmax(IA_percent >= low)
    idx_high = np.argmax(IA_percent >= high)
    t_start = t[idx_low]
    t_end = t[idx_high]

    # Zero-crossing rate of the acceleration signal
    cont_pd = np.count_nonzero(np.diff(np.sign(acc)))
    freq_cross = cont_pd / t[-1] if t[-1] > 0 else 0

    # Destructiveness potential
    pot_dest = IA_total / (freq_cross ** 2) if freq_cross > 0 else 0

    return {
        "IA_percent": IA_percent,
        "t_start": t_start,
        "t_end": t_end,
        "IA_total": IA_total,
        "pot_dest": pot_dest,
    }
