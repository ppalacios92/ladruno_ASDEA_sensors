# Window selector

`ambient/window_selector.py`

Automatic selection of stationary windows by STA/LTA.

## What to implement

**`compute(fs, time, signal, ratio, vent, vmin, vmax)`**: split the signal
into windows of length `vent`; keep a window only if all of its STA/LTA samples
fall inside `(vmin, vmax)`. Return the time and signal matrices of the kept
windows plus their positions and ids.

## Inputs / outputs

- In: `fs`, `time`, `signal`, `ratio` (STA/LTA), `vent` (s), `vmin`, `vmax`.
- Out: `(MT, MV, positions, win_ids)`.

## Source

Port from `AmbientSoilPeriod` `window_selector`.
