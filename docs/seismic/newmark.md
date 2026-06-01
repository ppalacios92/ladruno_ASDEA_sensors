# Newmark

`seismic/newmark.py`

Response spectrum of a SDOF system by the linear-acceleration (beta) method.

## What to implement

**`compute(acc, dt, zeta, max_period, dT, factor)`**: for each period in
`arange(0, max_period, dT)`, solve the SDOF response (`@njit` inner loop) and
collect `Sd, Sv, Sa, PSv, PSa` plus the time histories `u, v, a, at` at
`T = 1 s`. Apply `factor` to the acceleration spectra (`PSa`, `Sa`) only.

## Inputs / outputs

- In: `acc` (m/s^2), `dt`, `zeta=0.05`, `max_period=5.01`, `dT=0.01`,
  `factor=1.0` (use `1/9.81` to present in g).
- Out: dict with `T, PSa, PSv, Sd, Sv, Sa, u, v, a, at`.

## Source

Port from `EarthquakeSignal` `NewmarkSpectrumAnalyzer.compute` (with the
`solve_newmark` numba kernel). Keep the full output; the package always returns
every quantity.
