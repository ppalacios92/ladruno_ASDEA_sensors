"""Coherence between sensors.

A single pair plus a matrix across every pair of sensors, to validate the
modal peaks and detect noisy or faulty channels.
"""


def compute(acc_a, acc_b, dt, nperseg=1024, noverlap=512, window="hann"):
    """Magnitude-squared coherence between two signals.

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


def matrix(signals, dt, **kwargs):
    """Coherence for every pair of sensors.

    Parameters
    ----------
    signals : dict
        ``{device: signal}``.
    dt : float
        Sampling interval in seconds.
    **kwargs
        Forwarded to :func:`compute`.

    Returns
    -------
    dict
        Keys: f, pairs (``{(device_a, device_b): coherence}``).
    """
    raise NotImplementedError
