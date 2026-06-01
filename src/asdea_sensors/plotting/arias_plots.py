"""Plots of the Arias intensity (Husid plot)."""


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


def plot_arias(result, component="x", save=None):
    """Plot the normalized Arias intensity curve and the significant duration.

    Parameters
    ----------
    result : dict
        Output of ``seismic.arias.compute``.
    component : str, default "x"
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

    fig, ax = plt.subplots(figsize=(9, 5))
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
    fig.tight_layout()

    return _finish(fig, save, "arias_{}".format(component))
