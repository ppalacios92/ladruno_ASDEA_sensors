"""Base rocking: rotation of the foundation.

Estimates the rocking of the base from the base sensor (and, when available,
the difference between base sensors), to assess soil-foundation flexibility.
"""


def compute(acc_vertical, dt, base_width=None, acc_vertical_b=None):
    """Estimate the base rocking.

    Parameters
    ----------
    acc_vertical : np.ndarray
        Vertical acceleration at the base, m/s^2.
    dt : float
        Sampling interval in seconds.
    base_width : float or None
        Plan distance between the two base points (when two are available),
        to turn a vertical difference into a rocking angle.
    acc_vertical_b : np.ndarray or None
        Vertical acceleration at a second base point.

    Returns
    -------
    dict
        Keys: rocking (time history), spectrum, rocking_freq.
    """
    raise NotImplementedError
