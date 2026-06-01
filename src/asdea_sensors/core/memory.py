"""Memory helpers: decide between RAM and lazy reading, and report RAM usage.

Mirrors the large-file awareness pattern: estimate how much memory a read
would take and compare it against the available RAM (psutil).
"""


def estimate_bytes(n_samples, n_components=3, dtype_size=8):
    """Estimate the memory of a signal read, in bytes."""
    raise NotImplementedError


def is_large(n_bytes, ram_fraction=0.5):
    """Return True when ``n_bytes`` exceeds ``ram_fraction`` of the free RAM."""
    raise NotImplementedError


def ram_status():
    """Return ``(used, available, percent)`` from psutil."""
    raise NotImplementedError
