"""H5Reader: read the acceleration of one device from one or many .h5 files.

The .h5 layout is ``Devices/<id>/Acceleration`` (N, 3) plus ``Timestamp``.
Each sensor uses a per-device axis mapping because the sensors were installed
in a non-standard orientation (see ``config.settings.SENSOR_AXES``). The raw
acceleration is stored in g (the vertical channel sits near -1 g, i.e. gravity),
so it is converted to m/s^2 on read to keep the whole package in SI.

This wraps the original ``readH5File`` routine (to be ported from kraken).
"""


class H5Reader:
    """Read and concatenate acceleration for a single device.

    Parameters
    ----------
    axes_map : dict
        Per-sensor axis mapping ``{device: (ix, iy, iz)}`` selecting which
        physical columns are X, Y, Z for each sensor.
    to_si : bool, default True
        Convert the raw acceleration from g to m/s^2 (multiply by 9.81).
    """

    def __init__(self, axes_map, to_si=True):
        self.axes_map = axes_map
        self.to_si = to_si

    def read(self, files, device, components="all", remove_mean=False):
        """Read ``device`` from ``files`` and return the concatenated signal.

        Parameters
        ----------
        files : list of str
            Ordered .h5 file paths to concatenate.
        device : str
            Device id to read.
        components : {"x", "y", "z", "all"}, default "all"
        remove_mean : bool, default False
            Subtract each component's mean while concatenating.

        Returns
        -------
        dict
            ``{"acc": ..., "time": ..., "dt": ..., "axes": (ix, iy, iz)}``.
        """
        raise NotImplementedError

    def read_one(self, path, device):
        """Read the acceleration of ``device`` from a single .h5 file."""
        raise NotImplementedError

    def dt_from_timestamp(self, path, device):
        """Estimate dt (and fs) for ``device`` from its Timestamp dataset."""
        raise NotImplementedError
