# Plotting

`plotting/`

Figures, decoupled from the calculations. Every plot function takes a result
(or a `SignalData` / analysis object) that was already computed and cached, and
only draws it. Nothing here computes signals or spectra.

## Modules

| Module | Plots |
|--------|-------|
| `signal_plots` | acceleration / velocity / displacement time histories |
| `fourier_plots` | Fourier amplitude spectrum with dominant peaks |
| `newmark_plots` | Newmark spectral quantities vs period |
| `rotd_plots` | RotD percentile spectra |
| `arias_plots` | Arias intensity (Husid) curve and significant duration |
| `psd_plots` | PSD curve and band energy across sensors |
| `stft_plots` | spectrogram |
| `transfer_plots` | transfer function magnitude with modal frequencies |
| `modal_plots` | tracked modal frequencies vs time |
| `ambient_plots` | STA/LTA, selected windows, per-window and mean spectra |
| `amplification_plots` | amplification ratios per sensor |

## Conventions

- `component="x"|"y"|"z"|"all"` and a `save` argument (format/path or `None`
  to show).
- ASCII only in any text drawn; no box-drawing characters.
- Read the cached numbers; never trigger a recomputation from a plot.
