"""Plots for the ambient analysis (STA/LTA, windows, taper, spectrum)."""


def plot_sta_lta(analysis, save=None):
    """Plot the STA/LTA ratio with the acceptance band."""
    raise NotImplementedError


def plot_windows(analysis, save=None):
    """Plot the signal with the selected windows highlighted."""
    raise NotImplementedError


def plot_spectrum(analysis, save=None):
    """Plot the per-window spectra and the mean spectrum with its peaks."""
    raise NotImplementedError
