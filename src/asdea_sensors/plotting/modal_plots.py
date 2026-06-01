"""Plots of the modal tracking over time."""


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


def plot_modal_tracking(result, save=None):
    """Plot the tracked modal frequencies against time.

    Parameters
    ----------
    result : dict
        Output of ``structural.modal_tracking.compute``.
    save : str or None, default None
    """
    import numpy as np
    import matplotlib.pyplot as plt

    t = np.asarray(result["t"])
    freqs = np.asarray(result["freqs"])

    fig, ax = plt.subplots(figsize=(10, 5))
    if freqs.ndim == 1:
        ax.plot(t, freqs, ".-", lw=1.0, ms=4, color="C0")
    else:
        # One series per tracked mode (modes along the second axis).
        for k in range(freqs.shape[1]):
            ax.plot(t, freqs[:, k], ".-", lw=1.0, ms=4,
                    label="mode {}".format(k + 1))
        ax.legend()

    ax.set_xlabel("Time [s]")
    ax.set_ylabel("Modal frequency [Hz]")
    ax.set_title("Modal frequency tracking", fontweight="bold")
    ax.grid(True, alpha=0.3)
    fig.tight_layout()

    return _finish(fig, save, "modal_tracking")
