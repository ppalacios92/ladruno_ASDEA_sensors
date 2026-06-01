"""Newmark response spectrum (linear acceleration / beta method).

Solves a single-degree-of-freedom system for a range of periods and returns
the spectral quantities plus the time histories. (Ported from EarthquakeSignal
NewmarkSpectrumAnalyzer.)
"""

import numpy as np
from numba import njit


@njit
def solve_newmark(ag, dt, zeta, Tj):
    """Solve a SDOF system for one period with the beta-Newmark method.

    ag is the ground acceleration in m/s^2. Returns the peak spectral
    quantities and the relative/absolute time histories.
    """
    gama = 1 / 2
    beta = 1 / 4
    w = 2 * np.pi / Tj
    m = 1.0
    k = m * w ** 2
    c = 2 * m * w * zeta
    a1 = m / (beta * dt ** 2) + c * gama / (beta * dt)
    a2 = m / (beta * dt) + c * (gama / beta - 1)
    a3 = m * (1 / (2 * beta) - 1) + c * dt * (gama / (2 * beta) - 1)
    kp = k + a1

    u = np.zeros(len(ag))
    v = np.zeros(len(ag))
    a = np.zeros(len(ag))
    at = np.zeros(len(ag))

    for i in range(len(ag) - 1):
        p_eff = -m * ag[i] + a1 * u[i] + a2 * v[i] + a3 * a[i]
        u[i + 1] = p_eff / kp
        a[i + 1] = (u[i + 1] - u[i]) / (beta * dt ** 2) - v[i] / (beta * dt) - a[i] * (1 / (2 * beta) - 1)
        at[i + 1] = a[i + 1] + ag[i]
        v[i + 1] = v[i] + dt * ((1 - gama) * a[i] + gama * a[i + 1])

    Sd = np.max(np.abs(u))
    Sv = np.max(np.abs(v))
    Sa = np.max(np.abs(at))
    PSv = w * Sd
    PSa = w ** 2 * Sd

    return Sd, Sv, Sa, PSv, PSa, u, v, a, at


def compute(acc, dt, zeta=0.05, max_period=5.01, dT=0.01, factor=1.0):
    """Compute the response spectrum of an acceleration record.

    Parameters
    ----------
    acc : np.ndarray
        Ground acceleration in m/s^2.
    dt : float
        Sampling interval in seconds.
    zeta : float, default 0.05
        Damping ratio.
    max_period : float, default 5.01
        Maximum period in seconds.
    dT : float, default 0.01
        Period step in seconds.
    factor : float, default 1.0
        Presentation multiplier applied to the acceleration spectra (PSa, Sa).
        Use ``1/9.81`` to return them in g. PSv (m/s) and Sd (m) are untouched.

    Returns
    -------
    dict
        Keys: T, PSa, PSv, Sd, Sv, Sa, u, v, a, at.
    """
    T = np.arange(0.0, max_period, dT)
    # acc is already in SI (m/s^2); no g-to-SI conversion needed.
    ag = np.asarray(acc, dtype=float)

    Sd, Sv, Sa, PSv, PSa = [], [], [], [], []
    u_hist, v_hist, a_hist, at_hist = [], [], [], []

    # Minimum stability bound for the linear acceleration scheme.
    gama = 1 / 2
    beta = 1 / 4
    q = dt * np.pi * np.sqrt(2) * np.sqrt(gama - 2 * beta)

    for Tj in T:
        if Tj > q:
            Sd_, Sv_, Sa_, PSv_, PSa_, u, v, a, at = solve_newmark(ag, dt, zeta, Tj)
            Sd.append(Sd_)
            Sv.append(Sv_)
            Sa.append(Sa_)
            PSv.append(PSv_)
            PSa.append(PSa_)

            if np.isclose(Tj, 1.0, atol=0.01):
                u_hist = u
                v_hist = v
                a_hist = a
                at_hist = at
        else:
            PGA = np.max(np.abs(ag))
            Sd.append(0)
            Sv.append(0)
            Sa.append(PGA)
            PSv.append(0)
            PSa.append(PGA)

    Sd = np.array(Sd)
    Sv = np.array(Sv)
    Sa = np.array(Sa) * factor
    PSv = np.array(PSv)
    PSa = np.array(PSa) * factor

    return {
        'T': T,
        'PSa': PSa,
        'PSv': PSv,
        'Sd': Sd,
        'Sv': Sv,
        'Sa': Sa,
        'u': np.array(u_hist),
        'v': np.array(v_hist),
        'a': np.array(a_hist),
        'at': np.array(at_hist),
    }
