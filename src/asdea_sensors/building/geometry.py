"""Geometry helpers for the building layer.

Reads the per-sensor geometry (floor, UTM E/N, elevation, azimuth) and provides
the spatial relations the structural methods need: plan distances, grouping by
floor, ordering by height, and rotation of a sensor's local axes into a common
building frame.

The sensors were installed in a non-standard orientation, so each one has an
``azimuth``; combining sensors (torsion, mode shapes) requires rotating their
horizontal components into a shared frame first.
"""

import numpy as np


def _require(geometry, device, key):
    """Return ``geometry[device][key]`` or raise if it is missing/None."""
    if device not in geometry:
        raise KeyError("device %r not found in geometry" % device)
    value = geometry[device].get(key)
    if value is None:
        raise ValueError(
            "geometry for device %r has no %r set (it is None); "
            "fill config.SENSOR_GEOMETRY first" % (device, key)
        )
    return value


def plan_distance(geometry, device_a, device_b):
    """Horizontal (plan) distance between two sensors from their UTM E/N.

    Parameters
    ----------
    geometry : dict
        ``config.SENSOR_GEOMETRY``.
    device_a, device_b : str
        Device ids.

    Returns
    -------
    float
        Distance in metres in the E-N plane.
    """
    d_e, d_n = plan_vector(geometry, device_a, device_b)
    return float(np.hypot(d_e, d_n))


def plan_vector(geometry, device_a, device_b):
    """Return the ``(dE, dN)`` plan vector from ``device_a`` to ``device_b``."""
    e_a = _require(geometry, device_a, "E")
    n_a = _require(geometry, device_a, "N")
    e_b = _require(geometry, device_b, "E")
    n_b = _require(geometry, device_b, "N")
    return (float(e_b - e_a), float(n_b - n_a))


def sensors_by_floor(geometry):
    """Group device ids by floor: ``{floor: [device, ...]}``."""
    groups = {}
    for device, info in geometry.items():
        floor = info.get("floor")
        groups.setdefault(floor, []).append(device)
    return groups


def order_by_height(geometry, devices=None):
    """Return device ids ordered by elevation (low to high)."""
    if devices is None:
        devices = list(geometry.keys())
    return sorted(devices, key=lambda d: _require(geometry, d, "elev"))


def heights(geometry, devices=None):
    """Return the elevation of each device, ordered by height."""
    ordered = order_by_height(geometry, devices)
    return [float(_require(geometry, d, "elev")) for d in ordered]


def rotate_to_common(acc_x, acc_y, azimuth):
    """Rotate a sensor's horizontal components into the common building frame.

    Parameters
    ----------
    acc_x, acc_y : np.ndarray
        Horizontal components in the sensor's local frame.
    azimuth : float
        Sensor azimuth in degrees relative to the common frame.

    Returns
    -------
    tuple
        ``(acc_x_common, acc_y_common)``.
    """
    acc_x = np.asarray(acc_x, dtype=float)
    acc_y = np.asarray(acc_y, dtype=float)
    a = np.radians(azimuth)
    c = np.cos(a)
    s = np.sin(a)
    acc_x_common = acc_x * c - acc_y * s
    acc_y_common = acc_x * s + acc_y * c
    return (acc_x_common, acc_y_common)
