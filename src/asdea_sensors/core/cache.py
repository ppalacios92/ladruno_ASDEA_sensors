"""Result cache: store per-sensor analysis results on the dataset.

The key includes the device, the analysis name, its parameters and the state
of the source signal, so a stale result is never returned: if anything
upstream changed, the key changes and the analysis runs again. No manual
``recompute`` flag is needed.
"""

import numpy as np


def _freeze(value):
    """Turn a value into a hashable, order-stable form."""
    if isinstance(value, dict):
        return tuple(sorted((k, _freeze(v)) for k, v in value.items()))
    if isinstance(value, (list, tuple)):
        return tuple(_freeze(v) for v in value)
    if isinstance(value, set):
        return tuple(sorted(_freeze(v) for v in value))
    return value


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
        return (device, analysis, _freeze(params or {}), _freeze(signal_state))

    def get(self, key):
        """Return the cached value for ``key`` or ``None`` if absent."""
        return self._store.get(key)

    def set(self, key, value):
        """Store ``value`` under ``key``."""
        self._store[key] = value

    def clear(self):
        """Drop every entry."""
        self._store.clear()

    def ram_bytes(self):
        """Approximate the RAM used by the cached results, in bytes."""
        total = 0
        for value in self._store.values():
            total += _value_bytes(value)
        return total


def _value_bytes(value):
    """Sum the nbytes of numpy arrays found in a cached value."""
    if isinstance(value, np.ndarray):
        return value.nbytes
    if isinstance(value, dict):
        return sum(_value_bytes(v) for v in value.values())
    if isinstance(value, (list, tuple, set)):
        return sum(_value_bytes(v) for v in value)
    return 0
