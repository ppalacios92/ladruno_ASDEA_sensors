"""H5Index: scan a folder once, parse each file's date and detect the devices,
sampling rate and time span. Built once at construction; queried many times.
"""


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
        raise NotImplementedError

    def in_range(self, t0, t1):
        """Return the file paths whose date falls within ``[t0, t1]``, ordered."""
        raise NotImplementedError

    def parse_date(self, filename):
        """Parse ``YYYYMMDDHHMMSS`` from a file name into a datetime."""
        raise NotImplementedError
