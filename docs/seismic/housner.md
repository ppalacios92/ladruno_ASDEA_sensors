# Housner

`seismic/housner.py`

Housner spectral intensity (SI).

## What to implement

**`compute(acc, dt, T1, T2, zeta)`**: compute the pseudo-velocity spectrum
(`PSv`, via Newmark) and integrate it between `T1` and `T2`.

## Inputs / outputs

- In: `acc` (m/s^2), `dt`, `T1=0.1`, `T2=2.5`, `zeta=0.05`.
- Out: dict with `SI`.

## Why

Summarizes how severe a record is for structures: it integrates over the
period range where most buildings respond.
