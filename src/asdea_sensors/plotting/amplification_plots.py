"""Plots of the spectral amplification between sensors / floors."""


def plot_amplification(result, save=None):
    """Plot the amplification ratios for each sensor.

    Parameters
    ----------
    result : dict
        Output of ``ambient.amplification.compute`` (includes the basis used).
    save : str or None, default None
    """
    raise NotImplementedError
