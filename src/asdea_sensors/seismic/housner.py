"""Housner spectral intensity (SI).

Area under the pseudo-velocity spectrum (PSv) between two periods, typically
0.1 to 2.5 s, the range relevant to buildings. Summarizes how severe a record
is for structures.
"""

import numpy as np

from asdea_sensors.seismic import newmark


def compute(acc, dt, T1=0.1, T2=2.5, zeta=0.05):
    """Compute the Housner spectral intensity.

    Parameters
    ----------
    acc : np.ndarray
        Acceleration in m/s^2.
    dt : float
        Sampling interval in seconds.
    T1, T2 : float, default 0.1, 2.5
        Integration period bounds in seconds.
    zeta : float, default 0.05
        Damping ratio used for the PSv spectrum.

    Returns
    -------
    dict
        Keys: SI.
    """
    # Make sure the spectrum reaches at least T2.
    max_period = max(5.01, T2 + 0.01)
    result = newmark.compute(acc, dt, zeta=zeta, max_period=max_period)
    T = result["T"]
    PSv = result["PSv"]

    # Integrate PSv over the [T1, T2] period band by the trapezoidal rule.
    mask = (T >= T1) & (T <= T2)
    SI = np.trapz(PSv[mask], T[mask])

    return {"SI": SI}
