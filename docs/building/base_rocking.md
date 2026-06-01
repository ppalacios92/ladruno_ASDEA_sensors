# Base rocking

`building/base_rocking.py`

Rotation (rocking) of the foundation, to assess soil-foundation flexibility.

## What to implement

**`compute(acc_vertical, dt, base_width, acc_vertical_b)`**: when two vertical
base measurements are available, the rocking angle is their difference divided
by the plan separation `base_width`; with a single base sensor, characterize
the low-frequency vertical content. Return the rocking history, its spectrum
and the rocking frequency.

## Inputs / outputs

- In: vertical acceleration at the base (MOF00134), `dt`, optional second base
  point and `base_width`.
- Out: dict with `rocking, spectrum, rocking_freq`.

## Why

Rocking indicates how much the structure rotates on a flexible soil, which
shifts the apparent modal frequencies of the building.
