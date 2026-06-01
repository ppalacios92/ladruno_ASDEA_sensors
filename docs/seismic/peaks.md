# Peaks

`seismic/peaks.py`

Peak ground values: PGA, PGV, PGD.

## What to implement

**`compute(acc, vel, disp)`**: return `max(|acc|)`, `max(|vel|)`,
`max(|disp|)`. Velocity and displacement come from the derived signal, so the
caller must integrate first.

## Inputs / outputs

- In: `acc` (m/s^2), `vel` (m/s), `disp` (m).
- Out: dict with `PGA, PGV, PGD`.
