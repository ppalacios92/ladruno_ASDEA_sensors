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
    import numpy as np

    from .ambient_analysis import AmbientAnalysis

    # Mean smoothed spectrum of each component through the ambient pipeline.
    amb_h1 = AmbientAnalysis(signal_h1, config); amb_h1.average()
    amb_h2 = AmbientAnalysis(signal_h2, config); amb_h2.average()
    amb_v = AmbientAnalysis(signal_v, config); amb_v.average()

    freqs = amb_v.freqs[:, 0]
    s_h1 = amb_h1.mean_spectrum
    s_h2 = amb_h2.mean_spectrum
    s_v = amb_v.mean_spectrum

    if combine == "quadratic":
        s_h = np.sqrt((s_h1 ** 2 + s_h2 ** 2) / 2.0)
    else:
        s_h = np.sqrt(s_h1 * s_h2)

    with np.errstate(divide="ignore", invalid="ignore"):
        HV = np.where(s_v != 0, s_h / s_v, 0.0)

    # Fundamental frequency: the peak of HV over the positive frequencies.
    pos = freqs > 0
    f0 = freqs[pos][np.argmax(HV[pos])] if np.any(pos) else 0.0

    return {"freqs": freqs, "HV": HV, "f0": f0}
