"""Plots of the Fourier amplitude spectrum."""


def plot_fourier(result, component="x", smooth=None, save=None):
    """Plot a Fourier spectrum and mark its dominant frequencies.

    Parameters
    ----------
    result : dict
        Output of ``seismic.fourier.compute``.
    component : str, default "x"
    smooth : {None, "konno"}, default None
    save : str or None, default None
    """
    raise NotImplementedError
