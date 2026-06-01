# ASDEA_sensors

Post-processing of building accelerometer records stored as `.h5` files.

You give the package a folder path. It indexes the `.h5` files, reads the
continuous acceleration per sensor, and lets you run signal processing,
spectra and structural characterization on top of it.

## How to read these docs

Each page documents one source file and is written as an **implementation
guide**: what the file is for, what to implement, the public API, and which
original routine to port it from. The skeletons already define the signatures
and docstrings; the docs tell you what goes inside.

## Layers

| Layer | Purpose |
|-------|---------|
| `core` | Discover files, read lazily, window, resample, cache |
| `model` | The `SignalData` container and its processing steps |
| `config` | Single configuration (sensor axes, floors, bands, STA/LTA) |
| `derive` | Baseline correction, filters, integration (acc -> vel -> disp) |
| `seismic` | Newmark, RotD, Arias, Fourier, PSD, STFT, peaks, CAV, Housner |
| `building` | Transfer function, coherence, modal, torsion, drift, base rocking |
| `ambient` | STA/LTA, windowing, taper, FFT, Konno-Ohmachi, HVSR, amplification |
| `batch` | Internal parallel engine (joblib) |
| `io` | Export results to self-describing `.h5` with Provenance |
| `plotting` | Figures, decoupled from the calculations |

The `examples/` folder has an extensive Jupyter tour showing every method with
all of its inputs.

## Conventions

- **Units are SI**: acceleration `m/s^2`, velocity `m/s`, displacement `m`.
  The raw `.h5` acceleration is in `g`, converted to `m/s^2` on read.
- **Per-sensor access**: `ds.MOF00135.<method>`. Calling `ds.<method>` broadcasts
  to every device.
- **Components**: `component="x"|"y"|"z"` returns one result; `"all"` returns a
  dict per axis.
- **Cache**: results are stored on the dataset and invalidated automatically when
  the source signal or parameters change. No manual recompute flag.
- **Date**: the canonical date of a file is its name `YYYYMMDDHHMMSS`.
- **Internal prints**: every method prints a short line of what it did (parameters
  used, shapes, whether it came from cache), in the ShakerMakerResults style,
  toggled by `ds.verbose`. ASCII only, e.g.
  `[newmark] MOF00135 comp=x zeta=0.05 Tmax=5.01 dT=0.01 -> 501 periods (cached)`.

## Original routines

The analysis code is ported from two existing packages (copied in, not
installed as dependencies):

- `EarthquakeSignal` -> Newmark, RotD, Arias, Fourier, baseline correction.
- `AmbientSoilPeriod` -> STA/LTA, window selection, taper, FFT, Konno-Ohmachi.
