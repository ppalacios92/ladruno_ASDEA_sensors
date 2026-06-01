"""Baseline correction for acceleration.

Removes baseline drift from an acceleration record. The polynomial scheme
integrates to velocity and displacement internally to fit and remove the
drift, then returns the corrected acceleration. (Ported from EarthquakeSignal
BaselineCorrection.)
"""

import numpy as np


def baseline_correct(acc, dt, method="polynomial"):
    """Return the baseline-corrected acceleration.

    Parameters
    ----------
    acc : np.ndarray
        Acceleration in m/s^2.
    dt : float
        Sampling interval in seconds.
    method : {"polynomial", "linear", "mean"}, default "polynomial"
        Drift model to remove.

    Returns
    -------
    np.ndarray
        Corrected acceleration in m/s^2.
    """
    acc = np.asarray(acc, dtype=float)

    if method == "mean":
        return acc - acc.mean()

    if method == "linear":
        # Remove a best-fit straight line from the acceleration.
        n = len(acc)
        time = np.arange(n) * dt
        slope, intercept = np.polyfit(time, acc, 1)
        return acc - (intercept + slope * time)

    if method != "polynomial":
        raise ValueError("method must be 'polynomial', 'linear' or 'mean'")

    # Polynomial scheme: integrate to velocity and displacement, fit the
    # quadratic drift in acceleration and subtract it. The acceleration is
    # already in m/s^2 (SI), so no g conversion is applied.
    n = len(acc)
    time = np.arange(n) * dt

    # Step 1: velocity by trapezoidal integration.
    vel = np.zeros(n)
    for i in range(1, n):
        vel[i] = vel[i - 1] + (acc[i - 1] + acc[i]) * dt / 2

    # Step 2: displacement integration.
    disp = np.zeros(n)
    for i in range(1, n):
        disp[i] = disp[i - 1] + vel[i - 1] * dt + (2 * acc[i - 1] + acc[i]) * dt ** 2 / 6

    # Step 3: polynomial drift moment coefficients A1, A2, A3.
    A1i = np.zeros(n - 1)
    A2i = np.zeros(n - 1)
    A3i = np.zeros(n - 1)
    for i in range(n - 1):
        ti, ti1 = time[i], time[i + 1]
        vi = vel[i]
        ai, ai1 = acc[i], acc[i + 1]
        dti = ti1 - ti

        A1i[i] = 0.5 * vi * dti * (ti + ti1) + (1 / 24) * dti ** 2 * (
            ai * (3 * ti + 5 * ti1) + ai1 * (ti + 3 * ti1))
        A2i[i] = (1 / 3) * vi * dti * (ti ** 2 + ti * ti1 + ti1 ** 2) + (1 / 60) * dti ** 2 * (
            ai * (4 * ti ** 2 + 7 * ti * ti1 + 9 * ti1 ** 2) +
            ai1 * (ti ** 2 + 3 * ti * ti1 + 6 * ti1 ** 2))
        A3i[i] = (1 / 4) * vi * dti * (ti ** 3 + ti ** 2 * ti1 + ti * ti1 ** 2 + ti1 ** 3) + (1 / 120) * dti ** 2 * (
            ai * (5 * ti ** 3 + 9 * ti ** 2 * ti1 + 12 * ti * ti1 ** 2 + 14 * ti1 ** 3) +
            ai1 * (ti ** 3 + 3 * ti ** 2 * ti1 + 6 * ti * ti1 ** 2 + 10 * ti1 ** 3))

    A1, A2, A3 = np.sum(A1i), np.sum(A2i), np.sum(A3i)
    tT = time[-1]

    # Step 4: polynomial coefficients.
    C0 = (300 * A1 / tT ** 3) - (900 * A2 / tT ** 4) + (630 * A3 / tT ** 5)
    C1 = (-900 * A1 / tT ** 4) + (2880 * A2 / tT ** 5) - (2100 * A3 / tT ** 6)
    C2 = (630 * A1 / tT ** 5) - (2100 * A2 / tT ** 6) + (1575 * A3 / tT ** 7)

    # Step 5: subtract the drift from the acceleration.
    return acc - (C0 + 2 * C1 * time + 3 * C2 * time ** 2)
