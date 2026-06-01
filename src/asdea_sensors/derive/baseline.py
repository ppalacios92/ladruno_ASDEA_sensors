"""Baseline correction for acceleration.

Removes baseline drift from an acceleration record. The polynomial scheme
integrates to velocity and displacement internally to fit and remove the
drift, then returns the corrected acceleration. (Ported from EarthquakeSignal
BaselineCorrection.)
"""


def baseline_correct(acc, dt, method="polynomial"):
    """Return the baseline-corrected acceleration.

    Parameters
    ----------
    acc : np.ndarray
        Acceleration in m/s^2.
    dt : float
        Sampling interval in seconds.
    method : {"polynomial", "linear", "mean"}, default "polynomial"
        Drift model to remove.

    Returns
    -------
    np.ndarray
        Corrected acceleration in m/s^2.
    """
    raise NotImplementedError
