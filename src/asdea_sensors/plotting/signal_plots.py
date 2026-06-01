"""Plots of the time signals (acceleration, velocity, displacement)."""


def _finish(fig, save, default_name):
    """Show the figure or save it.

    ``save`` is None -> show; a bare format like "png"/"svg" -> save under a
    name derived from the plot; anything else -> treat as a path.
    """
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


def plot_signals(signal, components="all", kind="acc", factor=1.0, unit=None,
                 time_axis="absolute", figsize=None, xlim=None, ylim=None,
                 save=None):
    """Plot the time histories of a signal.

    Parameters
    ----------
    signal : SignalData
        The signal to plot.
    components : {"x", "y", "z", "all"}, default "all"
    kind : {"acc", "vel", "disp"}, default "acc"
        Which quantity to plot.
    factor : float, default 1.0
        Multiplier applied to the plotted data (e.g. 1/9.81 to show g).
    unit : str or None, default None
        Y-axis unit label; if None the default SI unit for ``kind`` is used.
    time_axis : {"absolute", "relative"}, default "absolute"
        "absolute" uses the real date/time on the x axis (format
        ``%Y-%m-%d %H:%M:%S``), keeping the temporal reference; it needs
        ``signal.t_abs`` (falls back to relative if missing). "relative" uses
        seconds from the window start (time at zero).
    figsize : tuple or None, default None
        Figure size; if None a default based on the number of components.
    xlim, ylim : tuple or None, default None
        Axis limits applied to every subplot when not None. For
        ``time_axis="absolute"`` xlim is a pair of datetimes.
    save : str or None, default None
        File format/path to save the figure (e.g. "svg"), or None to show.
    """
    import matplotlib.pyplot as plt
    import matplotlib.dates as mdates

    labels = {
        "acc": ("Acceleration", "acc", "m/s^2"),
        "vel": ("Velocity", "vel", "m/s"),
        "disp": ("Displacement", "disp", "m"),
    }
    title_word, prefix, default_unit = labels[kind]
    unit = unit if unit is not None else default_unit

    if components == "all":
        comps = ("x", "y", "z")
    else:
        comps = (components,)

    # X axis: absolute date/time when available, else seconds from zero.
    use_abs = (time_axis == "absolute" and getattr(signal, "t_abs", None) is not None)
    time = signal.t_abs if use_abs else signal.time

    fig, axes = plt.subplots(len(comps), 1, sharex=True,
                             figsize=figsize or (10, 2.4 * len(comps)))
    if len(comps) == 1:
        axes = [axes]

    for ax, comp in zip(axes, comps):
        data = getattr(signal, "{}_{}".format(prefix, comp), None)
        if data is None:
            ax.text(0.5, 0.5, "component {} not available".format(comp),
                    ha="center", va="center", transform=ax.transAxes)
        else:
            ax.plot(time, data * factor, lw=0.8, color="C0")
        ax.set_ylabel("{} {}\n[{}]".format(comp.upper(), title_word, unit))
        ax.grid(True, alpha=0.3)
        if xlim is not None:
            ax.set_xlim(xlim)
        if ylim is not None:
            ax.set_ylim(ylim)

    if use_abs:
        axes[-1].xaxis.set_major_formatter(mdates.DateFormatter("%Y-%m-%d %H:%M:%S"))
        for lbl in axes[-1].get_xticklabels():
            lbl.set_rotation(90)
        axes[-1].set_xlabel("Date")
    else:
        axes[-1].set_xlabel("Time [s]")
    axes[0].set_title("{} time history - device {}".format(
        title_word, signal.device), fontweight="bold")
    fig.tight_layout()

    return _finish(fig, save, "signal_{}_{}".format(prefix, signal.device))


def _read_sigs(dataset, devices, start_time, end_time, baseline, fmin, fmax,
               kind):
    """Read each device over the window, optionally correct/filter/derive."""
    sigs = {}
    for device in devices:
        handle = dataset.device(device)
        if start_time is not None and end_time is not None:
            handle = handle.get_window(start_time, end_time)
        if baseline:
            handle = handle.baseline()
        if fmin is not None and fmax is not None:
            handle = handle.filter(fmin, fmax, engine="scipy")
        if kind in ("vel", "disp"):
            handle = handle.derive()
        sigs[device] = handle.signal(components="all")
    return sigs


def plot_signals_all(dataset, devices, start_time=None, end_time=None,
                     components="all", kind="acc", factor=1.0, unit=None,
                     time_axis="absolute", baseline=False, fmin=None, fmax=None,
                     group=False, figsize=None, xlim=None, ylim=None, save=None):
    """Plot the time histories of several sensors over the same window.

    Pass the device list directly (no manual loop).

    Parameters
    ----------
    dataset : SensorDataset
        Source dataset.
    devices : list of str
        Device ids to plot, e.g. ``["MOF00134", "MNAT0031", "MOF00135"]``.
    start_time, end_time : datetime or str
        Window applied to every device.
    components, kind, factor, unit, time_axis, figsize, xlim, ylim
        Same meaning as :func:`plot_signals`.
    baseline : bool, default False
        Apply baseline correction before plotting.
    fmin, fmax : float or None, default None
        Band-pass edges; when both are given the signal is filtered first.
    group : bool, default False
        ``False`` draws one figure per device. ``True`` overlays every device
        on the same axes (one row per component, with a legend).
    save : str or None, default None
        ``None`` shows the figure(s). A bare format ("pdf"/"svg"/"png") saves
        ``signal_<kind>_<device>.<fmt>`` per device, or ``signals_all.<fmt>``
        when grouped.

    Returns
    -------
    list or str or None
        Saved paths (per device) or the grouped figure result.
    """
    import matplotlib.pyplot as plt
    import matplotlib.dates as mdates

    labels = {"acc": ("Acceleration", "acc", "m/s^2"),
              "vel": ("Velocity", "vel", "m/s"),
              "disp": ("Displacement", "disp", "m")}
    title_word, prefix, default_unit = labels[kind]
    unit = unit if unit is not None else default_unit
    comps = ("x", "y", "z") if components == "all" else (components,)

    sigs = _read_sigs(dataset, devices, start_time, end_time, baseline,
                      fmin, fmax, kind)

    if not group:
        paths = []
        for device in devices:
            paths.append(plot_signals(
                sigs[device], components=components, kind=kind, factor=factor,
                unit=unit, time_axis=time_axis, figsize=figsize, xlim=xlim,
                ylim=ylim, save=save))
        return paths

    # group=True: overlay every device, one row per component.
    fig, axes = plt.subplots(len(comps), 1, sharex=True,
                             figsize=figsize or (12, 2.6 * len(comps)))
    if len(comps) == 1:
        axes = [axes]

    for ax, comp in zip(axes, comps):
        for k, device in enumerate(devices):
            sig = sigs[device]
            use_abs = (time_axis == "absolute"
                       and getattr(sig, "t_abs", None) is not None)
            t = sig.t_abs if use_abs else sig.time
            data = getattr(sig, "{}_{}".format(prefix, comp), None)
            if data is not None:
                ax.plot(t, data * factor, lw=0.7, color="C%d" % (k % 10),
                        label=device)
        ax.set_ylabel("{} {}\n[{}]".format(comp.upper(), title_word, unit))
        ax.grid(True, alpha=0.3)
        if xlim is not None:
            ax.set_xlim(xlim)
        if ylim is not None:
            ax.set_ylim(ylim)
    axes[0].legend(loc="upper right", ncol=len(devices), fontsize=8)

    use_abs = (time_axis == "absolute"
               and getattr(sigs[devices[0]], "t_abs", None) is not None)
    if use_abs:
        axes[-1].xaxis.set_major_formatter(mdates.DateFormatter("%Y-%m-%d %H:%M:%S"))
        for lbl in axes[-1].get_xticklabels():
            lbl.set_rotation(90)
        axes[-1].set_xlabel("Date")
    else:
        axes[-1].set_xlabel("Time [s]")
    axes[0].set_title("%s time history - %d sensors" % (title_word, len(devices)),
                      fontweight="bold")
    fig.tight_layout()
    return _finish(fig, save, "signals_all_%s" % kind)
