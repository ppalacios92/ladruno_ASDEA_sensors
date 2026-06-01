"""Plots of the PSD and the band energy."""


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


def plot_psd(result, component="x", figsize=None, xlim=None, ylim=None,
             save=None):
    """Plot a PSD curve.

    Parameters
    ----------
    result : dict
        Output of ``seismic.psd.compute``.
    component : str, default "x"
    figsize : tuple or None, default None
        Figure size; if None a default is used.
    xlim, ylim : tuple or None, default None
        Axis limits applied when not None.
    save : str or None, default None
    """
    import matplotlib.pyplot as plt

    f = result["f"]
    pxx = result["Pxx"]

    fig, ax = plt.subplots(figsize=figsize or (9, 5))
    ax.semilogy(f, pxx, lw=1.0, color="C0")
    ax.set_xlabel("Frequency [Hz]")
    ax.set_ylabel("PSD [(m/s^2)^2/Hz]")
    ax.set_title("Power spectral density - component {}".format(component),
                 fontweight="bold")
    ax.grid(True, which="both", alpha=0.3)
    if xlim is not None:
        ax.set_xlim(xlim)
    if ylim is not None:
        ax.set_ylim(ylim)
    fig.tight_layout()

    return _finish(fig, save, "psd_{}".format(component))


def plot_psd_bands(result, band, figsize=None, xlim=None, ylim=None,
                   save=None):
    """Plot the energy in one band as a bar chart across sensors.

    Parameters
    ----------
    result : dict
        Broadcast PSD result keyed by device.
    band : (float, float)
        The frequency band to display.
    figsize : tuple or None, default None
        Figure size; if None a default based on the number of devices.
    xlim, ylim : tuple or None, default None
        Axis limits applied when not None.
    save : str or None, default None
    """
    import matplotlib.pyplot as plt

    devices = []
    energies = []
    for device, res in result.items():
        be = res.get("band_energy")
        if isinstance(be, dict):
            # Band energy keyed by band -> pick the requested band.
            value = be.get(tuple(band))
            if value is None:
                value = be.get(band)
        else:
            value = be
        if value is None:
            continue
        devices.append(str(device))
        energies.append(value)

    fig, ax = plt.subplots(
        figsize=figsize or (max(6, 0.8 * len(devices) + 2), 5))
    ax.bar(devices, energies, color="C0")
    ax.set_xlabel("Device")
    ax.set_ylabel("Band energy [(m/s^2)^2]")
    ax.set_title("PSD band energy {:.2f}-{:.2f} Hz".format(band[0], band[1]),
                 fontweight="bold")
    ax.grid(True, axis="y", alpha=0.3)
    if devices:
        plt.setp(ax.get_xticklabels(), rotation=45, ha="right")
    if xlim is not None:
        ax.set_xlim(xlim)
    if ylim is not None:
        ax.set_ylim(ylim)
    fig.tight_layout()

    return _finish(fig, save, "psd_bands")


def plot_psd_all(dataset, results, component="x", group=True,
                 figsize=None, xlim=(0, 25), ylim=None, save=None):
    """Plot precomputed Welch PSDs of several sensors (no compute here).

    The PSDs are computed on the object and this function only draws them::

        results = ds.psd(component="x", nperseg=512, noverlap=256)
        plot_psd_all(ds, results, component="x", group=True)
        plot_psd_bands(results, band=(2.0, 8.0))

    Parameters
    ----------
    dataset : SensorDataset
        Source object; used only for the device order and colors.
    results : dict
        Output of ``dataset.psd(component=..., ...)``, i.e.
        ``{device: psd_result}``.
    component : str, default "x"
        Label only (which component the results were computed for).
    group : bool, default True
        ``True`` overlays every device; ``False`` one figure each.
    figsize, xlim, ylim, save
        Plot controls (xlim defaults to 0-25 Hz).

    Returns
    -------
    None or str or list
    """
    import matplotlib.pyplot as plt

    devices = [d for d in dataset.devices if d in results]
    colors = getattr(dataset, "device_colors", {}) or {}

    if group:
        fig, ax = plt.subplots(figsize=figsize or (10, 5))
        for k, device in enumerate(devices):
            r = results[device]
            ax.semilogy(r["f"], r["Pxx"] + 1e-30, lw=0.9,
                        color=colors.get(device, "C%d" % (k % 10)), label=device)
        ax.set_xlabel("Frequency [Hz]")
        ax.set_ylabel("PSD [(m/s^2)^2/Hz]")
        ax.set_title("PSD - %d sensors - component %s" % (len(devices), component),
                     fontweight="bold")
        ax.grid(True, which="both", alpha=0.3)
        ax.legend(fontsize=8)
        if xlim is not None:
            ax.set_xlim(xlim)
        if ylim is not None:
            ax.set_ylim(ylim)
        fig.tight_layout()
        return _finish(fig, save, "psd_all")

    paths = []
    for device in devices:
        paths.append(plot_psd(results[device], component=component,
                              figsize=figsize, xlim=xlim, ylim=ylim, save=save))
    return paths
