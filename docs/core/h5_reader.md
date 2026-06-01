# H5Reader

`core/h5_reader.py`

Reads the acceleration of one device from one or many `.h5` files and
concatenates it into a continuous signal.

## HDF5 layout

```
Devices/<id>/Acceleration   (N, 3)  float32   raw, in g
Devices/<id>/Timestamp      (M, 4)  uint64    [unix_s, nanos, counter, 0]
```

## What to implement

1. **`read_one`**: open a file, read `Devices/<device>/Acceleration`, select
   the columns given by `axes_map[device]` as X, Y, Z, convert g -> m/s^2
   (multiply by `config.GRAVITY`) when `to_si`.
2. **`read`**: read each file in `files` in order (optionally via
   `parallel_reader`), concatenate, rebuild the continuous time vector,
   optionally remove the mean. Return `{"acc", "time", "dt", "axes"}`.
3. **`dt_from_timestamp`**: estimate dt/fs from the `Timestamp` dataset.

## Axis mapping (important)

The sensors were installed in a non-standard orientation, so each device uses
its own column mapping (`config.SENSOR_AXES`), e.g. `MOF00134 -> (0,1,2)` and
the rest `-> (3,1,5)`. Keep this mapping; do not normalize it. The current
files only have 3 columns in `Acceleration`, so a mapping with an index above 2
must be reconciled with the original `readH5File` (to be ported from kraken).

## Source

Wraps the original `readH5File` routine.
