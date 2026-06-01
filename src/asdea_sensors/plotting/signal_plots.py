"""Plots of the time signals (acceleration, velocity, displacement)."""


def plot_signals(signal, components="all", kind="acc", save=None):
    """Plot the time histories of a signal.

    Parameters
    ----------
    signal : SignalData
        The signal to plot.
    components : {"x", "y", "z", "all"}, default "all"
    kind : {"acc", "vel", "disp"}, default "acc"
        Which quantity to plot.
    save : str or None, default None
        File format/path to save the figure (e.g. "svg"), or None to show.
    """
    raise NotImplementedError
