"""Plots of the Arias intensity (Husid plot)."""

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


def plot_arias(result, component="x", figsize=None, xlim=None, ylim=None,
               save=None):
    """Plot the normalized Arias intensity curve and the significant duration.

    Parameters
    ----------
    result : dict
        Output of ``seismic.arias.compute``.
    component : str, default "x"
    figsize : tuple or None, default None
        Figure size; if None a default is used.
    xlim, ylim : tuple or None, default None
        Axis limits applied when not None.
    save : str or None, default None
    """
    import numpy as np
    import matplotlib.pyplot as plt

    ia = np.asarray(result["IA_percent"])
    dt = result.get("dt")
    if dt is not None:
        x = np.arange(ia.size) * dt
        xlabel = "Time [s]"
        t_start = result.get("t_start")
        t_end = result.get("t_end")
    else:
        # Fall back to percentage of record length along the x axis.
        x = np.linspace(0.0, 100.0, ia.size)
        xlabel = "Record length [%]"
        t_start = result.get("t_start")
        t_end = result.get("t_end")

    fig, ax = plt.subplots(figsize=figsize or (9, 5))
    ax.plot(x, ia, lw=1.3, color="C0", label="Arias intensity")

    if t_start is not None and t_end is not None:
        ax.axvline(t_start, color="C3", ls="--", lw=1.0,
                   label="significant duration")
        ax.axvline(t_end, color="C3", ls="--", lw=1.0)
        ax.axvspan(t_start, t_end, color="C3", alpha=0.1)

    ia_total = result.get("IA_total")
    title = "Husid plot - component {}".format(component)
    if ia_total is not None:
        title += "  (IA_total = {:.4g} m/s)".format(ia_total)

    ax.set_xlabel(xlabel)
    ax.set_ylabel("Normalized Arias intensity [%]")
    ax.set_title(title, fontweight="bold")
    ax.grid(True, alpha=0.3)
    ax.legend()
    if xlim is not None:
        ax.set_xlim(xlim)
    if ylim is not None:
        ax.set_ylim(ylim)
    fig.tight_layout()

    return _finish(fig, save, "arias_{}".format(component))


def plot_arias_all(dataset, results, components="all", layout="auto",
                   group=None, figsize=None, xlim=None, ylim=None, save=None):
    """Plot precomputed Arias curves (no compute here); layout from shape.

    ::

        arias = ds.arias(component="all", low=5, high=95)
        plot_arias_all(ds, arias)                 # grid: rows x/y/z, cols sensors
        plot_arias_all(ds, ds.arias(component="x"), layout="overlay")   # sensors overlaid
        plot_arias_all(ds, ds.MOF00135.arias(component="all"))          # one sensor, comps overlaid

    The significant-duration band (t_start..t_end) is shaded in each panel.

    Parameters
    ----------
    dataset : SensorDataset
        Source object (device order, colors, titles).
    results : dict
        ``ds.arias(component="all")`` -> ``{device: {x, y, z: result}}`` or a
        single-component / single-sensor variant.
    components : str or sequence, default "all"
    layout : {"auto", "grid", "overlay"}, default "auto"
    group : bool or None
        Back-compat alias (``True`` -> overlay, ``False`` -> grid).
    figsize, xlim, ylim, save
        Plot controls.
    """
    import numpy as np

    def curve(r):
        ia = np.asarray(r["IA_percent"])
        dt = r.get("dt")
        x = np.arange(ia.size) * dt if dt else np.linspace(0.0, 100.0, ia.size)
        return x, ia

    def mark(ax, r, color):
        t0, t1 = r.get("t_start"), r.get("t_end")
        if t0 is not None and t1 is not None:
            ax.axvspan(t0, t1, color="C3", alpha=0.12)

    return _panels.draw_analysis(
        dataset, results, curve=curve,
        components=components, layout=layout, group=group, yscale="linear",
        xlabel="Time [s]", ylabel_unit="%", title_word="Arias intensity",
        name="arias_all", mark=mark,
        figsize=figsize, xlim=xlim, ylim=ylim, save=save)
