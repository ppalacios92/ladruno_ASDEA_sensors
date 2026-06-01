# Arias

`seismic/arias.py`

Arias intensity curve and significant duration.

## What to implement

**`compute(acc, dt, low, high)`**: Arias intensity
`IA = (pi / 2g) * cumsum(acc^2) * dt`, normalize to percent, find the times at
`low`% and `high`% for the significant duration, and compute the
destructiveness potential from the zero-crossing rate.

## Inputs / outputs

- In: `acc` (m/s^2), `dt`, `low=5`, `high=95`.
- Out: dict with `IA_percent, t_start, t_end, IA_total, pot_dest`.

## Source

Port from `EarthquakeSignal` `AriasIntensityAnalyzer.compute`.
