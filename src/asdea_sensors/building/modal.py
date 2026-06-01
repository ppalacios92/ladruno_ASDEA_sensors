"""Modal characterization: frequencies, mode shapes, damping and tracking.

Operational modal analysis (OMA) from the vertical array of sensors: the
amplitude and phase of each floor at a modal frequency give the mode shape;
the bandwidth around the peak gives the damping. Modal tracking follows the
frequencies in time for monitoring.
"""

import numpy as np
from scipy import signal as sp_signal

from . import geometry as geom


def _fft_magnitude(sig, dt):
    """One-sided FFT magnitude and its frequency axis."""
    sig = np.asarray(sig, dtype=float)
    n = sig.size
    mag = np.abs(np.fft.rfft(sig))
    f = np.fft.rfftfreq(n, d=dt)
    return f, mag


def _maybe_smooth(f, mag, smooth, bexp):
    """Optional Konno-Ohmachi smoothing of a 1-D magnitude spectrum."""
    if smooth == "konno":
        from asdea_sensors.ambient import konno_ohmachi
        mag2d = np.asarray(mag, dtype=float).reshape(-1, 1)
        return konno_ohmachi.compute(np.asarray(f, dtype=float), mag2d, bexp)[:, 0]
    return np.asarray(mag, dtype=float)


def _pick_modes(f, mag, fband, n_modes):
    """Pick up to ``n_modes`` strongest spectral peaks inside ``fband``."""
    lo, hi = fband
    band = (f >= lo) & (f <= hi)
    f_band = f[band]
    mag_band = mag[band]
    if f_band.size == 0:
        return np.array([])
    peaks, _ = sp_signal.find_peaks(mag_band)
    if peaks.size == 0:
        return np.array([])
    order = np.argsort(mag_band[peaks])[::-1]
    chosen = peaks[order[:n_modes]]
    freqs = np.sort(f_band[chosen])
    return freqs


def modal_frequencies(signals, dt, fband=(0.5, 10.0), n_modes=3, smooth="konno",
                      bexp=40):
    """Identify the modal frequencies shared by the sensors.

    Parameters
    ----------
    signals : dict
        ``{device: signal}`` across the floors.
    dt : float
        Sampling interval in seconds.
    fband : (float, float), default (0.5, 10.0)
        Frequency band to search.
    n_modes : int, default 3
        Number of modes to identify.
    smooth : {None, "konno"}, default "konno"
    bexp : int, default 40

    Returns
    -------
    dict
        Keys: freqs (the identified modal frequencies).
    """
    f = None
    acc = None
    for sig in signals.values():
        fi, mag = _fft_magnitude(sig, dt)
        mag = _maybe_smooth(fi, mag, smooth, bexp)
        if acc is None:
            f = fi
            acc = mag
        else:
            # All signals share dt; align lengths defensively.
            m = min(acc.size, mag.size)
            acc = acc[:m] + mag[:m]
            f = f[:m]
    if acc is None:
        return {"freqs": np.array([])}
    acc = acc / len(signals)
    freqs = _pick_modes(f, acc, fband, n_modes)
    return {"freqs": freqs}


def mode_shapes(signals, geometry, dt, modal_freqs=None, component="x",
                fband=(0.5, 10.0), n_modes=3):
    """Mode shapes: amplitude and phase per floor at each modal frequency.

    Parameters
    ----------
    signals : dict
        ``{device: signal}`` across the floors.
    geometry : dict
        ``config.SENSOR_GEOMETRY`` (used to order by height).
    dt : float
        Sampling interval in seconds.
    modal_freqs : sequence or None
        Frequencies to evaluate the shapes at. ``None`` finds them first.
    component : {"x", "y"}, default "x"
    fband : (float, float), default (0.5, 10.0)
    n_modes : int, default 3

    Returns
    -------
    dict
        Keys: freqs, heights, shapes (amplitude per floor), phases.
    """
    devices = geom.order_by_height(geometry, list(signals.keys()))
    floor_heights = geom.heights(geometry, devices)

    if modal_freqs is None:
        modal_freqs = modal_frequencies(signals, dt, fband=fband,
                                        n_modes=n_modes)["freqs"]
    modal_freqs = np.atleast_1d(np.asarray(modal_freqs, dtype=float))

    # FFT of every device on a shared frequency axis.
    spectra = {}
    f = None
    for dev in devices:
        fi, full = _fft_full(signals[dev], dt)
        if f is None:
            f = fi
        spectra[dev] = full

    ref = devices[0]
    shapes = np.zeros((modal_freqs.size, len(devices)))
    phases = np.zeros((modal_freqs.size, len(devices)))

    for i, fm in enumerate(modal_freqs):
        k = int(np.argmin(np.abs(f - fm)))
        ref_val = spectra[ref][k]
        for j, dev in enumerate(devices):
            val = spectra[dev][k]
            # Cross-spectrum vs the reference: amplitude and relative phase.
            cross = val * np.conj(ref_val)
            shapes[i, j] = np.abs(val)
            phases[i, j] = np.angle(cross)

    return {
        "freqs": modal_freqs,
        "heights": floor_heights,
        "shapes": shapes,
        "phases": phases,
    }


def _fft_full(sig, dt):
    """Complex one-sided FFT and its frequency axis."""
    sig = np.asarray(sig, dtype=float)
    n = sig.size
    spec = np.fft.rfft(sig)
    f = np.fft.rfftfreq(n, d=dt)
    return f, spec


def damping(signal, dt, modal_freq, method="half_power", band=0.1):
    """Modal damping ratio at a given frequency.

    Parameters
    ----------
    signal : np.ndarray
        Single-component signal in m/s^2.
    dt : float
        Sampling interval in seconds.
    modal_freq : float
        Frequency of the mode in Hz.
    method : {"half_power", "random_decrement"}, default "half_power"
    band : float, default 0.1
        Half-width (fraction) of the band around the peak for the fit.

    Returns
    -------
    dict
        Keys: zeta (damping ratio), modal_freq.
    """
    signal = np.asarray(signal, dtype=float)

    if method == "half_power":
        f, mag = _fft_magnitude(signal, dt)
        # Power spectrum, restricted to a window around the modal frequency.
        lo = modal_freq * (1.0 - 5.0 * band)
        hi = modal_freq * (1.0 + 5.0 * band)
        sel = (f >= max(lo, 0.0)) & (f <= hi)
        f_w = f[sel]
        p_w = mag[sel] ** 2
        if f_w.size < 3:
            return {"zeta": float("nan"), "modal_freq": modal_freq}

        k = int(np.argmax(p_w))
        f0 = f_w[k]
        peak = p_w[k]
        half = peak / 2.0  # -3 dB in power.

        # Lower half-power frequency.
        f1 = f_w[0]
        for i in range(k, 0, -1):
            if p_w[i] <= half:
                f1 = np.interp(half, [p_w[i], p_w[i + 1]], [f_w[i], f_w[i + 1]])
                break
        # Upper half-power frequency.
        f2 = f_w[-1]
        for i in range(k, f_w.size - 1):
            if p_w[i + 1] <= half:
                f2 = np.interp(half, [p_w[i + 1], p_w[i]], [f_w[i + 1], f_w[i]])
                break

        zeta = (f2 - f1) / (2.0 * f0) if f0 > 0 else float("nan")
        return {"zeta": float(zeta), "modal_freq": float(f0)}

    if method == "random_decrement":
        # Band-pass around the mode, then fit the decay of the envelope.
        fs = 1.0 / dt
        lo = modal_freq * (1.0 - band)
        hi = modal_freq * (1.0 + band)
        nyq = fs / 2.0
        wn = [max(lo, 1e-6) / nyq, min(hi, nyq * 0.999) / nyq]
        b, a = sp_signal.butter(4, wn, btype="band")
        filtered = sp_signal.filtfilt(b, a, signal)

        env = np.abs(sp_signal.hilbert(filtered))
        t = np.arange(env.size) * dt
        good = env > (env.max() * 1e-3)
        if good.sum() < 2:
            return {"zeta": float("nan"), "modal_freq": modal_freq}
        # Slope of log-envelope = -zeta * 2*pi*f0.
        slope = np.polyfit(t[good], np.log(env[good]), 1)[0]
        zeta = -slope / (2.0 * np.pi * modal_freq) if modal_freq > 0 else float("nan")
        return {"zeta": float(zeta), "modal_freq": float(modal_freq)}

    raise ValueError("unknown method %r" % method)


def tracking(signal, dt, window="10min", overlap=0.5, fband=(1.0, 8.0),
             n_modes=2, smooth="konno", bexp=40):
    """Track modal frequencies over time with a moving window.

    Parameters
    ----------
    signal : np.ndarray
        Single-component signal in m/s^2.
    dt : float
        Sampling interval in seconds.
    window : str or float, default "10min"
        Moving window length.
    overlap : float, default 0.5
    fband : (float, float), default (1.0, 8.0)
    n_modes : int, default 2
    smooth : {None, "konno"}, default "konno"
    bexp : int, default 40

    Returns
    -------
    dict
        Keys: t, freqs (shape ``(n_windows, n_modes)``).
    """
    from asdea_sensors.core.window_service import parse_duration

    signal = np.asarray(signal, dtype=float)
    win_sec = parse_duration(window)
    win_n = int(round(win_sec / dt))
    if win_n < 2:
        win_n = min(signal.size, 2)
    step = max(int(round(win_n * (1.0 - overlap))), 1)

    t_list = []
    freq_list = []
    start = 0
    while start + win_n <= signal.size:
        seg = signal[start:start + win_n]
        f, mag = _fft_magnitude(seg, dt)
        mag = _maybe_smooth(f, mag, smooth, bexp)
        freqs = _pick_modes(f, mag, fband, n_modes)
        # Pad / trim to a fixed length so the result is rectangular.
        row = np.full(n_modes, np.nan)
        row[:freqs.size] = freqs[:n_modes]
        freq_list.append(row)
        t_list.append((start + win_n / 2.0) * dt)
        start += step

    return {
        "t": np.asarray(t_list),
        "freqs": np.asarray(freq_list),
    }
