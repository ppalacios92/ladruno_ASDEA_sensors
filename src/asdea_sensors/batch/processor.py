"""Internal batch engine.

Powers the broadcast methods (an analysis over every device) and the time
sweeps. It is not part of the user-facing API: it is driven by the dataset's
``n_jobs`` and ``parallel`` properties.
"""


class BatchEngine:
    """Run a callable over many items, in parallel when enabled.

    Parameters
    ----------
    n_jobs : int, default 4
        Number of parallel jobs (joblib).
    parallel : bool, default True
        Run in parallel; when False, run serially.
    """

    def __init__(self, n_jobs=4, parallel=True):
        self.n_jobs = n_jobs
        self.parallel = parallel

    def map(self, func, items):
        """Apply ``func`` to each item and return the results in order.

        Parameters
        ----------
        func : callable
            Function applied to one item.
        items : iterable
            Items to process (e.g. device ids, or time blocks).
        """
        items = list(items)
        if not items:
            return []

        if self.parallel and self.n_jobs and self.n_jobs != 1:
            # Threads: the work is HDF5 I/O plus numba/numpy that release the
            # GIL, and threads avoid pickling the dataset across processes.
            # Fall back to a serial loop when joblib is not installed.
            try:
                from joblib import Parallel, delayed
            except ImportError:
                return [func(item) for item in items]
            return Parallel(n_jobs=self.n_jobs, prefer="threads")(
                delayed(func)(item) for item in items)

        return [func(item) for item in items]
