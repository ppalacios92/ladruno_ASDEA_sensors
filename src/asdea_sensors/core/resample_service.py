"""Resample service: change the sampling rate of a signal, a sensor, or the
whole dataset. Useful as a preprocessing step to standardize dt before any
analysis.
"""


def resample_signal(signal, dt_in, dt_out=None, fs_out=None):
    """Resample one signal array to a target dt or fs.

    Parameters
    ----------
    signal : np.ndarray
        Input samples (1-D).
    dt_in : float
        Current sampling interval in seconds.
    dt_out : float or None
        Target sampling interval in seconds.
    fs_out : float or None
        Target sampling frequency in Hz (alternative to ``dt_out``).

    Returns
    -------
    np.ndarray
        Resampled signal.
    """
    raise NotImplementedError


def target_dt(dt=None, fs=None):
    """Resolve a target dt from either ``dt`` or ``fs`` (exactly one given)."""
    raise NotImplementedError
