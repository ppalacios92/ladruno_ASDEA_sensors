# Modal

`building/modal.py`

Operational modal analysis (OMA): modal frequencies, mode shapes, damping and
time tracking.

## What to implement

- **`modal_frequencies(signals, dt, fband, n_modes, smooth, bexp)`**: average
  the (smoothed) spectra of all sensors and pick the `n_modes` peaks inside
  `fband` as the shared modal frequencies.
- **`mode_shapes(signals, geometry, dt, modal_freqs, component, fband,
  n_modes)`**: at each modal frequency, take the cross-spectrum of every floor
  against a reference floor to get the amplitude and phase per floor; order by
  height (from `geometry`) to form the shape vector.
- **`damping(signal, dt, modal_freq, method, band)`**: estimate the damping
  ratio. `"half_power"` uses the bandwidth at -3 dB around the peak;
  `"random_decrement"` fits the decay of the random decrement signature.
- **`tracking(signal, dt, window, overlap, fband, n_modes, smooth, bexp)`**:
  slide a moving window, pick the peaks in `fband` per window, follow the
  frequencies in time.

## Inputs / outputs

- `signals`: `{device: signal}` across the floors.
- `geometry`: `config.SENSOR_GEOMETRY` (to order by height).
- Outputs: dicts with `freqs`; mode shapes add `heights, shapes, phases`;
  damping adds `zeta`; tracking adds `t, freqs`.

## Why

The mode shapes (including the torsional shape) and damping describe how the
building actually vibrates; tracking the frequencies over time is structural
health monitoring.
