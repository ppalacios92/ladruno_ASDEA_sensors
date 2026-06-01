"""STA/LTA ratio.

Short-term over long-term average of the squared signal, used to flag
transients and to pick quiet windows. (Ported from AmbientSoilPeriod
algorithm_sta_lta.)
"""

import numpy as np


def compute(signal, fs, sta, lta):
    """Compute the STA/LTA ratio.

    Parameters
    ----------
    signal : np.ndarray
        Input signal (1-D).
    fs : float
        Sampling frequency in Hz.
    sta : float
        Short-term window length in seconds.
    lta : float
        Long-term window length in seconds.

    Returns
    -------
    tuple
        ``(sta_lta, sta_vals, lta_vals)`` arrays.
    """
    n = len(signal)
    n_sta = int(fs * sta)
    n_lta = int(fs * lta)

    # Edge padding using the mean of the first two samples (as in the original).
    edge_val = abs((signal[0] + signal[1]) / 2.0)
    signal2 = signal ** 2

    padded_sta = np.concatenate((np.full(n_sta, edge_val), signal2))
    padded_lta = np.concatenate((np.full(n_lta, edge_val), signal2))

    cumsum_sta = np.cumsum(padded_sta)
    cumsum_lta = np.cumsum(padded_lta)

    sta_vals = (cumsum_sta[n_sta:n_sta + n] - cumsum_sta[0:n]) / n_sta
    lta_vals = (cumsum_lta[n_lta:n_lta + n] - cumsum_lta[0:n]) / n_lta

    with np.errstate(divide='ignore', invalid='ignore'):
        sta_lta = np.where(lta_vals != 0, sta_vals / lta_vals, 0.0)

    return sta_lta, sta_vals, lta_vals
