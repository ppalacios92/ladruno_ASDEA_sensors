# FFT windows

`ambient/fft_windows.py`

Per-window FFT.

## What to implement

**`compute(fs, windows, apply_filter, f1, f2)`**: for each window, detrend,
optionally band-pass (off by default), remove the mean, and take the one-sided
FFT. Return the frequency axis, the complex spectrum and its magnitude as
matrices.

## Inputs / outputs

- In: `fs`, `windows` `(n_samples, n_windows)`, `apply_filter=False`,
  `f1=0.1`, `f2=25.0`.
- Out: `(freqs, complex_spectrum, magnitude)`.

## Notes

Filtering is off by default here: the signal is expected to be filtered
upstream with `SignalData.filter`.

## Source

Port from `AmbientSoilPeriod` `fft_vent`.
