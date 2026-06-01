"""Floor/base transfer function (FRF) -> building modal frequencies.

The ratio of floor motion to base motion in the frequency domain. Its peaks
sit at the building's natural (modal) frequencies. Computed with Welch
cross/auto spectra and an H1/H2/Hv estimator.
"""


def compute(acc_num, acc_den, dt, estimator="H1", nperseg=1024, noverlap=512,
            window="hann", smooth="konno", bexp=40, fmax=25.0):
    """Compute the transfer function between two signals.

    Parameters
    ----------
    acc_num : np.ndarray
        Numerator signal (upper floor), m/s^2.
    acc_den : np.ndarray
        Denominator signal (base / lower floor), m/s^2.
    dt : float
        Sampling interval in seconds.
    estimator : {"H1", "H2", "Hv"}, default "H1"
        FRF estimator. H1 assumes noise on the output, H2 on the input,
        Hv is their geometric mean.
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
