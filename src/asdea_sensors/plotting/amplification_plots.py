"""Plots of the spectral amplification between sensors / floors."""


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


def plot_amplification(result, figsize=None, xlim=None, ylim=None, save=None):
    """Plot the amplification ratios for each sensor.

    Parameters
    ----------
    result : dict
        Output of ``ambient.amplification.compute`` (includes the basis used).
    figsize : tuple or None, default None
        Figure size; if None a default is used.
    xlim, ylim : tuple or None, default None
        Axis limits applied when not None.
    save : str or None, default None
    """
    import matplotlib.pyplot as plt

    freqs = result["freqs"]
    ratios = result["ratios"]
    basis = result.get("basis")

    fig, ax = plt.subplots(figsize=figsize or (10, 5))
    for device, ratio in ratios.items():
        ax.plot(freqs, ratio, lw=1.0, label=str(device))

    ax.axhline(1.0, color="0.5", ls="--", lw=0.8)

    title = "Spectral amplification"
    if basis is not None:
        title += " (basis: {})".format(basis)

    ax.set_xlabel("Frequency [Hz]")
    ax.set_ylabel("Amplification ratio [-]")
    ax.set_title(title, fontweight="bold")
    ax.grid(True, alpha=0.3)
    ax.legend()
    if xlim is not None:
        ax.set_xlim(xlim)
    if ylim is not None:
        ax.set_ylim(ylim)
    fig.tight_layout()

    return _finish(fig, save, "amplification")
