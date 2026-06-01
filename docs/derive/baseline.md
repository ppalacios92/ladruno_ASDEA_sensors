# Baseline correction

`derive/baseline.py`

Removes baseline drift from an acceleration record.

## What to implement

**`baseline_correct(acc, dt, method)`**: for `"polynomial"`, integrate the
acceleration to velocity and displacement, fit the polynomial drift
coefficients and subtract the drift from the acceleration; return the corrected
acceleration. `"linear"` and `"mean"` are simpler fallbacks.

## Inputs / outputs

- In: `acc` (m/s^2), `dt` (s), `method`.
- Out: corrected `acc` (m/s^2).

## Source

Port from `EarthquakeSignal` `BaselineCorrection.apply` (keep the corrected
acceleration; the velocity/displacement it computes internally are just the
mechanism, the package integrates separately in `derive.integrate`).
