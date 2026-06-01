"""Plots of the RotD spectra."""


def plot_rotd(result, rotd=(0, 50, 100), save=None):
    """Plot one or more RotD percentile spectra.

    Parameters
    ----------
    result : dict
        Output of ``seismic.rotd.compute`` (holds the PSa matrix).
    rotd : sequence of int, default (0, 50, 100)
        Percentiles to draw.
    save : str or None, default None
    """
    raise NotImplementedError
