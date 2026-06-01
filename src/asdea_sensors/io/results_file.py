"""ResultsFile: read a results .h5 written by the exporter.

Gives easy access to each stored result and to its parameters and provenance,
so a saved analysis can be inspected and reproduced.
"""

import json

import h5py
import numpy as np


def _decode(value):
    """Turn an HDF5 attribute back into a plain Python value.

    Bytes become str, numpy scalars become Python scalars, and strings that
    hold JSON (config, input_files, pipeline, list/dict params) are parsed
    back into their original structure.
    """
    if isinstance(value, bytes):
        value = value.decode("utf-8")
    if isinstance(value, np.generic):
        value = value.item()
    if isinstance(value, str):
        stripped = value.strip()
        if stripped[:1] in ("{", "[") or stripped in ("true", "false", "null"):
            try:
                return json.loads(stripped)
            except (ValueError, TypeError):
                return value
    return value


class ResultsFile:
    """Reader for a results .h5 file.

    Parameters
    ----------
    path : str
        Path to a results file written by ``io.exporter``.

    Attributes
    ----------
    provenance : dict
        The Provenance block (input files, pipeline, params, config, ...).
    devices : list of str
        Devices present in the file.
    """

    def __init__(self, path):
        self.path = path
        self.provenance = None
        self.devices = []

        with h5py.File(path, "r") as f:
            self.provenance = {}
            if "Provenance" in f:
                for key, value in f["Provenance"].attrs.items():
                    self.provenance[key] = _decode(value)

            if "Results" in f:
                self.devices = sorted(f["Results"].keys())

    def analyses(self, device):
        """List the analyses stored for a device."""
        with h5py.File(self.path, "r") as f:
            group = f.get("Results/%s" % device)
            if group is None:
                return []
            return sorted(group.keys())

    def get(self, device, analysis):
        """Return ``(data, params)`` for one stored result."""
        data = {}
        params = {}
        with h5py.File(self.path, "r") as f:
            group = f.get("Results/%s/%s" % (device, analysis))
            if group is None:
                return data, params
            for key, value in group.attrs.items():
                params[key] = _decode(value)
            for name, item in group.items():
                if isinstance(item, h5py.Dataset):
                    data[name] = item[()]
        return data, params
