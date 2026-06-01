"""Transfer functions floor/base -> building modal frequencies.

A single-pair estimate plus a convenience that stacks the FRF of every floor
against the base, using the whole vertical array of sensors.
"""

import numpy as np
from scipy import signal as sp_signal


def _smooth_magnitude(f, mag, smooth, bexp):
    """Optional Konno-Ohmachi smoothing of a 1-D magnitude spectrum."""
    if smooth == "konno":
        from asdea_sensors.ambient import konno_ohmachi
        mag2d = np.asarray(mag, dtype=float).reshape(-1, 1)
        smoothed = konno_ohmachi.compute(np.asarray(f, dtype=float), mag2d, bexp)
        return smoothed[:, 0]
    return np.asarray(mag, dtype=float)


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
    acc_num = np.asarray(acc_num, dtype=float)
    acc_den = np.asarray(acc_den, dtype=float)
    fs = 1.0 / dt

    common = dict(fs=fs, window=window, nperseg=nperseg, noverlap=noverlap)
    f, sxx = sp_signal.welch(acc_den, **common)
    _, syy = sp_signal.welch(acc_num, **common)
    # csd(x, y) gives Sxy; here x = denominator (input), y = numerator (output).
    _, sxy = sp_signal.csd(acc_den, acc_num, **common)

    if estimator == "H1":
        h = sxy / sxx
    elif estimator == "H2":
        # Syy / Syx, with Syx the conjugate of Sxy.
        h = syy / np.conj(sxy)
    elif estimator == "Hv":
        h1 = sxy / sxx
        h2 = syy / np.conj(sxy)
        h = np.sqrt(h1 * h2)
    else:
        raise ValueError("unknown estimator %r" % estimator)

    keep = f <= fmax
    f = f[keep]
    h = h[keep]

    mag = np.abs(h)
    mag_s = _smooth_magnitude(f, mag, smooth, bexp)

    peaks, _ = sp_signal.find_peaks(mag_s)
    modal_freqs = f[peaks]
    modal_amps = mag_s[peaks]

    return {
        "f": f,
        "H": h,
        "modal_freqs": modal_freqs,
        "modal_amps": modal_amps,
    }


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
    results = {}
    for key, sig in signals_by_floor.items():
        results[key] = compute(sig, base_signal, dt, **kwargs)
    return results
