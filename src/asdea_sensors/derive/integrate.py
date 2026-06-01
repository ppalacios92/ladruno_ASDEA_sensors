"""Integration: acceleration -> velocity -> displacement.

Plain cumulative trapezoidal integration. The mean can be removed before
integrating to limit the drift that integration amplifies.
"""


def to_velocity(acc, dt, remove_mean=True):
    """Integrate acceleration (m/s^2) to velocity (m/s)."""
    raise NotImplementedError


def to_displacement(vel, dt, remove_mean=True):
    """Integrate velocity (m/s) to displacement (m)."""
    raise NotImplementedError


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
    raise NotImplementedError
