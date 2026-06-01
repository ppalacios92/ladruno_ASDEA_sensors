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


def plot_psd_all(dataset, devices=None, start_time=None, end_time=None, component="x",
                 nperseg=512, noverlap=256, window="hann", bands=None,
                 baseline=True, fmin=None, fmax=None, group=True,
                 figsize=None, xlim=(0, 25), ylim=None, save=None):
    """PSD of several sensors over a window (no manual loop).

    Reads each device, optionally baseline-corrects and band-passes it, computes
    the Welch PSD and overlays the curves; also returns the per-device results
    so band energy can be compared with :func:`plot_psd_bands`.

    Parameters
    ----------
    dataset : SensorDataset
    devices : list of str
    start_time, end_time : datetime or str
    component : str, default "x"
    nperseg, noverlap, window, bands
        Welch parameters (see ``seismic.psd.compute``).
    baseline : bool, default True
    fmin, fmax : float or None
        Band-pass edges applied before the PSD when given.
    group : bool, default True
        ``True`` overlays every device; ``False`` one figure each.
    figsize, xlim, ylim, save
        Plot controls (xlim defaults to 0-25 Hz).

    Returns
    -------
    dict
        ``{device: psd_result}`` (use it with ``plot_psd_bands``).
    """
    import matplotlib.pyplot as plt
    from ..seismic import psd as _psd

    devices = list(dataset.devices) if devices is None else list(devices)
    results = {}
    for device in devices:
        handle = dataset.device(device)
        if start_time is not None and end_time is not None:
            handle = handle.get_window(start_time, end_time)
        if baseline:
            handle = handle.baseline()
        if fmin is not None and fmax is not None:
            handle = handle.filter(fmin, fmax, engine="scipy")
        sig = handle.signal(components="all")
        results[device] = _psd.compute(sig.component(component), sig.dt,
                                       nperseg=nperseg, noverlap=noverlap,
                                       window=window, bands=bands)

    if group:
        fig, ax = plt.subplots(figsize=figsize or (10, 5))
        for k, device in enumerate(devices):
            r = results[device]
            ax.semilogy(r["f"], r["Pxx"] + 1e-30, lw=0.9,
                        color="C%d" % (k % 10), label=device)
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
        _finish(fig, save, "psd_all")
    else:
        for device in devices:
            plot_psd(results[device], component=component, figsize=figsize,
                     xlim=xlim, ylim=ylim, save=save)
    return results
