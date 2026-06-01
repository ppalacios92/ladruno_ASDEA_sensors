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
