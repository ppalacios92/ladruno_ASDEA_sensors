"""H5Index: scan a folder once, parse each file's date and detect the devices,
sampling rate and time span. Built once at construction; queried many times.
"""

import glob
import os
import warnings
from datetime import datetime

import h5py
import numpy as np


class H5Index:
    """Index of the .h5 files in a folder.

    Parameters
    ----------
    path : str
        Folder to scan.
    pattern : str, default "*.h5"
        Glob used to select the files.
    date_source : {"filename", "timestamp"}, default "filename"
        How to date each file. "filename" parses ``YYYYMMDDHHMMSS`` from the
        name (canonical); "timestamp" reads the embedded clock.

    Attributes
    ----------
    files : list of tuple
        Sorted ``(datetime, path)`` entries.
    devices : list of str
        Device ids present in the files.
    fs : float
        Sampling frequency in Hz, measured from the Timestamp dataset.
    dt : float
        Sampling interval in seconds.
    """

    def __init__(self, path, pattern="*.h5", date_source="filename"):
        self.path = path
        self.pattern = pattern
        self.date_source = date_source
        self.files = []
        self.devices = []
        self.fs = None
        self.dt = None

        # 1) glob the folder and parse each file's date into (datetime, path).
        for fpath in glob.glob(os.path.join(path, pattern)):
            stem = os.path.splitext(os.path.basename(fpath))[0]
            when = self.parse_date(stem)
            if when is None:
                continue
            self.files.append((when, fpath))
        self.files.sort(key=lambda item: item[0])

        if not self.files:
            warnings.warn("H5Index: no files matched %r in %r" % (pattern, path))
            return

        # 2) open one file and list the groups under "Devices".
        first = self.files[0][1]
        with h5py.File(first, "r") as f:
            if "Devices" in f:
                self.devices = sorted(f["Devices"].keys())

        # 3) estimate fs / dt from the Timestamp dataset of the first device.
        if self.devices:
            self.dt, self.fs = self._estimate_dt(first, self.devices[0])

    def _estimate_dt(self, path, device):
        """Estimate (dt, fs) from one device's Timestamp dataset in ``path``.

        Each Timestamp row covers a fixed block of acceleration samples
        (N / M samples per row). Two distant Timestamp rows give the elapsed
        wall-clock time; dividing it by the number of acceleration samples in
        between gives the per-sample interval.
        """
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

        # rows spanned between the two (M rows -> M-1 intervals).
        rows_spanned = m - 1
        elapsed_per_row = elapsed / float(rows_spanned)

        dt = elapsed_per_row / samples_per_row
        fs = 1.0 / dt
        return dt, fs

    def in_range(self, t0, t1):
        """Return the file paths whose date falls within ``[t0, t1]``, ordered."""
        return [p for (when, p) in self.files if t0 <= when <= t1]

    def parse_date(self, filename):
        """Parse ``YYYYMMDDHHMMSS`` from a file name into a datetime."""
        stem = os.path.splitext(os.path.basename(filename))[0]
        try:
            return datetime.strptime(stem, "%Y%m%d%H%M%S")
        except ValueError:
            warnings.warn("H5Index: skipping malformed file name %r" % filename)
            return None
