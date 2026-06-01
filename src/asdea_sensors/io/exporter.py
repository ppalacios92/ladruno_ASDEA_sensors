"""Exporter: write analysis results to a self-describing .h5 file.

Layout::

    /Provenance
        input_files, pipeline, units, fs, dt, version, created_on,
        config, config_hash
    /Results/<device>/<analysis>
        <datasets>          e.g. T, PSa, IA_percent, freqs, H, ...
        .attrs              all parameters of that result (zeta, nperseg, ...)

Available at two levels: a whole-dataset export and a per-sensor export
(through the device chain).
"""


def export_dataset(dataset, path, analyses=None, components="all"):
    """Export every cached result of the dataset to one .h5 file.

    Parameters
    ----------
    dataset : SensorDataset
        Source dataset (provides the results cache and the provenance).
    path : str
        Output .h5 path.
    analyses : list of str or None
        Restrict to these analyses. ``None`` exports everything cached.
    components : {"x", "y", "z", "all"}, default "all"

    Returns
    -------
    str
        The written path.
    """
    raise NotImplementedError


def export_device(handle, path, analyses=None, components="all"):
    """Export one sensor's results to a .h5 file (used by the device chain).

    Parameters
    ----------
    handle : DeviceHandle
        The per-sensor view to export.
    path : str
        Output .h5 path.
    analyses : list of str or None
    components : {"x", "y", "z", "all"}, default "all"

    Returns
    -------
    str
        The written path.
    """
    raise NotImplementedError
