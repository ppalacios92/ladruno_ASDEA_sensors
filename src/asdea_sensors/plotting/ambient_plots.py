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


def plot_sta_lta(analysis, figsize=None, xlim=None, ylim=None, save=None):
    """Plot the STA/LTA ratio with the acceptance band.

    ``figsize`` overrides the default figure size; ``xlim``/``ylim`` set the
    axis limits when not None.
    """
    import numpy as np
    import matplotlib.pyplot as plt

    ratio = np.asarray(analysis.sta_lta_ratio)
    config = analysis.config or {}
    fs = config.get("Fs")
    if fs:
        x = np.arange(ratio.size) / fs
        xlabel = "Time [s]"
    else:
        x = np.arange(ratio.size)
        xlabel = "Sample"

    fig, ax = plt.subplots(figsize=figsize or (10, 4.5))
    ax.plot(x, ratio, lw=0.8, color="C0", label="STA/LTA")

    vmin = config.get("vmin")
    vmax = config.get("vmax")
    if vmin is not None:
        ax.axhline(vmin, color="C3", ls="--", lw=1.0, label="acceptance band")
    if vmax is not None:
        ax.axhline(vmax, color="C3", ls="--", lw=1.0)
    if vmin is not None and vmax is not None:
        ax.axhspan(vmin, vmax, color="C2", alpha=0.1)

    ax.set_xlabel(xlabel)
    ax.set_ylabel("STA/LTA ratio [-]")
    ax.set_title("STA/LTA ratio", fontweight="bold")
    ax.grid(True, alpha=0.3)
    ax.legend()
    if xlim is not None:
        ax.set_xlim(xlim)
    if ylim is not None:
        ax.set_ylim(ylim)
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


def plot_spectrum(analysis, figsize=None, xlim=None, ylim=None, save=None):
    """Plot the per-window spectra and the mean spectrum with its peaks.

    ``figsize`` overrides the default figure size; ``xlim``/``ylim`` set the
    axis limits when not None.
    """
    import numpy as np
    import matplotlib.pyplot as plt

    freqs = np.asarray(analysis.freqs)
    fft_abs = np.asarray(analysis.fft_abs)
    mean_spectrum = np.asarray(analysis.mean_spectrum)

    # freqs / fft_abs are (n_freqs, n_windows); use the 1-D frequency axis and
    # plot one faint line per window column.
    freq_axis = freqs[:, 0] if freqs.ndim == 2 else freqs
    spectra = fft_abs if fft_abs.ndim == 2 else fft_abs[:, None]

    fig, ax = plt.subplots(figsize=figsize or (10, 5))

    for k in range(spectra.shape[1]):
        ax.plot(freq_axis, spectra[:, k], lw=0.5, color="0.7",
                label="windows" if k == 0 else None)

    ax.plot(freq_axis, mean_spectrum, lw=1.6, color="C0", label="mean spectrum")

    dom = getattr(analysis, "dominant_period", None)
    if dom:
        f_dom = 1.0 / dom
        ax.axvline(f_dom, color="C3", ls="--", lw=1.0,
                   label="dominant {:.2f} Hz".format(f_dom))

    ax.set_xlabel("Frequency [Hz]")
    ax.set_ylabel("Fourier amplitude [m/s^2 . s]")
    ax.set_title("Ambient spectra", fontweight="bold")
    ax.grid(True, alpha=0.3)
    ax.legend()
    if xlim is not None:
        ax.set_xlim(xlim)
    if ylim is not None:
        ax.set_ylim(ylim)
    fig.tight_layout()

    return _finish(fig, save, "ambient_spectrum")


def plot_mean_spectrum_all(dataset, means, component="x", layout="auto",
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
    _panels.draw_analysis(
        dataset, means,
        curve=lambda r: (r["freqs"], r["spectrum"]),
        layout=layout, group=group, yscale="linear",
        xlabel="Frequency [Hz]", ylabel_unit="m/s^2 . s",
        title_word="Mean amplitude", name="ambient_mean_all",
        figsize=figsize, xlim=xlim, ylim=ylim, save=save)

    if isinstance(means, dict) and any(d in means for d in dataset.devices):
        return {d: means[d]["f_dom"] for d in dataset.devices if d in means}
    if isinstance(means, dict) and "f_dom" in means:
        return means["f_dom"]
    return None
