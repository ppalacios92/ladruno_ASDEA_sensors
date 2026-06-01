"""Coherence between sensors.

A single pair plus a matrix across every pair of sensors, to validate the
modal peaks and detect noisy or faulty channels.
"""

import itertools

import numpy as np
from scipy import signal as sp_signal


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
    acc_a = np.asarray(acc_a, dtype=float)
    acc_b = np.asarray(acc_b, dtype=float)
    f, cxy = sp_signal.coherence(acc_a, acc_b, fs=1.0 / dt, window=window,
                                 nperseg=nperseg, noverlap=noverlap)
    return {"f": f, "coherence": cxy}


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
    devices = list(signals.keys())
    f = None
    pairs = {}
    for a, b in itertools.combinations(devices, 2):
        res = compute(signals[a], signals[b], dt, **kwargs)
        if f is None:
            f = res["f"]
        pairs[(a, b)] = res["coherence"]
    return {"f": f, "pairs": pairs}
