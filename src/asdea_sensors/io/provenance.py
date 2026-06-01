"""Provenance: the traceability block written into every results .h5.

Provenance records where a result came from and how it was produced, so it can
be reproduced exactly: the input files, the processing pipeline applied to the
signal, the parameters of each analysis, the units, the code version, the date,
and a full copy + hash of the configuration.
"""


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
    raise NotImplementedError


def config_hash(config):
    """Return a stable hash of the configuration, for reproducibility checks."""
    raise NotImplementedError


def write(group, provenance):
    """Write the provenance dict into an HDF5 group as datasets/attrs."""
    raise NotImplementedError
