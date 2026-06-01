"""Interstory drift and drift profile over height.

Relative displacement between floors (drift ratio = relative displacement /
story height), the drift profile along the vertical array, and the per-floor
envelopes. Needs the signals integrated to displacement.
"""

import numpy as np


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
    disp_upper = np.asarray(disp_upper, dtype=float)
    disp_lower = np.asarray(disp_lower, dtype=float)
    rel = disp_upper - disp_lower
    max_drift = float(np.max(np.abs(rel))) if rel.size else float("nan")
    max_ratio = max_drift / story_height if story_height else float("nan")
    return {"drift": rel, "max_drift": max_drift, "max_ratio": max_ratio}


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
    floors = list(disps_by_floor.keys())
    heights = list(heights)

    profile = []
    max_ratio = []
    for i in range(1, len(floors)):
        lower = np.asarray(disps_by_floor[floors[i - 1]], dtype=float)
        upper = np.asarray(disps_by_floor[floors[i]], dtype=float)
        story_h = heights[i] - heights[i - 1]
        res = interstory_drift(upper, lower, story_h)
        profile.append(res["drift"])
        max_ratio.append(res["max_ratio"])

    return {
        "heights": heights,
        "max_drift_ratio": np.asarray(max_ratio),
        "profile": profile,
    }


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
    heights = list(heights)

    if quantity == "drift":
        # Per-story drift ratio envelope (one value per story, not per floor).
        prof = drift_profile(disps_by_floor, heights)
        return {"heights": heights, "envelope": prof["max_drift_ratio"]}

    # disp / accel: per-floor maximum absolute value of the signal.
    envelope = []
    for floor in disps_by_floor:
        sig = np.asarray(disps_by_floor[floor], dtype=float)
        envelope.append(float(np.max(np.abs(sig))) if sig.size else float("nan"))
    return {"heights": heights, "envelope": np.asarray(envelope)}
