"""Plots of the STFT (spectrogram)."""


def plot_stft(result, component="x", save=None):
    """Plot a spectrogram.

    Parameters
    ----------
    result : dict
        Output of ``seismic.stft.compute``.
    component : str, default "x"
    save : str or None, default None
    """
    raise NotImplementedError
