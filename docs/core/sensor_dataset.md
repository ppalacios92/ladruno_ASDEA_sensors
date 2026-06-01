# SensorDataset

`core/sensor_dataset.py`

The main object and entry point. Built from a folder path; cheap to
instantiate because it only reads the file index and metadata.

## What to implement

1. **Constructor**: build an `H5Index` over `path`, store `devices`, `fs`,
   `dt`, `time_span`, resolve `axes_map` (argument or `config.SENSOR_AXES`),
   create the `ResultCache`, and print the summary block when `verbose`.
2. **`__getattr__`**: when the attribute is a known device id, return its
   `DeviceHandle`. Otherwise raise `AttributeError` (so normal attributes keep
   working).
3. **`device(name)`**: explicit form of the above.
4. **Broadcast methods** (`newmark`, `rotd`, `arias`, `fourier`, `psd`,
   `peaks`): run the per-sensor version over every device through the
   `BatchEngine` and return a dict keyed by device.
5. **Structural methods** (`transfer_function`, `coherence`,
   `interstory_drift`, `amplification`): read the needed sensors and delegate
   to the `structural` / `ambient` modules.
6. **`resample`**: return a new dataset resampled to a target `dt`/`fs`.
7. **`sweep`**: split the span into fixed blocks and run the requested
   analyses on each, in parallel.
8. **Cache helpers**: `summary`, `cache_summary`, `clear_cache`.

## Summary block

Print files count, time span, devices, `fs`/`dt` (measured from Timestamp),
the per-sensor axis mapping, on-disk size and RAM status. ASCII only (use
`'-' * 60`), no box characters.

## Inputs

See the constructor docstring for every parameter (`path`, `pattern`,
`date_source`, `devices`, `load_mode`, `ram_fraction`, `axes_map`, `verbose`)
and the control properties `n_jobs` / `parallel`.

## Notes

Mirror the lazy, cached, import-deferred style: keep heavy imports inside the
methods, never read signal data in the constructor.
