# ASDEA_sensors

Post-processing of building accelerometer records stored as `.h5` files.

Give it a path, it indexes the `.h5` files, reads the continuous acceleration
signal per sensor, and lets you run signal processing, spectra, and structural
characterization on top of it.

## Layout

```
src/asdea_sensors/
  core/        discovery, lazy reading, windowing, resampling, cache
  model/       SignalData container + processing steps
  config/      single configuration (sensor axes, geometry, bands, STA/LTA)
  derive/      baseline correction, filters, integration (acc -> vel -> disp)
  seismic/     Newmark, RotD, Arias, Fourier, PSD, STFT, peaks, CAV, Housner
  building/    transfer function, coherence, modal, torsion, drift, base rocking
  ambient/     STA/LTA, windowing, taper, FFT, Konno-Ohmachi, HVSR, amplification
  batch/       internal parallel engine (joblib)
  io/          export results to self-describing .h5 with Provenance
  plotting/    plots, decoupled from the calculations
examples/      extensive Jupyter tour of every method and input
```

## Sensor layout

From the installation table:

| Sensor | Floor | Location |
|--------|-------|----------|
| MOF00134 | -1 | Electrical room, basement (base / input) |
| MNAT0031 |  2 | Stairwell ceiling, floor 2 |
| MNAT0034 |  3 | Stairwell ceiling, floor 3 |
| MOF00135 |  4 | Stairwell ceiling, floor 4 |
| MOF00136 |  4 | Cantilever meeting room, floor 4 |

The stairwell sensors (base + floors 2/3/4) form a vertical array for mode
shapes and drift; MOF00135 + MOF00136 share floor 4 and form the torsion pair.

## Units

Internal units are SI: acceleration `m/s^2`, velocity `m/s`, displacement `m`.
The raw `.h5` acceleration is in `g`, so the reader converts it to `m/s^2` on read.
Newmark accepts a `factor` to present acceleration spectra in other units
(e.g. `factor = 1/9.81` for `g`).

## Quick start

```python
from asdea_sensors import SensorDataset

ds = SensorDataset(r"path/to/h5_folder")
ds.devices

sig = ds.MOF00135.signal().baseline().filter(0.1, 24.9).derive()
spec = ds.MOF00135.newmark(component="x")
frf = ds.transfer_function(numerator="MOF00135", denominator="MOF00134", component="x")
```

## Documentation

Built with MkDocs:

```
pip install -e ".[docs]"
mkdocs serve
```
