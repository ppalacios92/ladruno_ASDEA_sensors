# Batch processor

`batch/processor.py`

Internal parallel engine. Not user-facing: it is driven by the dataset's
`n_jobs` and `parallel` properties.

## What to implement

**`BatchEngine.map(func, items)`**: apply `func` to each item, in parallel with
`joblib.Parallel(n_jobs=self.n_jobs)` when `parallel` is True, serially
otherwise. Keep the results in the input order. Optionally show a `tqdm` bar.

## When it runs

- `ds.<analysis>()` broadcasts an analysis over every device.
- `ds.sweep(...)` runs analyses over fixed time blocks.

The user controls it only through `ds.n_jobs` and `ds.parallel`.

## Source

Mirrors the parallel pattern of `EarthquakeSignal` `EarthquakeBatchProcessor`
(joblib + tqdm).
