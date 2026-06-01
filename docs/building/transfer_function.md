# Transfer function

`building/transfer_function.py`

Floor/base transfer function (FRF). Its peaks are the building's modal
frequencies.

## What to implement

- **`compute(acc_num, acc_den, dt, estimator, nperseg, noverlap, window,
  smooth, bexp, fmax)`**: Welch cross/auto spectra of the two signals, form the
  estimator (`H1 = Sxy/Sxx`, `H2 = Syy/Syx`, `Hv = sqrt(H1*H2)`), optionally
  Konno-Ohmachi smooth `|H|`, keep up to `fmax`, pick the peaks as the modal
  frequencies.
- **`stack(signals_by_floor, base_signal, dt, **kwargs)`**: call `compute` for
  every floor against the base, returning a dict keyed by floor/device. This is
  the multi-sensor use: one FRF per floor of the vertical array.

## Inputs / outputs

- In: `acc_num` (upper floor), `acc_den` (base), `dt`, `estimator="H1"`,
  `nperseg=1024`, `noverlap=512`, `window="hann"`, `smooth="konno"`,
  `bexp=40`, `fmax=25.0`.
- Out: dict with `f, H, modal_freqs, modal_amps`.

## Why

Identifies the building's natural frequencies; a drop over time means a loss of
stiffness. Stacking over the array also feeds the mode shapes.
