"""Band-pass filters for acceleration.

Two engines: ObsPy (Trace.filter, zero-phase Butterworth) and SciPy
(butter + filtfilt). Both validate the high cut against the Nyquist frequency.
"""

import warnings

import numpy as np


def bandpass(acc, dt, fmin, fmax, engine="obspy", order=4, zerophase=True):
    """Band-pass filter a 1-D signal.

    Parameters
    ----------
    acc : np.ndarray
        Input signal.
    dt : float
        Sampling interval in seconds.
    fmin, fmax : float
        Band edges in Hz. ``fmax`` is clipped below Nyquist if needed.
    engine : {"obspy", "scipy"}, default "obspy"
    order : int, default 4
        Filter order / corners.
    zerophase : bool, default True
        Zero-phase (forward-backward) filtering.

    Returns
    -------
    np.ndarray
        Filtered signal.
    """
    acc = np.asarray(acc, dtype=float)

    nyquist = 0.5 / dt
    if fmax >= nyquist:
        clipped = 0.99 * nyquist
        warnings.warn(
            "High cut %.2f Hz exceeds Nyquist (%.2f Hz); clipped to %.2f Hz"
            % (fmax, nyquist, clipped)
        )
        fmax = clipped

    if engine == "obspy":
        from obspy import Trace

        tr = Trace(data=acc.copy())
        tr.stats.delta = dt
        tr.filter(
            "bandpass",
            freqmin=fmin,
            freqmax=fmax,
            corners=order,
            zerophase=zerophase,
        )
        return tr.data

    if engine == "scipy":
        from scipy.signal import butter, filtfilt, lfilter

        wn = [fmin / nyquist, fmax / nyquist]
        b, a = butter(order, wn, btype="band")
        if zerophase:
            return filtfilt(b, a, acc)
        return lfilter(b, a, acc)

    raise ValueError("engine must be 'obspy' or 'scipy'")
