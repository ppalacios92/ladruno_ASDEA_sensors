"""STA/LTA ratio.

Short-term over long-term average of the squared signal, used to flag
transients and to pick quiet windows. (Ported from AmbientSoilPeriod
algorithm_sta_lta.)
"""


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
    raise NotImplementedError
