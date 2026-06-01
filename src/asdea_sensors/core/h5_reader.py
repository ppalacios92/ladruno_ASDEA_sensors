"""H5Reader: read the acceleration of one device from one or many .h5 files.

The .h5 layout is ``Devices/<id>/Acceleration`` (N, 3) plus ``Timestamp``.
Each sensor uses a per-device axis mapping because the sensors were installed
in a non-standard orientation (see ``config.settings.SENSOR_AXES``). The raw
acceleration is stored in g (the vertical channel sits near -1 g, i.e. gravity),
so it is converted to m/s^2 on read to keep the whole package in SI.

This wraps the original ``readH5File`` routine (to be ported from kraken).
"""

import warnings

import h5py
import numpy as np

from asdea_sensors.config import settings


class H5Reader:
    """Read and concatenate acceleration for a single device.

    Parameters
    ----------
    axes_map : dict
        Per-sensor axis mapping ``{device: (ix, iy, iz)}`` selecting which
        physical columns are X, Y, Z for each sensor.
    to_si : bool, default True
        Convert the raw acceleration from g to m/s^2 (multiply by 9.81).
    dt : float or None, default None
        Forced sampling interval. When given, the time vector uses it instead
        of estimating from the Timestamp dataset.
    """

    def __init__(self, axes_map, to_si=True, dt=None):
        self.axes_map = axes_map
        self.to_si = to_si
        self._dt_override = dt

    def _resolve_axes(self, device, ncols):
        """Return the (ix, iy, iz) columns to use for ``device``.

        The original mapping was written for files with more channels. The
        current files only have 3 columns, so any mapped index that is out of
        range falls back to the natural (0, 1, 2) order.
        """
        axes = self.axes_map.get(device, (0, 1, 2))
        if any(idx >= ncols for idx in axes):
            warnings.warn(
                "H5Reader: axes %r for %r exceed the %d available columns; "
                "falling back to (0, 1, 2)" % (axes, device, ncols)
            )
            axes = (0, 1, 2)
        return tuple(axes)

    def read_one(self, path, device):
        """Read the acceleration of ``device`` from a single .h5 file."""
        with h5py.File(path, "r") as f:
            raw = f["Devices/%s/Acceleration" % device][:]

        ncols = raw.shape[1]
        ix, iy, iz = self._resolve_axes(device, ncols)

        acc = np.empty((raw.shape[0], 3), dtype=np.float64)
        acc[:, 0] = raw[:, ix]
        acc[:, 1] = raw[:, iy]
        acc[:, 2] = raw[:, iz]

        if self.to_si:
            acc *= settings.GRAVITY

        return acc

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
        if not files:
            raise ValueError("read: 'files' is empty")

        chunks = [self.read_one(p, device) for p in files]
        acc = np.concatenate(chunks, axis=0)

        # remember the axis mapping that was actually used (files have 3 cols).
        axes = self._resolve_axes(device, 3)

        # dt / continuous time vector rebuilt from the per-sample interval
        # (or the forced override when the timestamps are unreliable).
        dt = self._dt_override or self.dt_from_timestamp(files[0], device)[0]
        n = acc.shape[0]
        time = np.arange(n, dtype=np.float64) * dt

        if remove_mean:
            acc = acc - acc.mean(axis=0, keepdims=True)

        # optionally keep a single component.
        comp_index = {"x": 0, "y": 1, "z": 2}
        if components != "all":
            key = components.lower()
            if key not in comp_index:
                raise ValueError("read: unknown components %r" % components)
            acc = acc[:, comp_index[key]]

        return {"acc": acc, "time": time, "dt": dt, "axes": axes}

    def dt_from_timestamp(self, path, device):
        """Estimate dt (and fs) for ``device`` from its Timestamp dataset."""
        with h5py.File(path, "r") as f:
            acc = f["Devices/%s/Acceleration" % device]
            ts = f["Devices/%s/Timestamp" % device]
            n = acc.shape[0]
            m = ts.shape[0]
            row_first = ts[0]
            row_last = ts[-1]

        # samples covered by each Timestamp row.
        samples_per_row = n / float(m)

        # absolute time of each row: unix_seconds + nanoseconds * 1e-9.
        t_first = float(row_first[0]) + float(row_first[1]) * 1e-9
        t_last = float(row_last[0]) + float(row_last[1]) * 1e-9
        elapsed = t_last - t_first

        # M rows -> M-1 intervals between the first and last row.
        rows_spanned = m - 1
        elapsed_per_row = elapsed / float(rows_spanned)

        dt = elapsed_per_row / samples_per_row
        fs = 1.0 / dt
        return dt, fs
