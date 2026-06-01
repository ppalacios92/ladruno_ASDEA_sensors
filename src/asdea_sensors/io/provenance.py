"""Provenance: the traceability block written into every results .h5.

Provenance records where a result came from and how it was produced, so it can
be reproduced exactly: the input files, the processing pipeline applied to the
signal, the parameters of each analysis, the units, the code version, the date,
and a full copy + hash of the configuration.
"""

import hashlib
import json

import numpy as np

from asdea_sensors import __version__
from asdea_sensors.config import settings


# Public configuration values copied into every export. Names that are not
# defined in the settings module are skipped, so this list can stay ahead of
# the config without breaking.
_CONFIG_KEYS = (
    "SENSOR_AXES",
    "SENSOR_GEOMETRY",
    "GRAVITY",
    "PSD",
    "AMBIENT",
    "FLOOR_TITLES",
)


def _input_files(dataset):
    """Collect the source .h5 paths from the dataset's file index."""
    index = getattr(dataset, "_index", None) or getattr(dataset, "index", None)
    entries = None
    if index is not None:
        entries = getattr(index, "files", None)
    if entries is None:
        entries = getattr(dataset, "files", None)
    if not entries:
        return []

    files = []
    for entry in entries:
        # The index stores (datetime, path) tuples; tolerate a bare path too.
        if isinstance(entry, (tuple, list)) and len(entry) >= 2:
            files.append(str(entry[1]))
        else:
            files.append(str(entry))
    return files


def _collect_config():
    """Build a serializable copy of the public config values."""
    config = {}
    for key in _CONFIG_KEYS:
        if hasattr(settings, key):
            config[key] = getattr(settings, key)
    # Round-trip through JSON so the stored copy is plain serializable data
    # (tuples become lists, etc.) and matches what config_hash sees.
    return json.loads(json.dumps(config, default=str))


def build(dataset, signal_state=None):
    """Build the provenance dictionary for a dataset / signal.

    Parameters
    ----------
    dataset : SensorDataset
        Source dataset (input files, fs, dt, devices, axes).
    signal_state : dict or None
        Processing pipeline applied to the signal (e.g. baseline, filter,
        derive, resample) with their parameters.

    Returns
    -------
    dict
        Keys: input_files, pipeline, units, fs, dt, version, created_on,
        config (full copy), config_hash.
    """
    config = _collect_config()

    created_on = getattr(dataset, "created_on", None)
    if created_on is None:
        created_on = ""

    provenance = {
        "input_files": _input_files(dataset),
        "pipeline": signal_state if signal_state is not None else "",
        "units": "SI",
        "fs": getattr(dataset, "fs", None),
        "dt": getattr(dataset, "dt", None),
        "version": __version__,
        "created_on": created_on,
        "config": config,
        "config_hash": config_hash(config),
    }
    return provenance


def config_hash(config):
    """Return a stable hash of the configuration, for reproducibility checks."""
    payload = json.dumps(config, sort_keys=True, default=str)
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def write(group, provenance):
    """Write the provenance dict into an HDF5 group as datasets/attrs."""
    for key, value in provenance.items():
        if value is None:
            group.attrs[key] = ""
        elif isinstance(value, (str, int, float, bool, np.integer, np.floating)):
            group.attrs[key] = value
        elif isinstance(value, (dict, list, tuple)):
            # Structured values (config, input_files, pipeline dict) are stored
            # as JSON strings so they survive a round-trip without losing keys.
            group.attrs[key] = json.dumps(value, default=str)
        else:
            group.attrs[key] = str(value)
