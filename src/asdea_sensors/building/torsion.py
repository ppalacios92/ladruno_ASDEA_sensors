"""Torsion of a floor from two (or more) sensors on the same level.

For a rigid diaphragm a plan point (x, y) moves as
    u_x = U_x - (y - y_c) * theta
    u_y = U_y + (x - x_c) * theta
so the floor rotation ``theta(t)`` follows from the difference of the same
horizontal component at two sensors separated in plan. With three horizontal
channels the full ``(U_x, U_y, theta)`` can be solved.
"""

import numpy as np
from scipy import signal as sp_signal


def floor_rotation(sig_a, sig_b, distance, component="x"):
    """Floor rotation theta(t) from two sensors on the same floor.

    Parameters
    ----------
    sig_a, sig_b : np.ndarray
        The same horizontal component at the two sensors (common frame).
    distance : float
        Plan separation between the sensors, perpendicular to ``component``.
    component : {"x", "y"}, default "x"

    Returns
    -------
    np.ndarray
        Rotation time history theta(t) in radians.
    """
    sig_a = np.asarray(sig_a, dtype=float)
    sig_b = np.asarray(sig_b, dtype=float)
    if distance == 0:
        raise ValueError("distance between sensors must be non-zero")
    return (sig_a - sig_b) / distance


def torsional_spectrum(theta, dt, smooth="konno", bexp=40):
    """Spectrum of the rotation, to read the torsional frequency.

    Parameters
    ----------
    theta : np.ndarray
        Rotation time history.
    dt : float
        Sampling interval in seconds.
    smooth : {None, "konno"}, default "konno"
    bexp : int, default 40

    Returns
    -------
    dict
        Keys: freqs, spectrum, torsional_freq.
    """
    theta = np.asarray(theta, dtype=float)
    n = theta.size
    spectrum = np.abs(np.fft.rfft(theta))
    freqs = np.fft.rfftfreq(n, d=dt)

    if smooth == "konno":
        from asdea_sensors.ambient import konno_ohmachi
        mag2d = spectrum.reshape(-1, 1)
        spectrum = konno_ohmachi.compute(freqs, mag2d, bexp)[:, 0]

    # Skip the DC bin when picking the dominant torsional frequency.
    if spectrum.size > 1:
        k = int(np.argmax(spectrum[1:])) + 1
        torsional_freq = float(freqs[k])
    else:
        torsional_freq = float("nan")

    return {
        "freqs": freqs,
        "spectrum": spectrum,
        "torsional_freq": torsional_freq,
    }


def torsion_ratio(theta, translation, radius):
    """Ratio of torsional displacement (theta * radius) to translation.

    Parameters
    ----------
    theta : np.ndarray
        Rotation time history.
    translation : np.ndarray
        Translation time history of the floor (same component).
    radius : float
        Representative plan radius used to turn rotation into displacement.

    Returns
    -------
    dict
        Keys: ratio (time history), max_ratio.
    """
    theta = np.asarray(theta, dtype=float)
    translation = np.asarray(translation, dtype=float)
    denom = np.where(np.abs(translation) > 0, translation, np.nan)
    ratio = (theta * radius) / denom
    max_ratio = float(np.nanmax(np.abs(ratio))) if ratio.size else float("nan")
    return {"ratio": ratio, "max_ratio": max_ratio}


def orbit(acc_x, acc_y):
    """Plan trajectory of a point (X vs Y), useful to see torsion/coupling.

    Parameters
    ----------
    acc_x, acc_y : np.ndarray
        The two horizontal components of one sensor (common frame). Usually the
        displacement is used; pass the derived signal for a physical orbit.

    Returns
    -------
    dict
        Keys: x, y (the trajectory).
    """
    return {
        "x": np.asarray(acc_x, dtype=float),
        "y": np.asarray(acc_y, dtype=float),
    }
