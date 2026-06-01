"""Torsion of a floor from two (or more) sensors on the same level.

For a rigid diaphragm a plan point (x, y) moves as
    u_x = U_x - (y - y_c) * theta
    u_y = U_y + (x - x_c) * theta
so the floor rotation ``theta(t)`` follows from the difference of the same
horizontal component at two sensors separated in plan. With three horizontal
channels the full ``(U_x, U_y, theta)`` can be solved.
"""


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
    raise NotImplementedError


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
    raise NotImplementedError


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
    raise NotImplementedError


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
    raise NotImplementedError
