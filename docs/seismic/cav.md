# CAV

`seismic/cav.py`

Cumulative Absolute Velocity.

## What to implement

**`compute(acc, dt)`**: cumulative integral of `|acc|` over time. Return the
total CAV and the cumulative curve.

## Inputs / outputs

- In: `acc` (m/s^2), `dt`.
- Out: dict with `CAV` (total), `curve` (cumulative in time).

## Why

Measures accumulated energy / damage potential, beyond the simple peak. A
standard threshold parameter in seismic practice.
