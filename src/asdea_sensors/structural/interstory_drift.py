"""Interstory drift between two floors.

Relative horizontal displacement between an upper and a lower floor, divided
by the story height to get the drift ratio. Needs both signals integrated to
displacement.
"""


def compute(disp_upper, disp_lower, dt, story_height=3.0):
    """Compute the interstory drift between two floors.

    Parameters
    ----------
    disp_upper, disp_lower : np.ndarray
        Displacement of the upper and lower floor, in m.
    dt : float
        Sampling interval in seconds.
    story_height : float, default 3.0
        Story height in m, used for the drift ratio.

    Returns
    -------
    dict
        Keys: time, drift, max_drift, max_ratio.
    """
    raise NotImplementedError
