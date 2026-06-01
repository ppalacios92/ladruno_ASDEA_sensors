"""Modal frequency tracking over time (structural health monitoring).

Slides a moving window over a long record, picks the spectral peak(s) in a
frequency band per window, and follows the modal frequency in time. A
sustained drop signals a loss of stiffness.
"""


def compute(acc, dt, window="10min", overlap=0.5, fband=(1.0, 8.0),
            n_modes=2, smooth="konno", bexp=40):
    """Track modal frequencies over a record.

    Parameters
    ----------
    acc : np.ndarray
        Acceleration in m/s^2.
    dt : float
        Sampling interval in seconds.
    window : str or float, default "10min"
        Moving window length.
    overlap : float, default 0.5
        Fractional overlap between windows.
    fband : (float, float), default (1.0, 8.0)
        Frequency band to search the modes in.
    n_modes : int, default 2
        Number of modes (peaks) to follow.
    smooth : {None, "konno"}, default "konno"
    bexp : int, default 40

    Returns
    -------
    dict
        Keys: t, freqs (shape ``(n_windows, n_modes)``).
    """
    raise NotImplementedError
