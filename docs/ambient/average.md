# Average

`ambient/average.py`

Average spectrum across windows.

## What to implement

**`compute(spectra)`**: mean of the per-window spectrum matrix along the window
axis, returning a single `(n_freqs,)` spectrum.

## Inputs / outputs

- In: `spectra` `(n_freqs, n_windows)`.
- Out: mean spectrum `(n_freqs,)`.

## Source

Port from `AmbientSoilPeriod` `prom_vent`.
