"""Exporter: write analysis results to a self-describing .h5 file.

Layout::

    /Provenance
        input_files, pipeline, units, fs, dt, version, created_on,
        config, config_hash
    /Results/<device>/<analysis>
        <datasets>          e.g. T, PSa, IA_percent, freqs, H, ...
        .attrs              all parameters of that result (zeta, nperseg, ...)

Available at two levels: a whole-dataset export and a per-sensor export
(through the device chain).
"""

import json

import h5py
import numpy as np

from asdea_sensors.io import provenance as _provenance


def _key_device(key):
    """Return the device id from a cache key, or None if not recognizable."""
    if isinstance(key, (tuple, list)) and len(key) >= 1:
        return key[0]
    return None


def _key_analysis(key):
    """Return the analysis name from a cache key, or None."""
    if isinstance(key, (tuple, list)) and len(key) >= 2:
        return key[1]
    return None


def _key_params(key):
    """Recover the parameter dict frozen into a cache key.

    The cache freezes params as a tuple of (name, value) pairs (see
    ``core.cache._freeze``). This unfreezes the top level back to a dict for
    storage as attributes. Anything that does not look like params is ignored.
    """
    if not isinstance(key, (tuple, list)) or len(key) < 3:
        return {}
    frozen = key[2]
    params = {}
    if isinstance(frozen, (tuple, list)):
        for item in frozen:
            if isinstance(item, (tuple, list)) and len(item) == 2:
                name, value = item
                params[str(name)] = value
    return params


def _attr_value(value):
    """Convert a parameter value into something HDF5 attrs accept."""
    if isinstance(value, (str, int, float, bool, np.integer, np.floating)):
        return value
    if isinstance(value, np.ndarray) and value.ndim == 0:
        return value.item()
    # Tuples, lists, dicts and other structures go in as JSON strings.
    return json.dumps(value, default=str)


def _is_array_like(value):
    """True if the value can be stored as an HDF5 dataset."""
    if isinstance(value, np.ndarray):
        return True
    if isinstance(value, (list, tuple)):
        try:
            arr = np.asarray(value)
        except Exception:
            return False
        return arr.dtype != np.object_
    return False


def _write_result(group, value, params):
    """Write one cached result (dict-of-arrays or array) into ``group``.

    Parameters are stored as attributes. Array-like entries become datasets;
    scalar entries of a dict value are added as attributes; anything that is
    neither is skipped gracefully.
    """
    # Store the recovered parameters as attributes.
    for name, pval in params.items():
        try:
            group.attrs[name] = _attr_value(pval)
        except Exception:
            group.attrs[name] = str(pval)

    if isinstance(value, dict):
        for name, item in value.items():
            dname = str(name)
            if _is_array_like(item):
                group.create_dataset(dname, data=np.asarray(item))
            elif isinstance(item, (str, int, float, bool,
                                   np.integer, np.floating)):
                group.attrs[dname] = item
            else:
                # Non-array, non-scalar (e.g. nested dict): keep as JSON attr.
                try:
                    group.attrs[dname] = json.dumps(item, default=str)
                except Exception:
                    pass
    elif _is_array_like(value):
        group.create_dataset("data", data=np.asarray(value))
    # Anything else is skipped: there is nothing array-like to store.


def _export(dataset, cache, path):
    """Write provenance and every cache entry into a fresh .h5 at ``path``."""
    with h5py.File(path, "w") as f:
        prov_group = f.create_group("Provenance")
        prov = _provenance.build(dataset)
        _provenance.write(prov_group, prov)

        results = f.create_group("Results")
        for key, value in cache.items():
            device = _key_device(key)
            analysis = _key_analysis(key)
            if device is None or analysis is None:
                continue

            dev_group = results.require_group(str(device))
            name = str(analysis)
            # Avoid collisions when the same analysis is cached with different
            # parameters: suffix duplicates so neither is lost.
            target = name
            suffix = 1
            while target in dev_group:
                suffix += 1
                target = "%s_%d" % (name, suffix)

            res_group = dev_group.create_group(target)
            _write_result(res_group, value, _key_params(key))

    return path


def export_dataset(dataset, path, analyses=None, components="all"):
    """Export every cached result of the dataset to one .h5 file.

    Parameters
    ----------
    dataset : SensorDataset
        Source dataset (provides the results cache and the provenance).
    path : str
        Output .h5 path.
    analyses : list of str or None
        Restrict to these analyses. ``None`` exports everything cached.
    components : {"x", "y", "z", "all"}, default "all"

    Returns
    -------
    str
        The written path.
    """
    cache = getattr(dataset, "_cache", None) or {}
    selected = {}
    for key, value in cache.items():
        if analyses is not None and _key_analysis(key) not in analyses:
            continue
        selected[key] = value
    return _export(dataset, selected, path)


def export_device(handle, path, analyses=None, components="all"):
    """Export one sensor's results to a .h5 file (used by the device chain).

    Parameters
    ----------
    handle : DeviceHandle
        The per-sensor view to export.
    path : str
        Output .h5 path.
    analyses : list of str or None
    components : {"x", "y", "z", "all"}, default "all"

    Returns
    -------
    str
        The written path.
    """
    dataset = getattr(handle, "dataset", None)
    device = getattr(handle, "device", None)
    cache = getattr(dataset, "_cache", None) or {}

    selected = {}
    for key, value in cache.items():
        if _key_device(key) != device:
            continue
        if analyses is not None and _key_analysis(key) not in analyses:
            continue
        selected[key] = value
    return _export(dataset, selected, path)
