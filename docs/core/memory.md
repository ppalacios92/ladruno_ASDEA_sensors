# Memory helpers

`core/memory.py`

Decides between RAM and lazy reading, and reports RAM usage.

## What to implement

1. **`estimate_bytes`**: bytes for `n_samples * n_components * dtype_size`.
2. **`is_large`**: compare against `ram_fraction` of the available RAM
   (`psutil.virtual_memory().available`).
3. **`ram_status`**: return `(used, available, percent)` from psutil, for the
   summary block.

## Notes

Used by `SensorDataset` (load mode and summary) and `DeviceHandle.signal`
(ram vs lazy auto decision).
