"""IO layer: export results to self-describing .h5 files and read them back.

Every export carries a Provenance block (input files, processing pipeline,
parameters, units, version, date and a copy + hash of the config) so the
results are reproducible.
"""
