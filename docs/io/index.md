# IO

`io/`

Export analysis results to self-describing `.h5` files and read them back.
Every export carries a **Provenance** block so results are reproducible: you
can open the file later and know exactly how each number was produced.

## File layout

```
results.h5
  /Provenance
      input_files      list of source .h5 files
      pipeline         "baseline -> filter(0.1,24.9) -> derive"
      units = "SI"
      fs, dt, version, created_on
      config           full config copy (serialized)
      config_hash      stable hash of the config
  /Results/<device>/<analysis>
      <datasets>       e.g. T, PSa, IA_percent, freqs, H, ...
      .attrs           every parameter of that result (zeta, nperseg, bands, ...)
```

## Two levels

```python
ds.export_h5("run_31MAY.h5")               # whole dataset: all sensors + analyses
ds.MOF00135.export_h5("MOF00135.h5")       # one sensor (device chain)
```

Read back:

```python
from asdea_sensors.io.results_file import ResultsFile
r = ResultsFile("run_31MAY.h5")
r.provenance
r.analyses("MOF00135")
data, params = r.get("MOF00135", "newmark_x")
```

## Modules

| Module | Role |
|--------|------|
| `provenance` | build and write the Provenance block |
| `exporter` | write results (+ Provenance) to `.h5` |
| `results_file` | read a results `.h5` back |
