# Results file

`io/results_file.py`

Read a results `.h5` written by the exporter.

## What to implement

**`ResultsFile(path)`**:

- Constructor: open the file, load the `Provenance` block into `provenance`,
  list the devices under `/Results`.
- **`analyses(device)`**: list the analyses stored for a device.
- **`get(device, analysis)`**: return `(data, params)` for one result, where
  `data` is the datasets and `params` the stored attributes.

## Inputs / outputs

- In: `path` to a results file.
- Out: easy access to each result, its parameters and the provenance.

## Why

Lets you reopen a saved analysis, inspect exactly how it was computed, and
reproduce it from the stored config.
