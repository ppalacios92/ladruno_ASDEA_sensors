# Provenance

`io/provenance.py`

The traceability block written into every results `.h5`. It records where a
result came from and how it was produced, so it can be reproduced exactly.

## What to implement

- **`build(dataset, signal_state)`**: assemble the dict with `input_files`
  (the source `.h5` paths), `pipeline` (the processing steps applied to the
  signal, e.g. `"baseline -> filter(0.1,24.9) -> derive"`), `units`, `fs`,
  `dt`, `version`, `created_on`, a full `config` copy and its `config_hash`.
- **`config_hash(config)`**: a stable hash (e.g. of the JSON-serialized config)
  for reproducibility checks.
- **`write(group, provenance)`**: write the dict into an HDF5 group, scalars as
  attributes and arrays/lists as datasets.

## Why

Without provenance you have a spectrum but not the filter, window or parameters
behind it. With it, the result is self-describing and replicable: that was the
explicit requirement.

## Note

`created_on` must be passed in (the date is an input), not read from the clock,
to keep exports deterministic when reproduced.
