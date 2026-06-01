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
