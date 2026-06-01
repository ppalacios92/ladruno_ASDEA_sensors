"""Single configuration for the package: sensor axes, floor names, bands and
the ambient (STA/LTA) defaults. Edit here, not inside the analysis code.
"""

# Per-sensor axis mapping: which physical columns of the Acceleration dataset
# are X, Y, Z for each device.
#
# IMPORTANT: the sensors were installed in a NON-STANDARD orientation, so most
# of them do not use the natural (0, 1, 2) order. This mapping preserves the
# orientation used in the original routines and is printed on every read so it
# stays visible. Do not "fix" it to (0, 1, 2) without checking the install.
#
# NOTE: the current .h5 files only have 3 columns in Acceleration (0, 1, 2);
# a mapping with index > 2 must be reconciled with the ported readH5File.
SENSOR_AXES = {
    "MOF00134": (0, 1, 2),
    "MOF00135": (3, 1, 5),
    "MOF00136": (3, 1, 5),
    "MNAT0031": (3, 1, 5),
    "MNAT0034": (3, 1, 5),
}

# Human-readable floor for each device (used in plots and summaries).
FLOOR_TITLES = {
    "MOF00135": "",
    "MOF00134": "",
    "MOF00136": "",
    "MNAT0031": "",
    "MNAT0034": "",
}

# Gravity, used to convert the raw .h5 acceleration from g to m/s^2 on read.
GRAVITY = 9.81

# PSD / band-energy defaults.
PSD = {
    "NPERSEG": 256,
    "NOVERLAP": 128,
    "WINDOW": "hann",
    "FREQ_BANDS": [(0, 1), (1, 2.5), (2.5, 5), (5, 10)],
}

# Ambient analysis defaults (STA/LTA, windowing, taper, smoothing, FFT band).
AMBIENT = {
    "STA": 1.0,
    "LTA": 30.0,
    "vent": 60.0,
    "vmin": 0.2,
    "vmax": 2.5,
    "p": 0.05,
    "bexp": 40,
    "f1": 0.1,
    "f2": 25.0,
    "vent_seismic": False,
}
