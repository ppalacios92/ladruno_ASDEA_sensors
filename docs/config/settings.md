# Settings

`config/settings.py`

Single configuration for the whole package. Edit here, not inside the analysis
code.

## Contents

- **`SENSOR_AXES`**: per-device column mapping `{device: (ix, iy, iz)}`. The
  sensors were installed in a non-standard orientation, so most use `(3, 1, 5)`
  and `MOF00134` uses `(0, 1, 2)`. This is printed on every read. Do not change
  it without checking the physical install. Reconcile indices above 2 with the
  ported `readH5File` (the current files only have 3 acceleration columns).
- **`FLOOR_TITLES`**: human-readable floor per device (fill in as known).
- **`GRAVITY`**: 9.81, used to convert raw acceleration from g to m/s^2.
- **`PSD`**: default `NPERSEG`, `NOVERLAP`, `WINDOW`, `FREQ_BANDS`.
- **`AMBIENT`**: default STA/LTA, window, taper, smoothing and FFT-band values.

## Notes

This file holds data, not logic; it is already filled with the known values.
