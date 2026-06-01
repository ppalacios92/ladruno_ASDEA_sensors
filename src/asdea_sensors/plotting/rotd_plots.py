"""Plots of the RotD spectra."""


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


def plot_rotd(result, rotd=(0, 50, 100), figsize=None, xlim=None, ylim=None,
              save=None):
    """Plot one or more RotD percentile spectra.

    Parameters
    ----------
    result : dict
        Output of ``seismic.rotd.compute`` (holds the PSa matrix).
    rotd : sequence of int, default (0, 50, 100)
        Percentiles to draw.
    figsize : tuple or None, default None
        Figure size; if None a default is used.
    xlim, ylim : tuple or None, default None
        Axis limits applied when not None.
    save : str or None, default None
    """
    import matplotlib.pyplot as plt

    T = result["T"]

    fig, ax = plt.subplots(figsize=figsize or (9, 5))
    for n in rotd:
        key = "ROTD{}".format(n)
        if key not in result:
            continue
        ax.plot(T, result[key], lw=1.3, label="RotD{}".format(n))

    ax.set_xlabel("Period T [s]")
    ax.set_ylabel("PSa [m/s^2]")
    ax.set_title("RotD percentile spectra", fontweight="bold")
    ax.grid(True, alpha=0.3)
    ax.legend()
    if xlim is not None:
        ax.set_xlim(xlim)
    if ylim is not None:
        ax.set_ylim(ylim)
    fig.tight_layout()

    return _finish(fig, save, "rotd_spectra")


def plot_rotd_all(dataset, devices=None, start_time=None, end_time=None, comp_x="x", comp_y="y",
                  rotd=50, damping=0.05, angle_step=15, max_period=3.0, dT=0.02,
                  baseline=True, fmin=None, fmax=None, figsize=None, xlim=None,
                  ylim=None, save=None):
    """One RotD percentile spectrum per sensor, overlaid (no manual loop).

    Parameters
    ----------
    dataset : SensorDataset
    devices : list of str
    start_time, end_time : datetime or str
    comp_x, comp_y : str
        The two horizontal components to rotate.
    rotd : int, default 50
        Percentile to draw for every sensor (0/50/100).
    damping, angle_step, max_period, dT
        RotD parameters (coarser defaults keep it fast).
    baseline : bool, default True
    fmin, fmax : float or None
        Band-pass edges applied before the spectrum when given.
    figsize, xlim, ylim, save
        Plot controls.

    Returns
    -------
    None or str
    """
    import matplotlib.pyplot as plt
    from ..seismic import rotd as _rotd

    devices = list(dataset.devices) if devices is None else list(devices)
    colors = getattr(dataset, "device_colors", {}) or {}
    key = "ROTD%d" % rotd
    fig, ax = plt.subplots(figsize=figsize or (10, 5))
    for k, device in enumerate(devices):
        handle = dataset.device(device)
        if start_time is not None and end_time is not None:
            handle = handle.get_window(start_time, end_time)
        if baseline:
            handle = handle.baseline()
        if fmin is not None and fmax is not None:
            handle = handle.filter(fmin, fmax, engine="scipy")
        sig = handle.signal(components="all")
        r = _rotd.compute(sig.component(comp_x), sig.component(comp_y), sig.dt,
                          rotd=rotd, damping=damping, angle_step=angle_step,
                          max_period=max_period, dT=dT)
        ax.plot(r["T"], r[key], lw=1.1,
                color=colors.get(device, "C%d" % (k % 10)), label=device)

    ax.set_xlabel("Period T [s]")
    ax.set_ylabel("RotD%d PSa [m/s^2]" % rotd)
    ax.set_title("RotD%d - %d sensors" % (rotd, len(devices)), fontweight="bold")
    ax.grid(True, alpha=0.3)
    ax.legend(fontsize=8)
    if xlim is not None:
        ax.set_xlim(xlim)
    if ylim is not None:
        ax.set_ylim(ylim)
    fig.tight_layout()
    return _finish(fig, save, "rotd_all_%d" % rotd)
