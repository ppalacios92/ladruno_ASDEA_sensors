"""Konno-Ohmachi spectral smoothing.

Logarithmic-window smoothing of an amplitude spectrum, per window column.
(Ported from AmbientSoilPeriod sua_vent.)
"""


def compute(freqs, magnitude, bexp):
    """Smooth a spectrum with the Konno-Ohmachi window.

    Parameters
    ----------
    freqs : np.ndarray
        Frequency axis. A 1-D vector is broadcast over all window columns.
    magnitude : np.ndarray
        Spectrum magnitude of shape ``(n_freqs, n_windows)``.
    bexp : float
        Bandwidth coefficient (larger = less smoothing).

    Returns
    -------
    np.ndarray
        Smoothed spectrum, same shape as ``magnitude``.
    """
    raise NotImplementedError
