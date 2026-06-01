# Resample service

`core/resample_service.py`

Changes the sampling rate of a signal, a sensor or the whole dataset. Useful
to standardize `dt` before any analysis.

## What to implement

1. **`target_dt`**: resolve a target dt from either `dt` or `fs` (exactly one
   provided).
2. **`resample_signal`**: resample one array from `dt_in` to the target rate.
   Use a polyphase resampler (`scipy.signal.resample_poly`) for rational
   ratios, or interpolation otherwise.

## Notes

`SignalData.resample`, `DeviceHandle.resample` and `SensorDataset.resample`
all delegate here; the dataset version applies it to every sensor.
