# STA/LTA

`ambient/sta_lta.py`

Short-term over long-term average ratio.

## What to implement

**`compute(signal, fs, sta, lta)`**: square the signal, pad the edges, and use
cumulative sums to get the STA and LTA moving averages, then their ratio.

## Inputs / outputs

- In: `signal`, `fs` (Hz), `sta` (s), `lta` (s).
- Out: `(sta_lta, sta_vals, lta_vals)`.

## Source

Port from `AmbientSoilPeriod` `algorithm_sta_lta`.
