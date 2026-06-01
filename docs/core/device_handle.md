# DeviceHandle

`core/device_handle.py`

A thin per-sensor view returned by `ds.MOF00135`. Binds a device id to the
parent dataset and exposes the full analysis API for that single sensor.

## What to implement

1. **`signal`**: use the dataset's `H5Reader` (and `parallel_reader` when the
   window spans many files) to read and concatenate the device's acceleration
   into a `SignalData`. Honour `mode` (ram/lazy/auto) via `core.memory`.
2. **`window` / `get_window`**: resolve the bounds with `window_service` and
   return a new handle carrying that window.
3. **`resample`**: return a new handle resampled to a target `dt`/`fs`.
4. **Analysis methods** (`newmark`, `rotd`, `arias`, `cav`, `housner`,
   `peaks`, `fourier`, `psd`, `stft`, `modal_tracking`, `hvsr`,
   `amplification`): read the signal, build the cache key (device + analysis +
   params + signal state), return the cached value if present, otherwise call
   the matching `seismic` / `structural` / `ambient` routine and cache it.
5. **`component="all"`**: run the analysis for x, y, z and return a dict per
   axis.

## Caching

Every result is stored in the parent dataset's `ResultCache`. The key includes
the signal state so a re-filtered or re-windowed signal recomputes
automatically.

## Inputs

Each method's parameters are in its docstring; the analysis defaults match the
ported routines.
