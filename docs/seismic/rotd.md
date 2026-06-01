# RotD

`seismic/rotd.py`

Rotated response-spectra percentiles (ROTD00/50/100).

## What to implement

**`compute(acc_x, acc_y, dt, rotd, damping, angle_step, max_period, dT)`**:
rotate the two horizontals from 0 to 180 degrees in `angle_step` steps,
compute `PSa` at each angle (calls Newmark), stack into a matrix, and take the
`rotd` percentile per period. Also return the geometric mean, arithmetic mean
and SRSS spectra.

## Caching note

Return the full `PSa_matrix` so the caller can cache it: other percentiles
(0/50/100) are just another percentile of the same matrix, no recomputation.

## Inputs / outputs

- In: `acc_x`, `acc_y` (m/s^2), `dt`, `rotd=50`, `damping=0.05`,
  `angle_step=5`, `max_period=5.01`, `dT=0.01`.
- Out: dict with `T, ROTD<rotd>, angle_rotd<rotd>, PSa_matrix,
  PSa_geo_mean, PSa_arith_mean, PSa_SRSS`.

## Source

Port from `EarthquakeSignal` `RotDSpectrumAnalyzer.compute_rotd`.
