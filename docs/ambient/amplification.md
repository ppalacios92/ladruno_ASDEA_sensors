# Amplification

`ambient/amplification.py`

Spectral amplification between sensors / floors, with an explicit basis.

## What to implement

**`compute(ref_signal, other_signals, dt, basis, config)`**: compute the
spectrum of the reference and of each other sensor on the chosen `basis`, and
return the ratio `other / ref` per device.

- `basis="fourier"`: smoothed Fourier amplitude spectra (default).
- `basis="response"`: Newmark `PSa` spectra.
- `basis="hvsr"`: the H/V ratio.

Report the basis used in the result.

## Inputs / outputs

- In: `ref_signal`, `other_signals` (`{device: signal}`), `dt`,
  `basis="fourier"`, `config`.
- Out: dict with `freqs, ratios` (dict by device), `basis`.

## Source

Generalizes the notebook's spectral amplification (which divided smoothed
Fourier spectra) by making the basis a parameter.
