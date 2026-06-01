"""Housner spectral intensity (SI).

Area under the pseudo-velocity spectrum (PSv) between two periods, typically
0.1 to 2.5 s, the range relevant to buildings. Summarizes how severe a record
is for structures.
"""


def compute(acc, dt, T1=0.1, T2=2.5, zeta=0.05):
    """Compute the Housner spectral intensity.

    Parameters
    ----------
    acc : np.ndarray
        Acceleration in m/s^2.
    dt : float
        Sampling interval in seconds.
    T1, T2 : float, default 0.1, 2.5
        Integration period bounds in seconds.
    zeta : float, default 0.05
        Damping ratio used for the PSv spectrum.

    Returns
    -------
    dict
        Keys: SI.
    """
    raise NotImplementedError
