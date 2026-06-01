"""Konno-Ohmachi spectral smoothing.

Logarithmic-window smoothing of an amplitude spectrum, per window column.
(Ported from AmbientSoilPeriod sua_vent.)
"""

import numpy as np
from numba import njit


@njit
def _kernel(freqs, magnitude, bexp):
    mm, nn = magnitude.shape
    smoothed = np.zeros_like(magnitude)

    for j in range(nn):
        y = magnitude[:, j]
        f = freqs[:, j]

        nx = len(f)
        dx = f[1] - f[0]
        fratio = 10 ** (2.5 / bexp)

        for ix in range(nx):
            fc = f[ix]
            if fc <= 0:
                continue

            ix1 = max(int(fc / fratio / dx), 1)
            ix2 = min(int(fc * fratio / dx + 1), nx - 1)

            a1 = 0.0
            a2 = 0.0

            for jx in range(ix1, ix2 + 1):
                if jx != ix and f[jx] > 0:
                    log_ratio = np.log10(f[jx] / fc)
                    d = log_ratio * bexp
                    if d != 0.0:
                        s = np.sin(d)
                        c = (s / d) ** 4
                    else:
                        c = 1.0
                else:
                    c = 1.0
                a1 += c * y[jx]
                a2 += c

            smoothed[ix, j] = a1 / a2 if a2 != 0 else 0.0

    return smoothed


def compute(freqs, magnitude, bexp):
    """Smooth a spectrum with the Konno-Ohmachi window.

    Parameters
    ----------
    freqs : np.ndarray
        Frequency axis. A 1-D vector is broadcast over all window columns.
    magnitude : np.ndarray
        Spectrum magnitude of shape ``(n_freqs, n_windows)``.
    bexp : float
        Bandwidth coefficient (larger = less smoothing).

    Returns
    -------
    np.ndarray
        Smoothed spectrum, same shape as ``magnitude``.
    """
    if freqs.ndim == 1:
        freqs = np.tile(freqs[:, None], magnitude.shape[1])
    return _kernel(freqs, magnitude, bexp)
