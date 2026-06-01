"""Geometry helpers for the building layer.

Reads the per-sensor geometry (floor, UTM E/N, elevation, azimuth) and provides
the spatial relations the structural methods need: plan distances, grouping by
floor, ordering by height, and rotation of a sensor's local axes into a common
building frame.

The sensors were installed in a non-standard orientation, so each one has an
``azimuth``; combining sensors (torsion, mode shapes) requires rotating their
horizontal components into a shared frame first.
"""


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
    raise NotImplementedError


def plan_vector(geometry, device_a, device_b):
    """Return the ``(dE, dN)`` plan vector from ``device_a`` to ``device_b``."""
    raise NotImplementedError


def sensors_by_floor(geometry):
    """Group device ids by floor: ``{floor: [device, ...]}``."""
    raise NotImplementedError


def order_by_height(geometry, devices=None):
    """Return device ids ordered by elevation (low to high)."""
    raise NotImplementedError


def heights(geometry, devices=None):
    """Return the elevation of each device, ordered by height."""
    raise NotImplementedError


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
    raise NotImplementedError
