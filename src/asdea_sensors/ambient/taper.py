"""Tukey taper for windowed signals. (Ported from AmbientSoilPeriod taper_function.)"""

import numpy as np
from scipy.signal.windows import tukey


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
    m, _ = windows.shape
    taper = tukey(m, alpha=p)
    tapered_windows = windows * taper[:, np.newaxis]
    return tapered_windows, taper
