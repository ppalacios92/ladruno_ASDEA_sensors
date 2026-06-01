# Konno-Ohmachi

`ambient/konno_ohmachi.py`

Logarithmic-window spectral smoothing.

## What to implement

**`compute(freqs, magnitude, bexp)`**: for each frequency, build the
Konno-Ohmachi weighting `(sin(d)/d)^4` with `d = bexp * log10(f/fc)` over a
log-spaced neighbourhood and take the weighted average. Broadcast a 1-D `freqs`
over all window columns. Use a numba kernel for speed.

## Inputs / outputs

- In: `freqs`, `magnitude` `(n_freqs, n_windows)`, `bexp` (bandwidth).
- Out: smoothed spectrum, same shape.

## Source

Port from `AmbientSoilPeriod` `sua_vent`.
