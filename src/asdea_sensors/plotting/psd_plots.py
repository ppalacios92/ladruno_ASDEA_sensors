"""Plots of the PSD and the band energy."""


def plot_psd(result, component="x", save=None):
    """Plot a PSD curve.

    Parameters
    ----------
    result : dict
        Output of ``seismic.psd.compute``.
    component : str, default "x"
    save : str or None, default None
    """
    raise NotImplementedError


def plot_psd_bands(result, band, save=None):
    """Plot the energy in one band as a bar chart across sensors.

    Parameters
    ----------
    result : dict
        Broadcast PSD result keyed by device.
    band : (float, float)
        The frequency band to display.
    save : str or None, default None
    """
    raise NotImplementedError
