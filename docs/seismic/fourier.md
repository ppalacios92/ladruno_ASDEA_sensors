# Fourier

`seismic/fourier.py`

One-sided FFT amplitude spectrum and dominant frequencies.

## What to implement

**`compute(acc, dt, num_frequencies, prominence, distance_frac, smooth,
bexp)`**: one-sided FFT power spectrum, then `find_peaks` with the given
`prominence` and a minimum spacing of `distance_frac * len`, sorted by
amplitude to return the top `num_frequencies` peaks (frequency, period,
amplitude). When `smooth="konno"`, smooth the spectrum first with
`ambient.konno_ohmachi`.

## Inputs / outputs

- In: `acc` (m/s^2), `dt`, `num_frequencies=4`, `prominence=1e-6`,
  `distance_frac=0.02`, `smooth=None`, `bexp=40`.
- Out: dict with `freqs, spectrum, dom_freqs, dom_periods, dom_peaks`.

## Source

Port from `EarthquakeSignal` `FourierAnalyzer.compute`.
