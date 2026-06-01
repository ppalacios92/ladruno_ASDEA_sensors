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


def plot_rotd_all(dataset, results, rotd=50, layout="auto", group=None,
                  figsize=None, xlim=None, ylim=None, save=None):
    """Plot precomputed RotD spectra (no compute here); layout from shape.

    RotD has one series per sensor (the rotated percentile), so::

        results = ds.rotd(comp_x="x", comp_y="y", rotd=50, angle_step=15)
        plot_rotd_all(ds, results, rotd=50)                 # sensors overlaid
        plot_rotd_all(ds, results, rotd=50, layout="grid")  # one panel per sensor
        plot_rotd_all(ds, ds.MOF00135.rotd(rotd=50), rotd=50)   # one sensor, one curve

    Parameters
    ----------
    dataset : SensorDataset
        Source object (device order, colors, titles).
    results : dict or result
        ``ds.rotd(...)`` -> ``{device: rotd_result}``, or a single result.
    rotd : int, default 50
        Which percentile key (``ROTD<rotd>``) to draw; must match the compute.
    layout : {"auto", "grid", "overlay"}, default "auto"
    group : bool or None
        Back-compat alias (``True`` -> overlay, ``False`` -> grid).
    figsize, xlim, ylim, save
        Plot controls.
    """
    key = "ROTD%d" % rotd
    return _panels.draw_analysis(
        dataset, results,
        curve=lambda r: (r["T"], r[key]),
        layout=layout, group=group, yscale="linear",
        xlabel="Period T [s]", ylabel_unit="m/s^2",
        title_word="RotD%d PSa" % rotd, name="rotd_all_%d" % rotd,
        figsize=figsize, xlim=xlim, ylim=ylim, save=save)
