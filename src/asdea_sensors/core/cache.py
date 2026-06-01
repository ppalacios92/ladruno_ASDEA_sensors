"""Result cache: store per-sensor analysis results on the dataset.

The key includes the device, the analysis name, its parameters and the state
of the source signal, so a stale result is never returned: if anything
upstream changed, the key changes and the analysis runs again. No manual
``recompute`` flag is needed.
"""


class ResultCache:
    """Dictionary-backed cache with automatic-invalidation keys and RAM reporting."""

    def __init__(self):
        self._store = {}

    def key(self, device, analysis, params, signal_state):
        """Build a cache key from the inputs that affect the result.

        Parameters
        ----------
        device : str
        analysis : str
            Analysis name, e.g. "newmark".
        params : dict
            The analysis parameters.
        signal_state : hashable
            A fingerprint of the source signal (window, processing steps, dt).
        """
        raise NotImplementedError

    def get(self, key):
        """Return the cached value for ``key`` or ``None`` if absent."""
        raise NotImplementedError

    def set(self, key, value):
        """Store ``value`` under ``key``."""
        raise NotImplementedError

    def clear(self):
        """Drop every entry."""
        raise NotImplementedError

    def ram_bytes(self):
        """Approximate the RAM used by the cached results, in bytes."""
        raise NotImplementedError
