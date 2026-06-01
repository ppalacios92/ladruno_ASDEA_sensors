# Integrate

`derive/integrate.py`

Integrates acceleration to velocity and displacement.

## What to implement

- **`to_velocity(acc, dt, remove_mean)`**: cumulative trapezoidal integration
  of acceleration (m/s^2) to velocity (m/s).
- **`to_displacement(vel, dt, remove_mean)`**: same, velocity to displacement.
- **`derive(acc, dt, remove_mean)`**: run both, return `(vel, disp)`.

`remove_mean` subtracts the mean before each integration to limit the drift
that integration amplifies.

## Inputs / outputs

- In: `acc` (m/s^2), `dt` (s), `remove_mean`.
- Out: `vel` (m/s), `disp` (m).

## Notes

Use `scipy.integrate.cumulative_trapezoid` (prepend 0 to keep the length).
