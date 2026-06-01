# Modal tracking

`structural/modal_tracking.py`

Tracks modal frequencies over time (structural health monitoring).

## What to implement

**`compute(acc, dt, window, overlap, fband, n_modes, smooth, bexp)`**: slide a
moving window of length `window` (overlap `overlap`) over the record; in each
window compute the spectrum, optionally Konno-Ohmachi smooth it, pick the top
`n_modes` peaks inside `fband`, and record their frequencies. Return the window
times and a `(n_windows, n_modes)` frequency array.

## Inputs / outputs

- In: `acc` (m/s^2), `dt`, `window="10min"`, `overlap=0.5`, `fband=(1.0, 8.0)`,
  `n_modes=2`, `smooth="konno"`, `bexp=40`.
- Out: dict with `t, freqs`.

## Why

A sustained drop of a modal frequency over hours/days flags a stiffness loss.
