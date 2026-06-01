"""Plots of the RotD spectra."""

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


def plot_rotd_all(results, dataset=None, rotd=50, layout="auto", group=None,
                  figsize=None, xlim=None, ylim=None, save=None):
    """Plot precomputed RotD spectra (no compute here); layout from shape.

    ``rotd`` may be one percentile or several. Compute them together so they
    share the PSa matrix::

        results = ds.rotd(comp_x="x", comp_y="y", rotd=[0, 50, 100], angle_step=15)
        plot_rotd_all(ds, results, rotd=[0, 50, 100])           # grid: one panel/sensor, 3 curves
        plot_rotd_all(ds, results, rotd=50)                     # one percentile -> sensors overlaid
        plot_rotd_all(ds, results, rotd=50, layout="grid")      # one panel per sensor
        plot_rotd_all(ds, ds.MOF00135.rotd(rotd=[0,50,100]), rotd=[0,50,100])  # one sensor, 3 curves

    Parameters
    ----------
    dataset : SensorDataset
        Source object (device order, colors, titles).
    results : dict or result
        ``ds.rotd(...)`` -> ``{device: rotd_result}``, or a single result.
    rotd : int or sequence of int, default 50
        Percentile(s) to draw; each must be present in the result
        (``ROTD<p>``), i.e. it must have been computed.
    layout : {"auto", "grid", "overlay"}, default "auto"
        With several percentiles the layout is always a grid (one panel per
        sensor, percentiles overlaid). With one percentile, ``overlay`` puts
        every sensor on one axes and ``grid`` gives one panel each.
    group : bool or None
        Back-compat alias (``True`` -> overlay, ``False`` -> grid).
    figsize, xlim, ylim, save
        Plot controls.
    """
    import matplotlib.pyplot as plt

    results, dataset = _panels.resolve(results, dataset)
    pcts = [rotd] if isinstance(rotd, (int, float)) else list(rotd)
    layout = _panels._layout_from_group(layout, group)
    colors = getattr(dataset, "device_colors", {}) or {}
    titles = getattr(dataset, "titles", {}) or {}

    def present(res):
        return [p for p in pcts if ("ROTD%d" % p) in res]

    def style(ax):
        ax.set_xlabel("Period T [s]")
        ax.grid(True, alpha=0.3)
        if xlim is not None:
            ax.set_xlim(xlim)
        if ylim is not None:
            ax.set_ylim(ylim)

    is_multi = _panels._shape(results) in ("device_flat", "device_comp")

    # -- single sensor: requested percentiles overlaid on one axes ----
    if not is_multi:
        fig, ax = plt.subplots(figsize=figsize or (9, 5))
        for i, p in enumerate(present(results)):
            ax.plot(results["T"], results["ROTD%d" % p], lw=1.3,
                    color="C%d" % i, label="RotD%d" % p)
        ax.set_ylabel("PSa [m/s^2]")
        ax.legend(fontsize=8)
        style(ax)
        fig.tight_layout()
        return _panels._finish(fig, save, "rotd_all")

    devices = ([d for d in dataset.devices if d in results]
               if dataset is not None else list(results))

    # -- one percentile, overlay every sensor on one axes -------------
    if len(pcts) == 1 and layout != "grid":
        key = "ROTD%d" % pcts[0]
        fig, ax = plt.subplots(figsize=figsize or (10, 5))
        for j, d in enumerate(devices):
            ax.plot(results[d]["T"], results[d][key], lw=1.1,
                    color=colors.get(d, "C%d" % (j % 10)), label=d)
        ax.set_ylabel("RotD%d PSa [m/s^2]" % pcts[0])
        ax.legend(fontsize=8)
        style(ax)
        fig.tight_layout()
        return _panels._finish(fig, save, "rotd_all_%d" % pcts[0])

    # -- grid: one panel per sensor, percentiles overlaid -------------
    n = len(devices)
    fig, axes = plt.subplots(1, n, figsize=figsize or (3.6 * n, 4.2),
                             squeeze=False)
    for j, d in enumerate(devices):
        ax = axes[0][j]
        res = results[d]
        for i, p in enumerate(present(res)):
            ax.plot(res["T"], res["ROTD%d" % p], lw=1.1, color="C%d" % i,
                    label="RotD%d" % p)
        ax.set_title("%s - %s" % (d, titles.get(d, "")), fontsize=9,
                     fontweight="bold")
        if j == 0:
            ax.set_ylabel("PSa [m/s^2]")
        ax.legend(fontsize=7)
        style(ax)
    fig.tight_layout()
    return _panels._finish(fig, save, "rotd_all")
