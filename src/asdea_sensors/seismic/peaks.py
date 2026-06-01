"""Peak ground values: PGA, PGV, PGD.

Peaks of the absolute acceleration, velocity and displacement. Velocity and
displacement come from the derived signal, so the signal must be integrated
first.
"""


def compute(acc, vel, disp):
    """Return the peak ground values of one component.

    Parameters
    ----------
    acc : np.ndarray
        Acceleration in m/s^2.
    vel : np.ndarray
        Velocity in m/s.
    disp : np.ndarray
        Displacement in m.

    Returns
    -------
    dict
        Keys: PGA, PGV, PGD.
    """
    raise NotImplementedError
