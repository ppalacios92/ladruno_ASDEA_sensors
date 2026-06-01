"""Parallel reader: read slices from many .h5 files concurrently.

Used when a window spans many files. Each file slice is read on a worker
thread (I/O bound), then the slices are concatenated in order.
"""


def read_slices(reader, files, device, workers=4):
    """Read ``device`` from each file in ``files`` using a thread pool.

    Parameters
    ----------
    reader : H5Reader
        Reader used for a single file.
    files : list of str
        Ordered file paths.
    device : str
    workers : int, default 4
        Number of worker threads.

    Returns
    -------
    list
        Per-file results in the same order as ``files``.
    """
    raise NotImplementedError
