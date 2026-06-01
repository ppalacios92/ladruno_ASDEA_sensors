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
  config/      single configuration (sensor axes, floors, bands, STA/LTA)
  derive/      baseline correction, filters, integration (acc -> vel -> disp)
  seismic/     Newmark, RotD, Arias, Fourier, PSD, STFT, peaks, CAV, Housner
  structural/  transfer function, coherence, modal tracking, interstory drift
  ambient/     STA/LTA, windowing, taper, FFT, Konno-Ohmachi, HVSR, amplification
  batch/       internal parallel engine (joblib)
  plotting/    plots, decoupled from the calculations
```

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
