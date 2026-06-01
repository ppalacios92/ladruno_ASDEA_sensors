"""Short-time Fourier transform (spectrogram).

Shows how the frequency content of a long record evolves in time, useful for
monitoring building behaviour over hours.
"""


def compute(acc, dt, nperseg=256, noverlap=224, window="hann", fmax=25.0):
    """Compute the spectrogram of an acceleration record.

    Parameters
    ----------
    acc : np.ndarray
        Acceleration in m/s^2.
    dt : float
        Sampling interval in seconds.
    nperseg : int, default 256
    noverlap : int, default 224
    window : str, default "hann"
    fmax : float, default 25.0
        Upper frequency kept for display.

    Returns
    -------
    dict
        Keys: f, t, Zxx.
    """
    raise NotImplementedError
