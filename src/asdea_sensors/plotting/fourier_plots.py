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


def plot_fourier_all(dataset, spectra, components=("x", "y", "z"),
                     group=False, figsize=None, xlim=(0, 25), ylim=None,
                     save=None):
    """Plot precomputed Fourier spectra of several sensors (no compute here).

    The spectra are computed on the object and this function only draws them::

        spectra = ds.fourier(component="all", num_frequencies=4,
                             smooth="konno", bexp=40)
        plot_fourier_all(ds, spectra, group=True)

    Parameters
    ----------
    dataset : SensorDataset
        Source object; used only for the device order, colors and titles.
    spectra : dict
        Output of ``dataset.fourier(component="all", ...)``, i.e.
        ``{device: {"x": result, "y": result, "z": result}}``.
    components : sequence of str, default ("x", "y", "z")
        Components to show (one row each).
    group : bool, default False
        ``False`` -> one figure per device. ``True`` -> overlay all devices,
        one row per component.
    figsize, xlim, ylim, save
        Plot controls (xlim defaults to 0-25 Hz).

    Returns
    -------
    list or str or None
    """
    import matplotlib.pyplot as plt

    if isinstance(components, str):
        components = (components,)
    devices = [d for d in dataset.devices if d in spectra]
    colors = getattr(dataset, "device_colors", {}) or {}

    if not group:
        paths = []
        for j, device in enumerate(devices):
            color = colors.get(device, "C%d" % (j % 10))
            fig, axes = plt.subplots(len(components), 1, sharex=True,
                                     figsize=figsize or (10, 2.6 * len(components)))
            if len(components) == 1:
                axes = [axes]
            for ax, c in zip(axes, components):
                res = spectra[device][c]
                ax.semilogy(res["freqs"], res["spectrum"] + 1e-20,
                            lw=0.9, color=color)
                dom_f = res.get("dom_freqs")
                dom_p = res.get("dom_peaks")
                if dom_f is not None and dom_p is not None:
                    ax.plot(dom_f, dom_p, "rv", ms=6)
                ax.set_ylabel("%s\n[m/s^2 . s]" % c.upper())
                ax.grid(True, alpha=0.3)
                if xlim is not None:
                    ax.set_xlim(xlim)
                if ylim is not None:
                    ax.set_ylim(ylim)
            axes[-1].set_xlabel("Frequency [Hz]")
            axes[0].set_title("Fourier spectrum - %s" % device, fontweight="bold")
            fig.tight_layout()
            paths.append(_finish(fig, save, "fourier_all_%s" % device))
        return paths

    # group=True: overlay devices, one row per component.
    fig, axes = plt.subplots(len(components), 1, sharex=True,
                             figsize=figsize or (11, 2.6 * len(components)))
    if len(components) == 1:
        axes = [axes]
    for ax, c in zip(axes, components):
        for j, device in enumerate(devices):
            res = spectra[device][c]
            ax.semilogy(res["freqs"], res["spectrum"] + 1e-20, lw=0.8,
                        color=colors.get(device, "C%d" % (j % 10)), label=device)
        ax.set_ylabel("%s\n[m/s^2 . s]" % c.upper())
        ax.grid(True, alpha=0.3)
        if xlim is not None:
            ax.set_xlim(xlim)
        if ylim is not None:
            ax.set_ylim(ylim)
    axes[0].legend(loc="upper right", ncol=len(devices), fontsize=8)
    axes[-1].set_xlabel("Frequency [Hz]")
    axes[0].set_title("Fourier spectrum - %d sensors" % len(devices),
                      fontweight="bold")
    fig.tight_layout()
    return _finish(fig, save, "fourier_all")
