"""Resample service: change the sampling rate of a signal, a sensor, or the
whole dataset. Useful as a preprocessing step to standardize dt before any
analysis.
"""

from fractions import Fraction

import numpy as np
from scipy.signal import resample_poly


def resample_signal(signal, dt_in, dt_out=None, fs_out=None):
    """Resample one signal array to a target dt or fs.

    Parameters
    ----------
    signal : np.ndarray
        Input samples (1-D).
    dt_in : float
        Current sampling interval in seconds.
    dt_out : float or None
        Target sampling interval in seconds.
    fs_out : float or None
        Target sampling frequency in Hz (alternative to ``dt_out``).

    Returns
    -------
    np.ndarray
        Resampled signal.
    """
    signal = np.asarray(signal)
    dt_target = target_dt(dt=dt_out, fs=fs_out)

    # Nothing to do when the rate already matches.
    if dt_target == dt_in:
        return signal

    # Resampling factor: new rate / old rate = dt_in / dt_target.
    ratio = Fraction(dt_in).limit_denominator(1000000) / \
        Fraction(dt_target).limit_denominator(1000000)
    up = ratio.numerator
    down = ratio.denominator

    # Use the polyphase resampler for sane rational ratios; fall back to a
    # linear interpolation when the factors blow up.
    if up <= 1000 and down <= 1000:
        return resample_poly(signal, up, down)

    n_in = signal.shape[0]
    n_out = int(round(n_in * up / down))
    x_in = np.arange(n_in) * dt_in
    x_out = np.arange(n_out) * dt_target
    return np.interp(x_out, x_in, signal)


def target_dt(dt=None, fs=None):
    """Resolve a target dt from either ``dt`` or ``fs`` (exactly one given)."""
    if (dt is None) == (fs is None):
        raise ValueError("provide exactly one of dt or fs")
    if dt is not None:
        return float(dt)
    return 1.0 / float(fs)
