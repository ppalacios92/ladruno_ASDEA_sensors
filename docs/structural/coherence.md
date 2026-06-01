# Coherence

`structural/coherence.py`

Magnitude-squared coherence between two sensors.

## What to implement

**`compute(acc_a, acc_b, dt, nperseg, noverlap, window)`**: call
`scipy.signal.coherence` and return the frequency axis and the coherence
(0 to 1).

## Inputs / outputs

- In: `acc_a`, `acc_b` (m/s^2), `dt`, `nperseg=1024`, `noverlap=512`,
  `window="hann"`.
- Out: dict with `f, coherence`.

## Why

Validates the transfer function: a modal peak is trustworthy only where the
coherence is close to 1.
