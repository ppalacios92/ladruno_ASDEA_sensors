"""Plots of the Fourier amplitude spectrum."""


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


def plot_fourier(result, component="x", smooth=None, unit=None,
                 figsize=None, xlim=None, ylim=None, save=None):
    """Plot a Fourier spectrum and mark its dominant frequencies.

    Parameters
    ----------
    result : dict
        Output of ``seismic.fourier.compute``.
    component : str, default "x"
    smooth : {None, "konno"}, default None
    unit : str or None, default None
        Y-axis unit label; if None the default "m/s^2 . s" is used.
    figsize : tuple or None, default None
        Figure size; if None a default is used.
    xlim, ylim : tuple or None, default None
        Axis limits applied when not None.
    save : str or None, default None
    """
    import matplotlib.pyplot as plt

    freqs = result["freqs"]
    spectrum = result["spectrum"]
    unit = unit if unit is not None else "m/s^2 . s"

    fig, ax = plt.subplots(figsize=figsize or (10, 4.5))
    ax.plot(freqs, spectrum, lw=0.9, color="C0", label="amplitude")

    dom_freqs = result.get("dom_freqs")
    dom_peaks = result.get("dom_peaks")
    if dom_freqs is not None and dom_peaks is not None:
        ax.plot(dom_freqs, dom_peaks, "rv", ms=8, label="dominant peaks")
        for f, p in zip(dom_freqs, dom_peaks):
            ax.annotate("{:.2f} Hz".format(f), (f, p),
                        textcoords="offset points", xytext=(0, 8),
                        ha="center", fontsize=8)

    ax.set_xlabel("Frequency [Hz]")
    ax.set_ylabel("Fourier amplitude [{}]".format(unit))
    ax.set_title("Fourier amplitude spectrum - component {}".format(component),
                 fontweight="bold")
    ax.grid(True, alpha=0.3)
    ax.legend()
    if xlim is not None:
        ax.set_xlim(xlim)
    if ylim is not None:
        ax.set_ylim(ylim)
    fig.tight_layout()

    return _finish(fig, save, "fourier_{}".format(component))
