# Examples

The `examples/` folder has a **master** notebook plus 10 focused notebooks.
Everything shown in the focused notebooks is also represented in the master.

While the package is a skeleton (methods raise `NotImplementedError`), the
notebooks are an API reference: they show the intended calls and all their
inputs. Each section becomes runnable as its layer is implemented.

## Notebooks

| # | Notebook | Topic |
|---|----------|-------|
| 00 | `00_ASDEA_sensors_full_tour.ipynb` | **Master** -- every method, indexes the rest |
| 01 | `01_load_and_inspect.ipynb` | load, set `SENSOR_GEOMETRY`, summary, internal prints |
| 02 | `02_windows_and_export.ipynb` | extract a time window, export the record + spectra to `.h5` |
| 03 | `03_signal_pipeline.ipynb` | baseline / filter / derive and their permutations |
| 04 | `04_filtered_vs_unfiltered.ipynb` | compare raw vs filtered Fourier / spectra / PSD |
| 05 | `05_response_spectra.ipynb` | Newmark (full output, `factor`), RotD percentiles |
| 06 | `06_intensity_measures.ipynb` | Arias, CAV, Housner, PGA/PGV/PGD |
| 07 | `07_frequency_content.ipynb` | Fourier, PSD bands, STFT, floor-by-floor |
| 08 | `08_building_modal.ipynb` | transfer function stack, coherence, mode shapes, damping |
| 09 | `09_torsion_and_drift.ipynb` | floor-4 torsion, orbit, drift profile, base rocking |
| 10 | `10_ambient_and_amplification.ipynb` | ambient step-by-step, HVSR, amplification bases |

## Highlights

- **Geometry up front**: notebook 01 (and the master) set `SENSOR_GEOMETRY`
  (UTM E/N, elevation, azimuth) at the start, overriding the config for the
  session.
- **Window + export**: notebook 02 extracts one sensor over a time window,
  computes acceleration / spectra / Arias / Newmark, and exports them to a
  self-describing `.h5` with a Provenance block.
- **Composite exercises**: notebook 04 builds raw and filtered versions of the
  same window and compares their Fourier spectra, response spectra and band
  energy; notebook 03 runs the pipeline steps in different orders.
- **Internal prints**: every method prints what it did when `ds.verbose=True`,
  in the ShakerMakerResults style.

## Run

```
pip install -e .
cd examples
jupyter lab 00_ASDEA_sensors_full_tour.ipynb
```

The notebooks add `../src` to `sys.path`, so they work straight from the
`examples/` folder before any install.
