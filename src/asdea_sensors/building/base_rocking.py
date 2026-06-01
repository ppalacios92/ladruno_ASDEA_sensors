"""Base rocking: rotation of the foundation.

Estimates the rocking of the base from the base sensor (and, when available,
the difference between base sensors), to assess soil-foundation flexibility.
"""

import numpy as np


def compute(acc_vertical, dt, base_width=None, acc_vertical_b=None):
    """Estimate the base rocking.

    Parameters
    ----------
    acc_vertical : np.ndarray
        Vertical acceleration at the base, m/s^2.
    dt : float
        Sampling interval in seconds.
    base_width : float or None
        Plan distance between the two base points (when two are available),
        to turn a vertical difference into a rocking angle.
    acc_vertical_b : np.ndarray or None
        Vertical acceleration at a second base point.

    Returns
    -------
    dict
        Keys: rocking (time history), spectrum, rocking_freq.
    """
    acc_vertical = np.asarray(acc_vertical, dtype=float)

    if acc_vertical_b is not None and base_width:
        # Two verticals: rocking angle from their difference over the width.
        acc_vertical_b = np.asarray(acc_vertical_b, dtype=float)
        n = min(acc_vertical.size, acc_vertical_b.size)
        rocking = (acc_vertical[:n] - acc_vertical_b[:n]) / base_width
    else:
        # Single sensor: keep the (low-frequency) vertical content as a proxy.
        rocking = acc_vertical

    n = rocking.size
    spectrum = np.abs(np.fft.rfft(rocking))
    freqs = np.fft.rfftfreq(n, d=dt)

    if spectrum.size > 1:
        k = int(np.argmax(spectrum[1:])) + 1
        rocking_freq = float(freqs[k])
    else:
        rocking_freq = float("nan")

    return {
        "rocking": rocking,
        "spectrum": spectrum,
        "rocking_freq": rocking_freq,
    }
