# STFT

`seismic/stft.py`

Short-time Fourier transform (spectrogram).

## What to implement

**`compute(acc, dt, nperseg, noverlap, window, fmax)`**: call
`scipy.signal.stft` and keep the frequencies up to `fmax`. Returns the time
and frequency axes and the complex spectrogram.

## Inputs / outputs

- In: `acc` (m/s^2), `dt`, `nperseg=256`, `noverlap=224`, `window="hann"`,
  `fmax=25.0`.
- Out: dict with `f, t, Zxx`.

## Why

Shows how the frequency content evolves over a long record, useful for
building monitoring.
