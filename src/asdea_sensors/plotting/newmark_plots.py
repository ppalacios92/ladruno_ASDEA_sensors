"""Plots of the Newmark response spectra."""


def plot_newmark(result, component="x", quantity="PSa", save=None):
    """Plot a Newmark spectral quantity against period.

    Parameters
    ----------
    result : dict
        Output of ``seismic.newmark.compute``.
    component : str, default "x"
    quantity : {"PSa", "PSv", "Sd", "Sv", "Sa"}, default "PSa"
    save : str or None, default None
    """
    raise NotImplementedError
