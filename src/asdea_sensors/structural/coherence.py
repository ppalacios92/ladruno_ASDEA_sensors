"""Coherence between two sensors.

The magnitude-squared coherence, 0 to 1, telling how linearly related two
signals are at each frequency. Validates the transfer function: a modal peak
is trustworthy only where the coherence is close to 1.
"""


def compute(acc_a, acc_b, dt, nperseg=1024, noverlap=512, window="hann"):
    """Compute the coherence between two signals.

    Parameters
    ----------
    acc_a, acc_b : np.ndarray
        The two signals in m/s^2.
    dt : float
        Sampling interval in seconds.
    nperseg : int, default 1024
    noverlap : int, default 512
    window : str, default "hann"

    Returns
    -------
    dict
        Keys: f, coherence.
    """
    raise NotImplementedError
