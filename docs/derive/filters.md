# Filters

`derive/filters.py`

Band-pass filtering of acceleration, with two engines.

## What to implement

**`bandpass(acc, dt, fmin, fmax, engine, order, zerophase)`**:

- `engine="obspy"`: wrap the array in an `obspy.Trace`, set `delta = dt`, call
  `tr.filter("bandpass", freqmin=fmin, freqmax=fmax, corners=order,
  zerophase=zerophase)`.
- `engine="scipy"`: `butter(order, [fmin, fmax] / nyquist, "band")` then
  `filtfilt` (or `lfilter` when `zerophase=False`).

Clip `fmax` just below Nyquist and warn if it exceeds it.

## Inputs / outputs

- In: `acc`, `dt`, `fmin`, `fmax`, `engine`, `order`, `zerophase`.
- Out: filtered array.

## Source

The ObsPy path matches the project's `bandpass` snippet; the SciPy path matches
`EarthquakeSignal` `BaselineCorrection.bandpass_filter`.
