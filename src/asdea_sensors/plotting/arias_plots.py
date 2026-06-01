"""Plots of the Arias intensity (Husid plot)."""


def plot_arias(result, component="x", save=None):
    """Plot the normalized Arias intensity curve and the significant duration.

    Parameters
    ----------
    result : dict
        Output of ``seismic.arias.compute``.
    component : str, default "x"
    save : str or None, default None
    """
    raise NotImplementedError
