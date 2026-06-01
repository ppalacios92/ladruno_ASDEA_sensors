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


def plot_newmark_all(dataset, specs, component="x", quantity="PSa", unit=None,
                     group=True, figsize=None, xlim=None, ylim=None, save=None):
    """Plot precomputed Newmark spectra of several sensors (no compute here).

    The spectra are computed on the object and this function only draws them::

        specs = ds.newmark(component="x", zeta=0.05, max_period=3.0, dT=0.02)
        plot_newmark_all(ds, specs, component="x", quantity="PSa", group=True)

    Parameters
    ----------
    dataset : SensorDataset
        Source object; used only for the device order and colors.
    specs : dict
        Output of ``dataset.newmark(component=..., ...)``, i.e.
        ``{device: newmark_result}``.
    component : str, default "x"
        Label only (which component the spectra were computed for).
    quantity : {"PSa", "PSv", "Sd", "Sv", "Sa"}, default "PSa"
        Which curve of the result to draw.
    unit : str or None, default None
        Y-axis unit label; if None the default SI unit for ``quantity`` is used.
    group : bool, default True
        ``True`` overlays every device on one axes; ``False`` one figure each.
    figsize, xlim, ylim, save
        Plot controls.

    Returns
    -------
    list or str or None
    """
    import matplotlib.pyplot as plt

    units = {"PSa": "m/s^2", "Sa": "m/s^2", "PSv": "m/s", "Sv": "m/s", "Sd": "m"}
    ylabel_unit = unit if unit is not None else units.get(quantity, "")
    devices = [d for d in dataset.devices if d in specs]
    colors = getattr(dataset, "device_colors", {}) or {}

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
