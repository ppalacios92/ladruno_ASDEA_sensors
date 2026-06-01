"""Power spectral density (Welch) and energy per frequency band."""


def compute(acc, dt, nperseg=256, noverlap=128, window="hann",
            bands=None, detrend="constant"):
    """Compute the PSD and the energy in each frequency band.

    Parameters
    ----------
    acc : np.ndarray
        Acceleration in m/s^2.
    dt : float
        Sampling interval in seconds.
    nperseg : int, default 256
    noverlap : int, default 128
    window : str, default "hann"
    bands : list of (float, float) or None
        Frequency bands for the band-energy summary. ``None`` uses the default
        bands in ``config.settings.PSD``.
    detrend : str, default "constant"

    Returns
    -------
    dict
        Keys: f, Pxx, band_energy (a dict keyed by band).
    """
    raise NotImplementedError
