"""Plots of the Newmark response spectra."""


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


def plot_newmark(result, component="x", quantity="PSa", unit=None,
                 figsize=None, xlim=None, ylim=None, save=None):
    """Plot a Newmark spectral quantity against period.

    Parameters
    ----------
    result : dict
        Output of ``seismic.newmark.compute``.
    component : str, default "x"
    quantity : {"PSa", "PSv", "Sd", "Sv", "Sa"}, default "PSa"
    unit : str or None, default None
        Y-axis unit label; if None the default unit for ``quantity`` is used.
    figsize : tuple or None, default None
        Figure size; if None a default is used.
    xlim, ylim : tuple or None, default None
        Axis limits applied when not None.
    save : str or None, default None
    """
    import matplotlib.pyplot as plt

    units = {
        "PSa": "m/s^2",
        "Sa": "m/s^2",
        "PSv": "m/s",
        "Sv": "m/s",
        "Sd": "m",
    }
    unit = unit if unit is not None else units.get(quantity, "")

    T = result["T"]
    y = result[quantity]

    fig, ax = plt.subplots(figsize=figsize or (9, 5))
    ax.plot(T, y, lw=1.3, color="C0")
    ax.set_xlabel("Period T [s]")
    ax.set_ylabel("{} [{}]".format(quantity, unit))
    ax.set_title("Newmark spectrum {} - component {}".format(
        quantity, component), fontweight="bold")
    ax.grid(True, alpha=0.3)
    if xlim is not None:
        ax.set_xlim(xlim)
    if ylim is not None:
        ax.set_ylim(ylim)
    fig.tight_layout()

    return _finish(fig, save, "newmark_{}_{}".format(quantity, component))


def plot_newmark_all(dataset, devices=None, start_time=None, end_time=None, component="x",
                     quantity="PSa", zeta=0.05, max_period=3.0, dT=0.02,
                     factor=1.0, unit=None, baseline=True, fmin=None, fmax=None,
                     group=True, figsize=None, xlim=None, ylim=None, save=None):
    """Newmark spectra of several sensors over a window (no manual loop).

    Reads each device, optionally baseline-corrects and band-passes it, computes
    the Newmark spectrum and plots the chosen ``quantity`` (PSa by default).

    Parameters
    ----------
    dataset : SensorDataset
    devices : list of str
    start_time, end_time : datetime or str
        Window applied to every device.
    component : str, default "x"
    quantity : {"PSa", "PSv", "Sd", "Sv", "Sa"}, default "PSa"
    zeta, max_period, dT, factor : floats
        Newmark parameters (``factor=1/9.81`` to show acceleration spectra in g).
    baseline : bool, default True
    fmin, fmax : float or None
        Band-pass edges applied before the spectrum when given.
    group : bool, default True
        ``True`` overlays every device on one axes; ``False`` one figure each.
    unit, figsize, xlim, ylim, save
        Plot controls.

    Returns
    -------
    list or str or None
    """
    import matplotlib.pyplot as plt
    from ..seismic import newmark as _newmark

    units = {"PSa": "m/s^2", "Sa": "m/s^2", "PSv": "m/s", "Sv": "m/s", "Sd": "m"}
    ylabel_unit = unit if unit is not None else units.get(quantity, "")
    devices = list(dataset.devices) if devices is None else list(devices)
    colors = getattr(dataset, "device_colors", {}) or {}

    specs = {}
    for device in devices:
        handle = dataset.device(device)
        if start_time is not None and end_time is not None:
            handle = handle.get_window(start_time, end_time)
        if baseline:
            handle = handle.baseline()
        if fmin is not None and fmax is not None:
            handle = handle.filter(fmin, fmax, engine="scipy")
        sig = handle.signal(components="all")
        specs[device] = _newmark.compute(sig.component(component), sig.dt,
                                         zeta=zeta, max_period=max_period,
                                         dT=dT, factor=factor)

    if not group:
        paths = []
        for device in devices:
            paths.append(plot_newmark(specs[device], component=component,
                                      quantity=quantity, unit=ylabel_unit,
                                      figsize=figsize, xlim=xlim, ylim=ylim,
                                      save=save))
        return paths

    fig, ax = plt.subplots(figsize=figsize or (10, 5))
    for k, device in enumerate(devices):
        s = specs[device]
        ax.plot(s["T"], s[quantity], lw=1.1,
                color=colors.get(device, "C%d" % (k % 10)), label=device)
    ax.set_xlabel("Period T [s]")
    ax.set_ylabel("%s [%s]" % (quantity, ylabel_unit))
    ax.set_title("Newmark %s - %d sensors - component %s"
                 % (quantity, len(devices), component), fontweight="bold")
    ax.grid(True, alpha=0.3)
    ax.legend(fontsize=8)
    if xlim is not None:
        ax.set_xlim(xlim)
    if ylim is not None:
        ax.set_ylim(ylim)
    fig.tight_layout()
    return _finish(fig, save, "newmark_all_%s" % quantity)
