# Parallel reader

`core/parallel_reader.py`

Reads slices from many `.h5` files concurrently, for windows that span many
files.

## What to implement

**`read_slices`**: submit one read per file to a `ThreadPoolExecutor`
(`workers` threads, I/O bound), collect the per-file results in the original
file order, and return them for the `H5Reader` to concatenate.

## Notes

Threads (not processes): the work is HDF5 I/O, which releases the GIL.
