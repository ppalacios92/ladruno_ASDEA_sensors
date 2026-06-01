# Coherence

`building/coherence.py`

Magnitude-squared coherence between sensors.

## What to implement

- **`compute(acc_a, acc_b, dt, nperseg, noverlap, window)`**: call
  `scipy.signal.coherence`, return `f` and the coherence (0 to 1).
- **`matrix(signals, dt, **kwargs)`**: coherence for every pair of sensors,
  returned as `{(a, b): coherence}` plus the shared `f`.

## Inputs / outputs

- In: `acc_a`, `acc_b` (m/s^2), `dt`, `nperseg=1024`, `noverlap=512`,
  `window="hann"`.
- Out (`compute`): dict with `f, coherence`.
- Out (`matrix`): dict with `f, pairs`.

## Why

Validates the transfer function and mode shapes: a modal peak is trustworthy
only where coherence is close to 1. The matrix also flags noisy/faulty
channels.
