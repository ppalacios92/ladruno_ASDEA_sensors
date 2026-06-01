"""Average spectrum across windows. (Ported from AmbientSoilPeriod prom_vent.)"""


def compute(spectra):
    """Average a per-window spectrum matrix into a single mean spectrum.

    Parameters
    ----------
    spectra : np.ndarray
        Spectrum matrix of shape ``(n_freqs, n_windows)``.

    Returns
    -------
    np.ndarray
        Mean spectrum of shape ``(n_freqs,)``.
    """
    raise NotImplementedError
