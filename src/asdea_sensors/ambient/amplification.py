"""Spectral amplification between sensors / floors.

Ratio of spectra between a reference sensor and the others. The ratio basis is
explicit: Fourier amplitude spectrum (smoothed), response spectrum (PSa), or
HVSR.
"""


def compute(ref_signal, other_signals, dt, basis="fourier", config=None):
    """Compute the spectral amplification of each sensor against a reference.

    Parameters
    ----------
    ref_signal : np.ndarray
        Reference signal (single component) in m/s^2.
    other_signals : dict
        ``{device: signal}`` for the sensors to compare against the reference.
    dt : float
        Sampling interval in seconds.
    basis : {"fourier", "response", "hvsr"}, default "fourier"
        "fourier" divides smoothed Fourier amplitude spectra, "response"
        divides Newmark PSa spectra, "hvsr" uses the H/V ratio.
    config : dict or None
        Ambient configuration used by the "fourier" and "hvsr" bases.

    Returns
    -------
    dict
        Keys: freqs, ratios (a dict keyed by device), basis.
    """
    raise NotImplementedError
