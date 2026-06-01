"""Plots of the floor/base transfer function."""


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


def plot_transfer_function(result, figsize=None, xlim=None, ylim=None,
                           save=None):
    """Plot a transfer function magnitude and mark the modal frequencies.

    Parameters
    ----------
    result : dict
        Output of ``structural.transfer_function.compute``.
    figsize : tuple or None, default None
        Figure size; if None a default is used.
    xlim, ylim : tuple or None, default None
        Axis limits applied when not None.
    save : str or None, default None
    """
    import numpy as np
    import matplotlib.pyplot as plt

    f = result["f"]
    h = np.abs(result["H"])

    fig, ax = plt.subplots(figsize=figsize or (10, 5))
    ax.plot(f, h, lw=1.0, color="C0", label="|H(f)|")

    modal_freqs = result.get("modal_freqs")
    modal_amps = result.get("modal_amps")
    if modal_freqs is not None and modal_amps is not None:
        ax.plot(modal_freqs, modal_amps, "rv", ms=8, label="modal frequencies")
        for mf, ma in zip(modal_freqs, modal_amps):
            ax.annotate("{:.2f} Hz".format(mf), (mf, ma),
                        textcoords="offset points", xytext=(0, 8),
                        ha="center", fontsize=8)

    ax.set_xlabel("Frequency [Hz]")
    ax.set_ylabel("Transfer function magnitude [-]")
    ax.set_title("Transfer function", fontweight="bold")
    ax.grid(True, alpha=0.3)
    ax.legend()
    if xlim is not None:
        ax.set_xlim(xlim)
    if ylim is not None:
        ax.set_ylim(ylim)
    fig.tight_layout()

    return _finish(fig, save, "transfer_function")
