# Interstory drift

`structural/interstory_drift.py`

Relative displacement between two floors, and the drift ratio.

## What to implement

**`compute(disp_upper, disp_lower, dt, story_height)`**: subtract the lower
floor displacement from the upper floor displacement, divide by
`story_height` for the ratio, and report the maxima.

## Inputs / outputs

- In: `disp_upper`, `disp_lower` (m), `dt`, `story_height=3.0`.
- Out: dict with `time, drift, max_drift, max_ratio`.

## Notes

Both inputs are displacements, so the signals must be derived
(`SignalData.derive`) first.
