"""Arias intensity and significant duration.

Computes the (normalized) Arias intensity curve, the significant duration
between two thresholds, the total Arias intensity and the destructiveness
potential. (Ported from EarthquakeSignal AriasIntensityAnalyzer.)
"""


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
    raise NotImplementedError
