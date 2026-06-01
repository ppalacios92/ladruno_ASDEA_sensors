"""Horizontal-to-Vertical Spectral Ratio (Nakamura).

Ratio of the (combined) horizontal spectrum to the vertical spectrum of the
same sensor. Its peak gives the fundamental frequency f0.
"""


def compute(signal_h1, signal_h2, signal_v, config, combine="geometric"):
    """Compute the HVSR of one sensor.

    Parameters
    ----------
    signal_h1, signal_h2 : np.ndarray
        The two horizontal components.
    signal_v : np.ndarray
        The vertical component.
    config : dict
        Ambient configuration (windowing, smoothing, FFT band).
    combine : {"geometric", "quadratic"}, default "geometric"
        How to combine the two horizontals.

    Returns
    -------
    dict
        Keys: freqs, HV, f0.
    """
    raise NotImplementedError
