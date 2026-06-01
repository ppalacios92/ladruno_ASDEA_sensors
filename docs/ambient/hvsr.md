# HVSR

`ambient/hvsr.py`

Horizontal-to-Vertical Spectral Ratio (Nakamura).

## What to implement

**`compute(signal_h1, signal_h2, signal_v, config, combine)`**: compute the
(windowed, smoothed) spectrum of each component, combine the two horizontals
(`"geometric"` or `"quadratic"`), divide by the vertical spectrum, and pick the
peak as the fundamental frequency `f0`.

## Inputs / outputs

- In: `signal_h1`, `signal_h2`, `signal_v`, `config` (ambient), `combine`.
- Out: dict with `freqs, HV, f0`.

## Notes

Reuses the ambient pipeline (windowing, FFT, Konno-Ohmachi) per component.
