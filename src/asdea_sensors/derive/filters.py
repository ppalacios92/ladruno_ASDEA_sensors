"""Band-pass filters for acceleration.

Two engines: ObsPy (Trace.filter, zero-phase Butterworth) and SciPy
(butter + filtfilt). Both validate the high cut against the Nyquist frequency.
"""


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
    raise NotImplementedError
