# PSD

`seismic/psd.py`

Power spectral density (Welch) and energy per frequency band.

## What to implement

**`compute(acc, dt, nperseg, noverlap, window, bands, detrend)`**: call
`scipy.signal.welch` with the given parameters, then integrate the PSD over
each band in `bands` (default `config.PSD["FREQ_BANDS"]`) for the band-energy
summary.

## Inputs / outputs

- In: `acc` (m/s^2), `dt`, `nperseg=256`, `noverlap=128`, `window="hann"`,
  `bands=None`, `detrend="constant"`.
- Out: dict with `f, Pxx, band_energy` (dict keyed by band).
