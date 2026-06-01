"""Per-window FFT.

FFT of each window (after detrending), returning the frequency axis, the
complex spectrum and its magnitude. The optional band-pass here is off by
default: the signal is expected to be filtered upstream.
(Ported from AmbientSoilPeriod fft_vent.)
"""


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
    raise NotImplementedError
