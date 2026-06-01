"""Cumulative Absolute Velocity (CAV).

Integral of the absolute acceleration over the record. A measure of the
accumulated energy / damage potential, beyond the simple peak.
"""


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
    raise NotImplementedError
