# Drift

`building/drift.py`

Interstory drift and drift profile over the height of the building.

## What to implement

- **`interstory_drift(disp_upper, disp_lower, story_height)`**: relative
  displacement `disp_upper - disp_lower`, drift ratio `/ story_height`, with the
  maxima.
- **`drift_profile(disps_by_floor, heights)`**: assemble the per-story drift
  ratios along the vertical array, ordered by height.
- **`story_envelope(disps_by_floor, heights, quantity)`**: the per-floor
  maximum of `drift`, `disp` or `accel` over the record.

## Inputs / outputs

- In: displacements per floor (so the signals must be derived first), the floor
  heights (from `geometry.heights`).
- Out: drift time history and ratio, the profile over height, the envelopes.

## Why

Interstory drift is the key structural demand parameter; the profile shows
where the demand concentrates over the height.
