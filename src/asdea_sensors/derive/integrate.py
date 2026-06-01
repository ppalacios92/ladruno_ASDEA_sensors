"""Integration: acceleration -> velocity -> displacement.

Plain cumulative trapezoidal integration. The mean can be removed before
integrating to limit the drift that integration amplifies.
"""

import numpy as np
from scipy.integrate import cumulative_trapezoid


def to_velocity(acc, dt, remove_mean=True):
    """Integrate acceleration (m/s^2) to velocity (m/s)."""
    acc = np.asarray(acc, dtype=float)
    if remove_mean:
        acc = acc - acc.mean()
    return cumulative_trapezoid(acc, dx=dt, initial=0)


def to_displacement(vel, dt, remove_mean=True):
    """Integrate velocity (m/s) to displacement (m)."""
    vel = np.asarray(vel, dtype=float)
    if remove_mean:
        vel = vel - vel.mean()
    return cumulative_trapezoid(vel, dx=dt, initial=0)


def derive(acc, dt, remove_mean=True):
    """Return ``(vel, disp)`` from an acceleration array.

    Parameters
    ----------
    acc : np.ndarray
        Acceleration in m/s^2.
    dt : float
        Sampling interval in seconds.
    remove_mean : bool, default True
        Remove the mean before each integration step.
    """
    vel = to_velocity(acc, dt, remove_mean=remove_mean)
    disp = to_displacement(vel, dt, remove_mean=remove_mean)
    return vel, disp
