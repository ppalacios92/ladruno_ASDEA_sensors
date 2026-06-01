# Examples

`examples/00_ASDEA_sensors_full_tour.ipynb`

An extensive Jupyter notebook that shows **every method with all of its
inputs**, as an API reference. While the package is a skeleton (methods raise
`NotImplementedError`), the notebook documents the intended calls and
parameters; each section becomes runnable as its layer is implemented.

## Sections

1. Setup
2. Instantiate and inspect (`SensorDataset`, all constructor parameters)
3. Per-sensor access, chaining and broadcast
4. Windows (start + length, or explicit bounds)
5. Resample (dataset, sensor, signal)
6. Signal pipeline -- `signal -> baseline -> filter -> derive`
7. Seismic -- Newmark, RotD, Arias, CAV, Housner, peaks, Fourier, PSD, STFT
8. Building -- transfer function, coherence, modal, torsion, drift, base rocking
9. Ambient -- step-by-step analysis, HVSR, amplification
10. Batch -- broadcast and time sweep
11. Export to `.h5` with Provenance
12. Plotting

## Run

```
pip install -e .
cd examples
jupyter lab 00_ASDEA_sensors_full_tour.ipynb
```

The notebook adds `../src` to `sys.path`, so it works straight from the
`examples/` folder before any install.
