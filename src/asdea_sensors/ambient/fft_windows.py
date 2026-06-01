"""Per-window FFT.

FFT of each window (after detrending), returning the frequency axis, the
complex spectrum and its magnitude. The optional band-pass here is off by
default: the signal is expected to be filtered upstream.
(Ported from AmbientSoilPeriod fft_vent.)
"""

import numpy as np
from scipy.signal import butter, filtfilt, detrend


def compute(fs, windows, apply_filter=False, f1=0.1, f2=25.0):
    """Compute the FFT of each window.

    Parameters
    ----------
    fs : float
        Sampling frequency in Hz.
    windows : np.ndarray
        Window matrix of shape ``(n_samples, n_windows)``.
    apply_filter : bool, default False
        Apply a band-pass before the FFT. Off by default (filter upstream).
    f1, f2 : float, default 0.1, 25.0
        Band edges used only when ``apply_filter=True``.

    Returns
    -------
    tuple
        ``(freqs, complex_spectrum, magnitude)`` matrices.
    """
    n_samples, n_windows = windows.shape
    nfft = n_samples
    freq_axis = np.fft.fftfreq(nfft, d=1 / fs)[:nfft // 2]

    freqs = np.tile(freq_axis[:, None], (1, n_windows))
    complex_spectrum = np.zeros((nfft // 2, n_windows), dtype=np.complex64)
    magnitude = np.zeros((nfft // 2, n_windows), dtype=np.float64)

    if apply_filter:
        wn = [f1 / (fs / 2), f2 / (fs / 2)]
        b, a = butter(4, wn, btype='band')

    for j in range(n_windows):
        amp = windows[:, j].copy()
        amp = detrend(amp)
        if apply_filter:
            amp = filtfilt(b, a, amp)
        amp = amp - np.mean(amp)
        spectrum = np.fft.fft(amp, n=nfft)[:nfft // 2]
        complex_spectrum[:, j] = spectrum
        magnitude[:, j] = np.abs(spectrum)

    return freqs, complex_spectrum, magnitude
