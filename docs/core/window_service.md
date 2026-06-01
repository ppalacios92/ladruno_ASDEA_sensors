# Window service

`core/window_service.py`

Turns a start plus a length (or two explicit bounds) into a sample range.
Windows are lazy: they only store the bounds; reading happens later.

## What to implement

1. **`parse_duration`**: convert `"60min"`, `"300sec"`, `"2hour"`, `"90s"`,
   `"1.5h"` or a number into seconds.
2. **`window_from_start`**: resolve `start` (ISO string / datetime / sample
   index) into a position via the index, add `parse_duration(length)`, return
   `(t0, t1)`.
3. **`window_from_bounds`**: resolve two explicit times into `(t0, t1)`.

## Notes

These functions return bounds only. The `DeviceHandle` carries them and the
`H5Reader` honours them on the next read.
