# Torsion

`building/torsion.py`

Floor torsion from two (or more) sensors on the same level.

## Physics

For a rigid diaphragm a plan point `(x, y)` moves as

```
u_x = U_x - (y - y_c) * theta
u_y = U_y + (x - x_c) * theta
```

so the floor rotation `theta(t)` follows from the difference of the same
horizontal component at two sensors separated in plan.

## What to implement

- **`floor_rotation(sig_a, sig_b, distance, component)`**:
  `theta = (sig_a - sig_b) / distance`, where the two signals are the same
  horizontal component (in the common frame) and `distance` is the plan
  separation perpendicular to that component.
- **`torsional_spectrum(theta, dt, smooth, bexp)`**: spectrum of `theta`, pick
  the peak as the torsional frequency.
- **`torsion_ratio(theta, translation, radius)`**: `theta * radius` over the
  translation, as a measure of torsional severity.
- **`orbit(acc_x, acc_y)`**: the X-Y plan trajectory of a point (use the
  derived displacement for a physical orbit).

## Inputs / outputs

- In: same-direction signals at two floor-4 sensors (MOF00135 + MOF00136),
  their plan `distance` (from `geometry.plan_distance`), `dt`.
- Out: rotation history, torsional spectrum/frequency, torsion ratio, orbit.

## Note

Two sensors give a rotation estimate (rigid-diaphragm assumption). Three
horizontal channels would let you solve `(U_x, U_y, theta)` fully.
