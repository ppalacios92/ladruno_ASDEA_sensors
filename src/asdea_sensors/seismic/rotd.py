"""RotD response spectra.

Rotates the two horizontal components from 0 to 180 degrees, computes the
pseudo-acceleration spectrum at each angle and takes a percentile (ROTD00,
ROTD50, ROTD100). (Ported from EarthquakeSignal RotDSpectrumAnalyzer.)
"""

import numpy as np

from asdea_sensors.seismic import newmark


def compute(acc_x, acc_y, dt, rotd=50, damping=0.05, angle_step=5,
            max_period=5.01, dT=0.01):
    """Compute a RotD percentile spectrum.

    Parameters
    ----------
    acc_x, acc_y : np.ndarray
        The two horizontal acceleration components in m/s^2.
    dt : float
        Sampling interval in seconds.
    rotd : {0, 50, 100}, default 50
        Percentile to return. The full 0-180 PSa matrix is also returned so
        the caller can cache it and reuse it for other percentiles.
    damping : float, default 0.05
    angle_step : int, default 5
        Rotation step in degrees.
    max_period : float, default 5.01
    dT : float, default 0.01

    Returns
    -------
    dict
        Keys: T, ROTD<rotd>, angle_rotd<rotd>, PSa_matrix,
        PSa_geo_mean, PSa_arith_mean, PSa_SRSS.
    """
    H1 = np.asarray(acc_x, dtype=float)
    H2 = np.asarray(acc_y, dtype=float)

    angles = np.arange(0, 181, angle_step)
    psa_matrix = []

    T = None
    for angle in angles:
        rot = np.cos(np.radians(angle)) * H1 + np.sin(np.radians(angle)) * H2
        result = newmark.compute(rot, dt, damping, max_period=max_period, dT=dT)
        psa_matrix.append(result["PSa"])
        T = result["T"]

    # Shape: (n_periods, n_angles)
    psa_matrix = np.array(psa_matrix).T

    rotd_spectrum = np.percentile(psa_matrix, rotd, axis=1)
    idx = np.argmax(psa_matrix == rotd_spectrum[:, None], axis=1)
    rotd_angle = angles[idx]

    geo_mean = np.sqrt(np.abs(H1 * H2))
    gm_result = newmark.compute(geo_mean, dt, damping, max_period=max_period, dT=dT)

    arith_mean = 0.5 * (H1 + H2)
    am_result = newmark.compute(arith_mean, dt, damping, max_period=max_period, dT=dT)

    srss = np.sqrt(H1 ** 2 + H2 ** 2)
    srss_result = newmark.compute(srss, dt, damping, max_period=max_period, dT=dT)

    return {
        "T": T,
        f"ROTD{rotd}": rotd_spectrum,
        f"angle_rotd{rotd}": rotd_angle,
        "PSa_matrix": psa_matrix,
        "PSa_geo_mean": gm_result["PSa"],
        "PSa_arith_mean": am_result["PSa"],
        "PSa_SRSS": srss_result["PSa"],
    }
