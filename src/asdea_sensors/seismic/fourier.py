"""Fourier amplitude spectrum and dominant frequencies.

One-sided FFT spectrum plus the most prominent peaks (frequency, period,
amplitude). Optional Konno-Ohmachi smoothing before peak picking.
(Ported from EarthquakeSignal FourierAnalyzer.)
"""


def compute(acc, dt, num_frequencies=4, prominence=1e-6, distance_frac=0.02,
            smooth=None, bexp=40):
    """Compute the spectrum and extract the dominant frequencies.

    Parameters
    ----------
    acc : np.ndarray
        Acceleration in m/s^2.
    dt : float
        Sampling interval in seconds.
    num_frequencies : int, default 4
        Number of dominant peaks to return.
    prominence : float, default 1e-6
        Minimum peak prominence.
    distance_frac : float, default 0.02
        Minimum peak spacing as a fraction of the spectrum length.
    smooth : {None, "konno"}, default None
        Optional Konno-Ohmachi smoothing.
    bexp : int, default 40
        Smoothing bandwidth when ``smooth="konno"``.

    Returns
    -------
    dict
        Keys: freqs, spectrum, dom_freqs, dom_periods, dom_peaks.
    """
    raise NotImplementedError
