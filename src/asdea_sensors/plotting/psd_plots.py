"""Plots of the PSD and the band energy."""

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


def plot_psd_all(dataset, results, components="all", layout="auto", group=None,
                 figsize=None, xlim=(0, 25), ylim=None, save=None):
    """Plot precomputed Welch PSDs (no compute here); layout from shape.

    ::

        results = ds.psd(component="all", nperseg=512)
        plot_psd_all(ds, results)                 # grid: rows x/y/z, cols sensors
        plot_psd_all(ds, ds.psd(component="x"), layout="overlay")   # sensors overlaid
        plot_psd_all(ds, ds.MOF00135.psd(component="all"))          # one sensor, comps overlaid
        plot_psd_bands(results, band=(2.0, 8.0))  # band energy bar chart

    Parameters
    ----------
    dataset : SensorDataset
        Source object (device order, colors, titles).
    results : dict
        ``ds.psd(component="all")`` -> ``{device: {x, y, z: result}}`` or a
        single-component / single-sensor variant.
    components : str or sequence, default "all"
    layout : {"auto", "grid", "overlay"}, default "auto"
    group : bool or None
        Back-compat alias (``True`` -> overlay, ``False`` -> grid).
    figsize, xlim, ylim, save
        Plot controls (xlim defaults to 0-25 Hz).
    """
    return _panels.draw_analysis(
        dataset, results,
        curve=lambda r: (r["f"], r["Pxx"] + 1e-30),
        components=components, layout=layout, group=group, yscale="log",
        xlabel="Frequency [Hz]", ylabel_unit="(m/s^2)^2/Hz",
        title_word="PSD", name="psd_all",
        figsize=figsize, xlim=xlim, ylim=ylim, save=save)
