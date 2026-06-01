"""Modal characterization: frequencies, mode shapes, damping and tracking.

Operational modal analysis (OMA) from the vertical array of sensors: the
amplitude and phase of each floor at a modal frequency give the mode shape;
the bandwidth around the peak gives the damping. Modal tracking follows the
frequencies in time for monitoring.
"""


def modal_frequencies(signals, dt, fband=(0.5, 10.0), n_modes=3, smooth="konno",
                      bexp=40):
    """Identify the modal frequencies shared by the sensors.

    Parameters
    ----------
    signals : dict
        ``{device: signal}`` across the floors.
    dt : float
        Sampling interval in seconds.
    fband : (float, float), default (0.5, 10.0)
        Frequency band to search.
    n_modes : int, default 3
        Number of modes to identify.
    smooth : {None, "konno"}, default "konno"
    bexp : int, default 40

    Returns
    -------
    dict
        Keys: freqs (the identified modal frequencies).
    """
    raise NotImplementedError


def mode_shapes(signals, geometry, dt, modal_freqs=None, component="x",
                fband=(0.5, 10.0), n_modes=3):
    """Mode shapes: amplitude and phase per floor at each modal frequency.

    Parameters
    ----------
    signals : dict
        ``{device: signal}`` across the floors.
    geometry : dict
        ``config.SENSOR_GEOMETRY`` (used to order by height).
    dt : float
        Sampling interval in seconds.
    modal_freqs : sequence or None
        Frequencies to evaluate the shapes at. ``None`` finds them first.
    component : {"x", "y"}, default "x"
    fband : (float, float), default (0.5, 10.0)
    n_modes : int, default 3

    Returns
    -------
    dict
        Keys: freqs, heights, shapes (amplitude per floor), phases.
    """
    raise NotImplementedError


def damping(signal, dt, modal_freq, method="half_power", band=0.1):
    """Modal damping ratio at a given frequency.

    Parameters
    ----------
    signal : np.ndarray
        Single-component signal in m/s^2.
    dt : float
        Sampling interval in seconds.
    modal_freq : float
        Frequency of the mode in Hz.
    method : {"half_power", "random_decrement"}, default "half_power"
    band : float, default 0.1
        Half-width (fraction) of the band around the peak for the fit.

    Returns
    -------
    dict
        Keys: zeta (damping ratio), modal_freq.
    """
    raise NotImplementedError


def tracking(signal, dt, window="10min", overlap=0.5, fband=(1.0, 8.0),
             n_modes=2, smooth="konno", bexp=40):
    """Track modal frequencies over time with a moving window.

    Parameters
    ----------
    signal : np.ndarray
        Single-component signal in m/s^2.
    dt : float
        Sampling interval in seconds.
    window : str or float, default "10min"
        Moving window length.
    overlap : float, default 0.5
    fband : (float, float), default (1.0, 8.0)
    n_modes : int, default 2
    smooth : {None, "konno"}, default "konno"
    bexp : int, default 40

    Returns
    -------
    dict
        Keys: t, freqs (shape ``(n_windows, n_modes)``).
    """
    raise NotImplementedError
