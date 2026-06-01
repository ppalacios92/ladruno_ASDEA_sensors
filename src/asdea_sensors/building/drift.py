"""Interstory drift and drift profile over height.

Relative displacement between floors (drift ratio = relative displacement /
story height), the drift profile along the vertical array, and the per-floor
envelopes. Needs the signals integrated to displacement.
"""


def interstory_drift(disp_upper, disp_lower, story_height=3.0):
    """Interstory drift between two floors.

    Parameters
    ----------
    disp_upper, disp_lower : np.ndarray
        Displacement of the upper and lower floor, in m.
    story_height : float, default 3.0
        Story height in m, for the drift ratio.

    Returns
    -------
    dict
        Keys: drift (time history), max_drift, max_ratio.
    """
    raise NotImplementedError


def drift_profile(disps_by_floor, heights):
    """Drift profile along the height of the building.

    Parameters
    ----------
    disps_by_floor : dict
        ``{floor: displacement}`` ordered by height (low to high).
    heights : sequence of float
        Elevation of each floor, in m.

    Returns
    -------
    dict
        Keys: heights, max_drift_ratio (per story), profile.
    """
    raise NotImplementedError


def story_envelope(disps_by_floor, heights, quantity="drift"):
    """Per-floor envelope of a quantity over the record.

    Parameters
    ----------
    disps_by_floor : dict
        ``{floor: signal}``.
    heights : sequence of float
    quantity : {"drift", "disp", "accel"}, default "drift"

    Returns
    -------
    dict
        Keys: heights, envelope (max per floor).
    """
    raise NotImplementedError
