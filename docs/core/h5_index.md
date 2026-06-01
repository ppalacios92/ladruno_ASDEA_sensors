# H5Index

`core/h5_index.py`

Scans a folder once and builds the index used by everything else.

## What to implement

1. **Constructor**: glob the folder with `pattern`, parse each file's date
   (`parse_date`), sort by date into `files` as `(datetime, path)`.
2. **Devices**: open one file and list the groups under `Devices/`.
3. **`fs` / `dt`**: estimate the sampling rate from the `Timestamp` dataset
   (two consecutive rows cover a fixed number of acceleration samples; the
   real rate is around 252.6 Hz, do not assume 250).
4. **`in_range(t0, t1)`**: return the ordered file paths whose date falls in
   the range. Fast, since the index already exists.
5. **`parse_date(filename)`**: parse `YYYYMMDDHHMMSS` with
   `datetime.strptime(name, "%Y%m%d%H%M%S")`. Skip and warn on a malformed
   name instead of crashing.

## Notes

The canonical date is the **file name**, not the file mtime and not the
embedded clock (the sensor clock may be wrong).
