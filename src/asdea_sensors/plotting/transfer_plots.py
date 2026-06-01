"""Plots of the floor/base transfer function."""


def plot_transfer_function(result, save=None):
    """Plot a transfer function magnitude and mark the modal frequencies.

    Parameters
    ----------
    result : dict
        Output of ``structural.transfer_function.compute``.
    save : str or None, default None
    """
    raise NotImplementedError
