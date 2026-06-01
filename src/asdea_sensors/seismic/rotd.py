"""RotD response spectra.

Rotates the two horizontal components from 0 to 180 degrees, computes the
pseudo-acceleration spectrum at each angle and takes a percentile (ROTD00,
ROTD50, ROTD100). (Ported from EarthquakeSignal RotDSpectrumAnalyzer.)
"""


def compute(acc_x, acc_y, dt, rotd=50, damping=0.05, angle_step=5,
            max_period=5.01, dT=0.01):
    """Compute a RotD percentile spectrum.

    Parameters
    ----------
    acc_x, acc_y : np.ndarray
        The two horizontal acceleration components in m/s^2.
    dt : float
        Sampling interval in seconds.
    rotd : {0, 50, 100}, default 50
        Percentile to return. The full 0-180 PSa matrix is also returned so
        the caller can cache it and reuse it for other percentiles.
    damping : float, default 0.05
    angle_step : int, default 5
        Rotation step in degrees.
    max_period : float, default 5.01
    dT : float, default 0.01

    Returns
    -------
    dict
        Keys: T, ROTD<rotd>, angle_rotd<rotd>, PSa_matrix,
        PSa_geo_mean, PSa_arith_mean, PSa_SRSS.
    """
    raise NotImplementedError
