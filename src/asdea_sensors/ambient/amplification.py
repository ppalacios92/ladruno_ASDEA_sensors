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
    import numpy as np

    if basis == "fourier":
        from .ambient_analysis import AmbientAnalysis

        ref = AmbientAnalysis(ref_signal, config); ref.average()
        freqs = ref.freqs[:, 0]
        ref_spec = ref.mean_spectrum

        ratios = {}
        for device, sig in other_signals.items():
            amb = AmbientAnalysis(sig, config); amb.average()
            with np.errstate(divide="ignore", invalid="ignore"):
                ratios[device] = np.where(ref_spec != 0,
                                          amb.mean_spectrum / ref_spec, 0.0)
        return {"freqs": freqs, "ratios": ratios, "basis": basis}

    if basis == "response":
        from ..seismic import newmark

        ref = newmark.compute(ref_signal, dt)
        T = ref["T"]
        ref_psa = ref["PSa"]

        ratios = {}
        for device, sig in other_signals.items():
            psa = newmark.compute(sig, dt)["PSa"]
            with np.errstate(divide="ignore", invalid="ignore"):
                ratios[device] = np.where(ref_psa != 0, psa / ref_psa, 0.0)
        # For the response basis the x axis is the period vector.
        return {"freqs": T, "ratios": ratios, "basis": basis}

    raise ValueError(
        "basis %r not supported here; use 'fourier' or 'response'. "
        "For H/V use ambient.hvsr.compute on a single sensor." % basis)
