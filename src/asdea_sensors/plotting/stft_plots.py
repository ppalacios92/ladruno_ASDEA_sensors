"""Plots of the STFT (spectrogram)."""


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


def plot_stft(result, component="x", save=None):
    """Plot a spectrogram.

    Parameters
    ----------
    result : dict
        Output of ``seismic.stft.compute``.
    component : str, default "x"
    save : str or None, default None
    """
    import numpy as np
    import matplotlib.pyplot as plt

    f = result["f"]
    t = result["t"]
    zxx = np.abs(result["Zxx"])

    fig, ax = plt.subplots(figsize=(10, 5))
    mesh = ax.pcolormesh(t, f, zxx, shading="auto", cmap="viridis")
    cbar = fig.colorbar(mesh, ax=ax)
    cbar.set_label("Magnitude [m/s^2]")

    ax.set_xlabel("Time [s]")
    ax.set_ylabel("Frequency [Hz]")
    ax.set_title("Spectrogram (STFT) - component {}".format(component),
                 fontweight="bold")
    fig.tight_layout()

    return _finish(fig, save, "stft_{}".format(component))
