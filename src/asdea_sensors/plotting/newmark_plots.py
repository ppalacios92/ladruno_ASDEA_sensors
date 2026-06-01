"""Plots of the Newmark response spectra."""

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


def plot_newmark_all(dataset, specs, components="all", quantity="PSa",
                     unit=None, layout="auto", group=None, figsize=None,
                     xlim=None, ylim=None, save=None):
    """Plot precomputed Newmark spectra (no compute here); layout from shape.

    ::

        specs = ds.newmark(component="all", max_period=3.0, dT=0.02)
        plot_newmark_all(ds, specs, quantity="PSa")          # grid: rows x/y/z, cols sensors
        plot_newmark_all(ds, ds.newmark(component="x"), layout="overlay")   # sensors overlaid
        plot_newmark_all(ds, ds.MOF00135.newmark(component="all"))          # one sensor, comps overlaid

    Parameters
    ----------
    dataset : SensorDataset
        Source object (device order, colors, titles).
    specs : dict
        ``ds.newmark(component="all")`` -> ``{device: {x, y, z: result}}`` or a
        single-component / single-sensor variant.
    components : str or sequence, default "all"
    quantity : {"PSa", "PSv", "Sd", "Sv", "Sa"}, default "PSa"
        Which curve of the result to draw.
    unit : str or None, default None
        Y-axis unit; if None the default SI unit for ``quantity`` is used.
    layout : {"auto", "grid", "overlay"}, default "auto"
    group : bool or None
        Back-compat alias (``True`` -> overlay, ``False`` -> grid).
    figsize, xlim, ylim, save
        Plot controls.
    """
    units = {"PSa": "m/s^2", "Sa": "m/s^2", "PSv": "m/s", "Sv": "m/s", "Sd": "m"}
    ylabel_unit = unit if unit is not None else units.get(quantity, "")
    return _panels.draw_analysis(
        dataset, specs,
        curve=lambda r: (r["T"], r[quantity]),
        components=components, layout=layout, group=group, yscale="linear",
        xlabel="Period T [s]", ylabel_unit=ylabel_unit, title_word=quantity,
        name="newmark_all_%s" % quantity,
        figsize=figsize, xlim=xlim, ylim=ylim, save=save)
