# Result cache

`core/cache.py`

Stores per-sensor analysis results on the dataset, with automatic
invalidation.

## What to implement

1. **`key`**: build a hashable key from device + analysis name + sorted
   params + a fingerprint of the source signal (window bounds, processing
   steps applied, dt). The fingerprint is what makes invalidation automatic:
   if the upstream signal changed, the key changes.
2. **`get` / `set` / `clear`**: dictionary access.
3. **`ram_bytes`**: sum the approximate size of the cached arrays, for the RAM
   warning shown by `SensorDataset.cache_summary`.

## Notes

No manual `recompute` flag anywhere: changing the signal or a parameter yields
a new key, so the analysis runs again on its own.
