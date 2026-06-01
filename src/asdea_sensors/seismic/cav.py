"""Cumulative Absolute Velocity (CAV).

Integral of the absolute acceleration over the record. A measure of the
accumulated energy / damage potential, beyond the simple peak.
"""

import numpy as np
from scipy.integrate import cumulative_trapezoid


def compute(acc, dt):
    """Compute the CAV of an acceleration record.

    Parameters
    ----------
    acc : np.ndarray
        Acceleration in m/s^2.
    dt : float
        Sampling interval in seconds.

    Returns
    -------
    dict
        Keys: CAV (total), curve (the cumulative curve in time).
    """
    acc = np.asarray(acc, dtype=float)

    # Cumulative integral of |acc| over time; prepend 0 to match input length
    curve = cumulative_trapezoid(np.abs(acc), dx=dt, initial=0)
    CAV = curve[-1] if len(curve) else 0.0

    return {"CAV": CAV, "curve": curve}
