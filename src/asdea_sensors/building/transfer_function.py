"""Transfer functions floor/base -> building modal frequencies.

A single-pair estimate plus a convenience that stacks the FRF of every floor
against the base, using the whole vertical array of sensors.
"""


def compute(acc_num, acc_den, dt, estimator="H1", nperseg=1024, noverlap=512,
            window="hann", smooth="konno", bexp=40, fmax=25.0):
    """Transfer function between two signals (numerator / denominator).

    Parameters
    ----------
    acc_num : np.ndarray
        Numerator signal (upper floor), m/s^2.
    acc_den : np.ndarray
        Denominator signal (base / lower floor), m/s^2.
    dt : float
        Sampling interval in seconds.
    estimator : {"H1", "H2", "Hv"}, default "H1"
        FRF estimator. H1 = Sxy/Sxx, H2 = Syy/Syx, Hv = sqrt(H1*H2).
    nperseg : int, default 1024
    noverlap : int, default 512
    window : str, default "hann"
    smooth : {None, "konno"}, default "konno"
    bexp : int, default 40
    fmax : float, default 25.0
        Upper frequency kept.

    Returns
    -------
    dict
        Keys: f, H, modal_freqs, modal_amps.
    """
    raise NotImplementedError


def stack(signals_by_floor, base_signal, dt, **kwargs):
    """FRF of every floor against the base (the whole vertical array).

    Parameters
    ----------
    signals_by_floor : dict
        ``{floor_or_device: signal}`` for the floors above the base.
    base_signal : np.ndarray
        Base (denominator) signal.
    dt : float
        Sampling interval in seconds.
    **kwargs
        Forwarded to :func:`compute` (estimator, nperseg, smooth, fmax, ...).

    Returns
    -------
    dict
        ``{floor_or_device: compute(...) result}``.
    """
    raise NotImplementedError
