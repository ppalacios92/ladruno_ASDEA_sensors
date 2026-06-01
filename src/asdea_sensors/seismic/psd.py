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
    import numpy as np
    from scipy.signal import welch

    from asdea_sensors.config import settings

    acc = np.asarray(acc, dtype=float)
    fs = 1.0 / dt

    f, Pxx = welch(acc, fs=fs, nperseg=nperseg, noverlap=noverlap,
                   window=window, detrend=detrend)

    if bands is None:
        bands = settings.PSD["FREQ_BANDS"]

    # Integrate the PSD over each band to get the band energy.
    band_energy = {}
    for low, high in bands:
        mask = (f >= low) & (f <= high)
        band_energy[(low, high)] = float(np.trapz(Pxx[mask], f[mask]))

    return {"f": f, "Pxx": Pxx, "band_energy": band_energy}
