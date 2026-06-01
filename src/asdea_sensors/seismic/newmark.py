"""Newmark response spectrum (linear acceleration / beta method).

Solves a single-degree-of-freedom system for a range of periods and returns
the spectral quantities plus the time histories. (Ported from EarthquakeSignal
NewmarkSpectrumAnalyzer.)
"""


def compute(acc, dt, zeta=0.05, max_period=5.01, dT=0.01, factor=1.0):
    """Compute the response spectrum of an acceleration record.

    Parameters
    ----------
    acc : np.ndarray
        Ground acceleration in m/s^2.
    dt : float
        Sampling interval in seconds.
    zeta : float, default 0.05
        Damping ratio.
    max_period : float, default 5.01
        Maximum period in seconds.
    dT : float, default 0.01
        Period step in seconds.
    factor : float, default 1.0
        Presentation multiplier applied to the acceleration spectra (PSa, Sa).
        Use ``1/9.81`` to return them in g. PSv (m/s) and Sd (m) are untouched.

    Returns
    -------
    dict
        Keys: T, PSa, PSv, Sd, Sv, Sa, u, v, a, at.
    """
    raise NotImplementedError
