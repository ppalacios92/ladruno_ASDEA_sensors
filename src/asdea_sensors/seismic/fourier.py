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
    import numpy as np
    from scipy.signal import find_peaks

    acc = np.asarray(acc, dtype=float)
    n = len(acc)
    fs = 1.0 / dt

    # One-sided FFT power spectrum.
    freqs = fs * np.arange(0, n // 2) / n
    y = np.fft.fft(acc)
    spectrum = np.abs(y[:n // 2]) ** 2 / n

    # Optional Konno-Ohmachi smoothing before peak picking.
    if smooth == "konno":
        from asdea_sensors.ambient import konno_ohmachi
        magnitude_2d = spectrum.reshape(-1, 1)
        spectrum = konno_ohmachi.compute(freqs, magnitude_2d, bexp).reshape(-1)

    # Identify spectral peaks with minimum prominence and spacing.
    distance = max(1, int(len(spectrum) * distance_frac))
    peaks, _ = find_peaks(spectrum, prominence=prominence, distance=distance)
    peak_amplitudes = spectrum[peaks]
    peak_freqs = freqs[peaks]

    # Sort by amplitude and keep the top num_frequencies peaks.
    sorted_indices = np.argsort(peak_amplitudes)[::-1]
    top_indices = sorted_indices[:num_frequencies]

    dom_freqs = peak_freqs[top_indices]
    dom_peaks = peak_amplitudes[top_indices]
    dom_periods = np.divide(
        1.0, dom_freqs,
        out=np.full_like(dom_freqs, np.inf, dtype=float),
        where=dom_freqs != 0,
    )

    return {
        "freqs": freqs,
        "spectrum": spectrum,
        "dom_freqs": dom_freqs,
        "dom_periods": dom_periods,
        "dom_peaks": dom_peaks,
    }
