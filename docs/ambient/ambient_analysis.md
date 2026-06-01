# Ambient analysis

`ambient/ambient_analysis.py`

Stateful, step-by-step ambient vibration analysis. The steps run in the order
of the routines, each stored so you can inspect it.

## What to implement

Each method runs one step and stores its output; if a later step is requested
before an earlier one, run the missing steps lazily in order.

1. **`sta_lta`**: `ambient.sta_lta.compute` -> `sta_lta_ratio`, `sta`, `lta`.
2. **`select_windows(manual)`**: `ambient.window_selector.compute`, or use the
   `manual` list of bounds -> `windows_signal`, `windows_time`, `win_ids`,
   `windows_pos`.
3. **`taper`**: `ambient.taper.compute` -> `taper_window`, tapered windows.
4. **`fft`**: `ambient.fft_windows.compute` -> `fft_complex`, `fft_abs`,
   `freqs`.
5. **`smooth`**: `ambient.konno_ohmachi.compute` -> `smoothed`.
6. **`average`**: `ambient.average.compute` -> `mean_spectrum`,
   `dominant_period`.

## No filtering here

The signal is expected to be filtered upstream with `SignalData.filter`; do not
filter inside these steps.

## Design

Replaces a monolithic "build everything" call: the user can run the steps one
by one or just ask for `mean_spectrum` and let the prior steps run.

## Source

Mirrors `AmbientSoilPeriod` `BuildPeriod`, but split into explicit steps and
without the internal filter.
