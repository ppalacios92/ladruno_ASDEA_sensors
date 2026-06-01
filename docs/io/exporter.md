# Exporter

`io/exporter.py`

Write analysis results to a self-describing `.h5` file.

## What to implement

- **`export_dataset(dataset, path, analyses, components)`**: write the
  Provenance block, then loop over the dataset's cached results and write each
  one under `/Results/<device>/<analysis>` as datasets, with all its parameters
  stored as group attributes. `analyses=None` exports everything cached.
- **`export_device(handle, path, analyses, components)`**: the same for a
  single sensor (called by `DeviceHandle.export_h5`).

## Layout

```
/Provenance         (see provenance.md)
/Results/<device>/<analysis>
    datasets        T, PSa, IA_percent, freqs, H, ...
    .attrs          zeta, max_period, nperseg, bands, factor, basis, ...
```

## Inputs / outputs

- In: a `SensorDataset` or `DeviceHandle`, output `path`, optional `analyses`
  filter, `components`.
- Out: the written path.

## Note

Store the parameters of each result as attributes next to its data, so a reader
knows exactly how that array was computed.
