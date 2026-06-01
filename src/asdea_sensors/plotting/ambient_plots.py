"""Plots for the ambient analysis (STA/LTA, windows, taper, spectrum)."""


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

    fig, ax = plt.subplots(figsize=figsize or (10, 5))

    # Per-window spectra (rows are windows) drawn faintly behind the mean.
    spectra = np.atleast_2d(fft_abs)
    for k, spec in enumerate(spectra):
        ax.plot(freqs, spec, lw=0.5, color="0.7",
                label="windows" if k == 0 else None)

    ax.plot(freqs, mean_spectrum, lw=1.6, color="C0", label="mean spectrum")

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
