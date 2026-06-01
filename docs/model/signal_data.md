# SignalData

`model/signal_data.py`

Lightweight container for one device's continuous signal: acceleration (and,
once derived, velocity and displacement) plus the time base. The processing
steps are decoupled and chainable.

## What to implement

1. **Properties**: `fs` (`1/dt`), `n` (sample count), `duration`.
2. **`baseline`**: call `derive.baseline.baseline_correct` on each selected
   component, return a new `SignalData` with corrected acceleration. Nothing
   else (no filtering, no integration).
3. **`filter`**: call `derive.filters.bandpass` on each selected component,
   return a new `SignalData`.
4. **`derive`**: call `derive.integrate.derive` to fill `vel_*` and `disp_*`
   from the current acceleration, return a new `SignalData`.
5. **`resample`**: delegate to `core.resample_service`.
6. **`component`**: return the acceleration array for "x", "y" or "z".
7. **`ambient`**: return an `AmbientAnalysis` bound to the chosen component.

## Design

Each step returns a **new** `SignalData` so the order is the caller's choice:

```python
sig.baseline().filter(0.1, 24.9).derive()
```

Keep them orthogonal: baseline corrects acceleration only, filter band-passes
only, derive integrates only.

## Units

SI throughout: acceleration `m/s^2`, velocity `m/s`, displacement `m`.
