# Taper

`ambient/taper.py`

Tukey taper for windowed signals.

## What to implement

**`compute(windows, p)`**: build a Tukey window of `alpha=p` the length of the
windows and multiply each column by it. Return the tapered matrix and the taper.

## Inputs / outputs

- In: `windows` `(n_samples, n_windows)`, `p` (Tukey alpha).
- Out: `(tapered_windows, taper)`.

## Source

Port from `AmbientSoilPeriod` `taper_function`.
