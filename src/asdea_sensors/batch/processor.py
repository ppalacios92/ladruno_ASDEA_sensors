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
        raise NotImplementedError
