"""Plots of the Fourier amplitude spectrum."""

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


def plot_fourier(result, component="x", unit=None,
                 figsize=None, xlim=None, ylim=None, save=None):
    """Plot a Fourier spectrum and mark its dominant frequencies.

    Parameters
    ----------
    result : dict
        Output of ``seismic.fourier.compute``.
    component : str, default "x"
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


def plot_fourier_all(spectra, dataset=None, components="all", layout="auto",
                     group=None, figsize=None, xlim=(0, 25), ylim=None,
                     save=None):
    """Plot precomputed Fourier spectra (no compute here); layout from shape.

    The spectra are computed on the object and this only draws them::

        spectra = ds.fourier(component="all", num_frequencies=4, smooth="konno")
        plot_fourier_all(ds, spectra)                 # grid: rows x/y/z, cols sensors
        plot_fourier_all(ds, spectra, layout="overlay")   # sensors overlaid per row
        plot_fourier_all(ds, ds.MOF00135.fourier(component="all"))  # one sensor, comps overlaid

    Parameters
    ----------
    dataset : SensorDataset
        Source object (device order, colors, titles).
    spectra : dict
        ``ds.fourier(component="all")`` -> ``{device: {x, y, z: result}}``;
        ``ds.MOF00135.fourier(component="all")`` -> ``{x, y, z: result}``;
        or a single component variant. See ``_panels`` for the shapes.
    components : str or sequence, default "all"
        Components to include.
    layout : {"auto", "grid", "overlay"}, default "auto"
    group : bool or None
        Back-compat alias (``True`` -> overlay, ``False`` -> grid).
    figsize, xlim, ylim, save
        Plot controls (xlim defaults to 0-25 Hz).
    """
    spectra, dataset = _panels.resolve(spectra, dataset)

    def mark(ax, res, color):
        dom_f, dom_p = res.get("dom_freqs"), res.get("dom_peaks")
        if dom_f is not None and dom_p is not None:
            ax.plot(dom_f, dom_p, "rv", ms=6)

    return _panels.draw_analysis(
        spectra, dataset=dataset,
        curve=lambda r: (r["freqs"], r["spectrum"] + 1e-20),
        components=components, layout=layout, group=group, yscale="log",
        xlabel="Frequency [Hz]", ylabel_unit="m/s^2 . s",
        title_word="Fourier amplitude", name="fourier_all", mark=mark,
        figsize=figsize, xlim=xlim, ylim=ylim, save=save)
