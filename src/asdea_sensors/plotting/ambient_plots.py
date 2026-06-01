"""Plots for the ambient analysis (STA/LTA, windows, taper, spectrum)."""

from . import _panels


def _finish(fig, save, default_name):
    """Show the figure or save it under a format/path."""
    import matplotlib.pyplot as plt

    if save is None:
        plt.show()
        return None
    if save.lower() in ("png", "svg", "pdf", "jpg", "jpeg"):
        fname = "{}.{}".format(default_name, save.lower())
    else:
        fname = save
    fig.savefig(fname, bbox_inches="tight")
    plt.close(fig)
    return fname


def plot_sta_lta(result, figsize=None, xlim=None, ylim=None, save=None):
    """Signal, STA, LTA and STA/LTA ratio (AmbientSoilPeriod style).

    Pass one device result from ``ds.ambient(...)`` (e.g. ``amb["MOF00135"]``).
    Four stacked panels: the signal, the short-term average, the long-term
    average, and the STA/LTA ratio with the ``vmin``/``vmax`` band (red dashed)
    and a vertical gridline every ``vent`` seconds.
    """
    import numpy as np
    import matplotlib.pyplot as plt

    sig = np.asarray(result["signal"])
    sta = np.asarray(result["sta"])
    lta = np.asarray(result["lta"])
    ratio = np.asarray(result["sta_lta_ratio"])
    fs = result.get("fs")
    vmin, vmax, vent = result.get("vmin"), result.get("vmax"), result.get("vent")
    t = np.arange(sig.size) / fs if fs else np.arange(sig.size)

    fig, axes = plt.subplots(4, 1, sharex=True, figsize=figsize or (10, 9))
    panels = [(sig, "Signal", "Signal"),
              (sta, "STA", "Short-Term Average (STA)"),
              (lta, "LTA", "Long-Term Average (LTA)")]
    for ax, (y, ylab, title) in zip(axes[:3], panels):
        ax.plot(t[:y.size], y, color="C0")
        ax.set_ylabel(ylab, fontweight="bold")
        ax.set_title(title, fontsize=11, fontweight="bold")

    axr = axes[3]
    axr.plot(t[:ratio.size], ratio, color="C0", label="STA/LTA")
    if vmin is not None:
        axr.axhline(vmin, color="red", ls="--", label="vmin = %g" % vmin)
    if vmax is not None:
        axr.axhline(vmax, color="red", ls="--", label="vmax = %g" % vmax)
    if fs and vent:
        for i in range(1, int(np.max(t) // vent) + 1):
            axr.axvline(i * vent, color="gray", ls=":", lw=0.5)
    axr.set_ylabel("STA / LTA", fontweight="bold")
    axr.set_title("STA / LTA Ratio", fontsize=11, fontweight="bold")
    axr.legend(fontsize=8)
    if ylim is not None:
        axr.set_ylim(ylim)

    for ax in axes:
        ax.grid(True, alpha=0.5)
        if xlim is not None:
            ax.set_xlim(xlim)
    axes[-1].set_xlabel("Time [s]", fontweight="bold")
    fig.tight_layout()
    return _finish(fig, save, "ambient_sta_lta")


def plot_windows(analysis, figsize=None, xlim=None, ylim=None, save=None):
    """Plot the signal with the selected windows highlighted.

    ``figsize`` overrides the default figure size; ``xlim``/``ylim`` set the
    axis limits when not None.
    """
    import numpy as np
    import matplotlib.pyplot as plt

    signal = np.asarray(analysis.signal)
    config = analysis.config or {}
    fs = config.get("Fs")
    if fs:
        x = np.arange(signal.size) / fs
        xlabel = "Time [s]"
    else:
        x = np.arange(signal.size)
        xlabel = "Sample"

    fig, ax = plt.subplots(figsize=figsize or (10, 4.5))
    ax.plot(x, signal, lw=0.6, color="0.5", label="signal")

    windows_pos = getattr(analysis, "windows_pos", None)
    first = True
    if windows_pos is not None:
        for pos in np.atleast_2d(windows_pos):
            i0, i1 = int(pos[0]), int(pos[-1])
            xa = x[i0] if i0 < x.size else x[-1]
            xb = x[i1] if i1 < x.size else x[-1]
            ax.axvspan(xa, xb, color="C0", alpha=0.25,
                       label="selected window" if first else None)
            first = False

    ax.set_xlabel(xlabel)
    ax.set_ylabel("Acceleration [m/s^2]")
    ax.set_title("Selected ambient windows", fontweight="bold")
    ax.grid(True, alpha=0.3)
    ax.legend()
    if xlim is not None:
        ax.set_xlim(xlim)
    if ylim is not None:
        ax.set_ylim(ylim)
    fig.tight_layout()

    return _finish(fig, save, "ambient_windows")


def plot_spectrum(result, peak_spacing_hz=0.2, num_peaks=4, min_freq=0.0,
                  figsize=None, xlim=None, ylim=None, save=None):
    """All-window spectra (gray) + mean (steelblue) + peaks (AmbientSoilPeriod style).

    Pass one device result from ``ds.ambient(...)`` (e.g. ``amb["MOF00135"]``).
    Log-frequency axis; every window spectrum is drawn light gray, the mean in
    steelblue, and the ``num_peaks`` strongest peaks of the mean are marked with
    their frequency and period.

    Parameters
    ----------
    result : dict
        One device result from ``ds.ambient(...)``.
    peak_spacing_hz : float, default 0.2
        Minimum spacing between detected peaks.
    num_peaks : int, default 4
        Strongest peaks to mark.
    min_freq : float, default 0.0
        Ignore peaks below this frequency.
    figsize, xlim, ylim, save
        Plot controls.

    Returns
    -------
    list of dict
        The detected peaks ``[{"freq", "period", "amplitude"}, ...]``.
    """
    import numpy as np
    import matplotlib.pyplot as plt
    from scipy.signal import find_peaks

    freqs = np.asarray(result["freqs"])
    f = freqs[:, 0] if freqs.ndim == 2 else freqs
    windows = result.get("per_window_smoothed")
    if windows is None:
        windows = result.get("per_window_spectra")
    windows = np.asarray(windows)
    mean = np.asarray(result["mean_spectrum"])
    df = f[1] - f[0]
    min_dist = max(1, int(peak_spacing_hz / df))

    fig, ax = plt.subplots(figsize=figsize or (10, 4))
    if windows.ndim == 2:
        for k in range(windows.shape[1]):
            ax.semilogx(f, windows[:, k], color="lightgray", alpha=0.4)
    elif windows.size:
        ax.semilogx(f, windows, color="lightgray", alpha=0.4)
    ax.semilogx(f, mean, color="steelblue", lw=2, label="Average Spectrum")

    peaks, _ = find_peaks(mean, distance=min_dist)
    peaks = [p for p in peaks if f[p] >= min_freq]
    top = sorted(peaks, key=lambda i: mean[i], reverse=True)[:num_peaks]
    pastel = ["mediumaquamarine", "lightcoral", "cornflowerblue", "plum"]
    found = []
    for i, idx in enumerate(top):
        fi, amp = f[idx], mean[idx]
        Ti = 1.0 / fi if fi else 0.0
        ax.plot(fi, amp, "o", color=pastel[i % len(pastel)], markersize=6,
                label="Peak %d: f = %.2f Hz / T = %.2f s" % (i + 1, fi, Ti))
        found.append({"freq": fi, "period": Ti, "amplitude": amp})

    ax.grid(True, which="both", ls="--", alpha=0.5)
    ax.set_xlabel("Frequency [Hz]", fontweight="bold")
    ax.set_ylabel("Amplitude", fontweight="bold")
    ax.set_title("Spectrum and Average (All Windows)", fontweight="bold")
    if xlim is not None:
        ax.set_xlim(xlim)
    if ylim is not None:
        ax.set_ylim(ylim)
    ax.legend(loc="upper left", fontsize=9)
    fig.tight_layout()
    _finish(fig, save, "ambient_spectrum")

    print("Peaks")
    for p in found:
        print("  f = %.3f Hz   T = %.3f s   A = %.4g"
              % (p["freq"], p["period"], p["amplitude"]))
    return found


def plot_mean_spectrum_all(means, dataset=None, component="x", layout="auto",
                           group=None, figsize=None, xlim=(0, 25), ylim=None,
                           save=None):
    """Plot precomputed ambient mean spectra (no compute here); layout from shape.

    One series per sensor (the mean spectrum), so::

        means = ds.ambient_mean(config, component="x")
        plot_mean_spectrum_all(ds, means)                 # sensors overlaid
        plot_mean_spectrum_all(ds, means, layout="grid")  # one panel per sensor
        plot_mean_spectrum_all(ds, ds.MOF00135.ambient_mean(config))   # one sensor

    Parameters
    ----------
    dataset : SensorDataset
        Source object (device order, colors, titles).
    means : dict or result
        ``ds.ambient_mean(config, component)`` ->
        ``{device: {"freqs", "spectrum", "f_dom"}}``, or a single result.
    component : {"x", "y", "z"}, default "x"
        Label only (which component the means were computed for).
    layout : {"auto", "grid", "overlay"}, default "auto"
    group : bool or None
        Back-compat alias (``True`` -> overlay, ``False`` -> grid).
    figsize, xlim, ylim, save
        Plot controls (xlim defaults to 0-25 Hz).

    Returns
    -------
    dict or float
        ``{device: dominant_frequency_Hz}`` (multi-sensor) or the single f_dom.
    """
    means, dataset = _panels.resolve(means, dataset)
    _panels.draw_analysis(
        means, dataset=dataset,
        curve=lambda r: (r["freqs"], r["spectrum"]),
        layout=layout, group=group, yscale="linear",
        xlabel="Frequency [Hz]", ylabel_unit="m/s^2 . s",
        title_word="Mean amplitude", name="ambient_mean_all",
        figsize=figsize, xlim=xlim, ylim=ylim, save=save)

    if _panels._shape(means) in ("device_flat", "device_comp"):
        order = (list(dataset.devices) if dataset is not None else list(means))
        return {d: means[d]["f_dom"] for d in order if d in means}
    if isinstance(means, dict) and "f_dom" in means:
        return means["f_dom"]
    return None


def _ambient_devices(dataset, results):
    """Devices present in an ``ds.ambient(...)`` broadcast result, or None."""
    if _panels._shape(results) in ("device_flat", "device_comp"):
        if dataset is not None:
            return [d for d in dataset.devices if d in results]
        return list(results)
    return None


def plot_sta_lta_all(results, dataset=None, layout="auto", group=None,
                     figsize=None, xlim=None, ylim=None, save=None):
    """Plot the STA/LTA ratio with the vmin/vmax acceptance band (object-driven).

    Feed the result of ``ds.ambient(...)``::

        amb = ds.ambient(sta=1.0, lta=30.0, vent=20.0, vmin=0.2, vmax=2.5)
        plot_sta_lta_all(ds, amb)                 # grid: one panel per sensor
        plot_sta_lta_all(ds, amb, layout="overlay")   # ratios overlaid
        plot_sta_lta_all(ds, ds.MOF00135.ambient())   # one sensor

    layout ``auto`` -> grid (a time series per sensor); ``overlay`` puts every
    ratio on one axes.
    """
    import numpy as np
    import matplotlib.pyplot as plt

    results, dataset = _panels.resolve(results, dataset)
    layout = _panels._layout_from_group(layout, group)
    colors = getattr(dataset, "device_colors", {}) or {}
    titles = getattr(dataset, "titles", {}) or {}

    def draw_one(ax, res, color, band=True, label=None):
        r = np.asarray(res["sta_lta_ratio"])
        fs = res.get("fs")
        x = np.arange(r.size) / fs if fs else np.arange(r.size)
        ax.plot(x, r, lw=0.8, color=color, label=label)
        vmin, vmax = res.get("vmin"), res.get("vmax")
        if band and vmin is not None and vmax is not None:
            ax.axhline(vmin, color="C3", ls="--", lw=1.0)
            ax.axhline(vmax, color="C3", ls="--", lw=1.0)
            ax.axhspan(vmin, vmax, color="C2", alpha=0.1)
        ax.grid(True, alpha=0.3)
        if xlim is not None:
            ax.set_xlim(xlim)
        if ylim is not None:
            ax.set_ylim(ylim)

    devices = _ambient_devices(dataset, results)

    if devices is None:                                    # single sensor
        fig, ax = plt.subplots(figsize=figsize or (10, 4.5))
        draw_one(ax, results, "C0")
        ax.set_xlabel("Time [s]")
        ax.set_ylabel("STA/LTA ratio [-]")
        fig.tight_layout()
        return _panels._finish(fig, save, "sta_lta_all")

    if layout == "overlay":
        fig, ax = plt.subplots(figsize=figsize or (11, 5))
        for j, d in enumerate(devices):
            draw_one(ax, results[d], colors.get(d, "C%d" % (j % 10)),
                     band=(j == 0), label=d)
        ax.set_xlabel("Time [s]")
        ax.set_ylabel("STA/LTA ratio [-]")
        ax.legend(fontsize=8)
        fig.tight_layout()
        return _panels._finish(fig, save, "sta_lta_all")

    n = len(devices)
    fig, axes = plt.subplots(n, 1, sharex=True,
                             figsize=figsize or (10, 2.2 * n), squeeze=False)
    for i, d in enumerate(devices):
        ax = axes[i][0]
        draw_one(ax, results[d], colors.get(d, "C%d" % (i % 10)))
        ax.set_ylabel("%s\nSTA/LTA" % d)
    axes[-1][0].set_xlabel("Time [s]")
    axes[0][0].set_title("STA/LTA ratio - %d sensors" % n, fontweight="bold")
    fig.tight_layout()
    return _panels._finish(fig, save, "sta_lta_all")


def plot_windows_all(results, dataset=None, layout="auto", group=None,
                     figsize=None, xlim=None, ylim=None, save=None):
    """Plot the signal with the selected ambient windows shaded (object-driven).

    Feed the result of ``ds.ambient(...)``::

        amb = ds.ambient(sta=1.0, lta=30.0, vent=20.0, vmin=0.2, vmax=2.5)
        plot_windows_all(ds, amb)                 # grid: one panel per sensor
        plot_windows_all(ds, ds.MOF00135.ambient())   # one sensor

    The windows that passed the STA/LTA band are shaded over each sensor signal.
    """
    import numpy as np
    import matplotlib.pyplot as plt

    results, dataset = _panels.resolve(results, dataset)
    layout = _panels._layout_from_group(layout, group)
    colors = getattr(dataset, "device_colors", {}) or {}

    def draw_one(ax, res, color):
        sig = np.asarray(res["signal"])
        fs = res.get("fs")
        vent = res.get("vent")
        x = np.arange(sig.size) / fs if fs else np.arange(sig.size)
        ax.plot(x, sig, lw=0.5, color="black")
        pos = res.get("windows_pos")
        pos = np.atleast_1d(pos) if pos is not None else np.array([])
        nwin = int(fs * vent) if (fs and vent) else None
        if nwin and pos.size:
            # One distinct color per window (rainbow), as in AmbientSoilPeriod.
            cmap = plt.cm.hsv(np.linspace(0, 1, pos.size))
            for i, a in enumerate(pos):
                a = int(a)
                x0 = a / fs
                x1 = min(a + nwin, sig.size - 1) / fs
                ax.axvspan(x0, x1, facecolor=cmap[i], alpha=0.35,
                           edgecolor=cmap[i], lw=0.3)
        ax.grid(True, alpha=0.3)
        if xlim is not None:
            ax.set_xlim(xlim)
        if ylim is not None:
            ax.set_ylim(ylim)

    devices = _ambient_devices(dataset, results)

    if devices is None:                                    # single sensor
        fig, ax = plt.subplots(figsize=figsize or (10, 4.5))
        draw_one(ax, results, "0.4")
        ax.set_xlabel("Time [s]")
        ax.set_ylabel("Acceleration [m/s^2]")
        fig.tight_layout()
        return _panels._finish(fig, save, "ambient_windows_all")

    n = len(devices)
    fig, axes = plt.subplots(n, 1, sharex=True,
                             figsize=figsize or (10, 2.2 * n), squeeze=False)
    for i, d in enumerate(devices):
        ax = axes[i][0]
        draw_one(ax, results[d], colors.get(d, "C%d" % (i % 10)))
        ax.set_ylabel("%s\n[m/s^2]" % d)
    axes[-1][0].set_xlabel("Time [s]")
    axes[0][0].set_title("Selected ambient windows - %d sensors" % n,
                         fontweight="bold")
    fig.tight_layout()
    return _panels._finish(fig, save, "ambient_windows_all")


def plot_spectrum_all(results, dataset=None, peak_spacing_hz=0.2, num_peaks=4,
                      min_freq=0.0, figsize=None, xlim=None, ylim=None,
                      save=None):
    """Per-sensor ambient spectra: all windows (gray) + mean (color) + peaks.

    Like :func:`plot_spectrum` but for every sensor at once: one panel per
    sensor (log frequency), each with every window spectrum in light gray, the
    mean in the sensor color, and the strongest peaks marked. Feed the broadcast
    result of ``ds.ambient(...)``.

    Returns ``{device: [{"freq", "period", "amplitude"}, ...]}``.
    """
    import numpy as np
    import matplotlib.pyplot as plt
    from scipy.signal import find_peaks

    results, dataset = _panels.resolve(results, dataset)
    devices = ([d for d in dataset.devices if d in results]
               if dataset is not None else list(results))
    colors = getattr(dataset, "device_colors", {}) or {}
    pastel = ["mediumaquamarine", "lightcoral", "cornflowerblue", "plum"]
    n = len(devices)
    fig, axes = plt.subplots(n, 1, figsize=figsize or (10, 2.7 * n),
                             squeeze=False)
    out = {}
    for i, d in enumerate(devices):
        ax = axes[i][0]
        r = results[d]
        f = np.asarray(r["freqs"])
        win = r.get("per_window_smoothed")
        if win is None:
            win = r.get("per_window_spectra")
        win = np.asarray(win)
        mean = np.asarray(r["mean_spectrum"])
        if win.ndim == 2:
            for k in range(win.shape[1]):
                ax.semilogx(f, win[:, k], color="lightgray", alpha=0.4)
        elif win.size:
            ax.semilogx(f, win, color="lightgray", alpha=0.4)
        ax.semilogx(f, mean, color=colors.get(d, "C%d" % (i % 10)), lw=2,
                    label="%s mean" % d)
        df = f[1] - f[0]
        pk, _ = find_peaks(mean, distance=max(1, int(peak_spacing_hz / df)))
        pk = [p for p in pk if f[p] >= min_freq]
        top = sorted(pk, key=lambda j: mean[j], reverse=True)[:num_peaks]
        peaks = []
        for j, idx in enumerate(top):
            fi, amp = f[idx], mean[idx]
            Ti = 1.0 / fi if fi else 0.0
            ax.plot(fi, amp, "o", color=pastel[j % len(pastel)], markersize=6,
                    label="f = %.2f Hz / T = %.2f s" % (fi, Ti))
            peaks.append({"freq": fi, "period": Ti, "amplitude": amp})
        ax.set_ylabel("%s\nAmplitude" % d)
        ax.grid(True, which="both", ls="--", alpha=0.5)
        ax.legend(fontsize=7, loc="upper left")
        if xlim is not None:
            ax.set_xlim(xlim)
        if ylim is not None:
            ax.set_ylim(ylim)
        out[d] = peaks
    axes[-1][0].set_xlabel("Frequency [Hz]", fontweight="bold")
    axes[0][0].set_title("Ambient spectra (all windows + mean) - %d sensors" % n,
                         fontweight="bold")
    fig.tight_layout()
    _panels._finish(fig, save, "ambient_spectrum_all")
    return out
