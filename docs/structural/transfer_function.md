# Transfer function

`structural/transfer_function.py`

Floor/base transfer function (FRF). Its peaks are the building's modal
frequencies.

## What to implement

**`compute(acc_num, acc_den, dt, estimator, nperseg, noverlap, window, smooth,
bexp, fmax)`**: with Welch cross/auto spectra of the two signals, form the FRF
estimator (`H1 = Sxy/Sxx`, `H2 = Syy/Syx`, `Hv = sqrt(H1*H2)`), optionally
Konno-Ohmachi smooth `|H|`, keep up to `fmax`, and pick the peaks as the modal
frequencies.

## Inputs / outputs

- In: `acc_num` (upper floor), `acc_den` (base), `dt`, `estimator="H1"`,
  `nperseg=1024`, `noverlap=512`, `window="hann"`, `smooth="konno"`,
  `bexp=40`, `fmax=25.0`.
- Out: dict with `f, H, modal_freqs, modal_amps`.

## Why

Identifies the building's natural frequencies; a drop over time means a loss of
stiffness.
