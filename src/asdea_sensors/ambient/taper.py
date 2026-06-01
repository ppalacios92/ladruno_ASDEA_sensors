"""Tukey taper for windowed signals. (Ported from AmbientSoilPeriod taper_function.)"""


def compute(windows, p):
    """Apply a Tukey taper to each window (column).

    Parameters
    ----------
    windows : np.ndarray
        Window matrix of shape ``(n_samples, n_windows)``.
    p : float
        Tukey alpha (fraction of the window that is tapered).

    Returns
    -------
    tuple
        ``(tapered_windows, taper)``.
    """
    raise NotImplementedError
