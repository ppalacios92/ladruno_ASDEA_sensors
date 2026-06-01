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

# Per-sensor geometry, used by the building layer (torsion, mode shapes,
# drift profile, base rocking). Floors come from the installation table; the
# UTM coordinates (E, N), elevation and azimuth are placeholders to fill in.
#
# - E, N, elev : UTM easting/northing and elevation, in metres. Only relative
#   values matter (plan distances and height differences).
# - azimuth    : heading of the sensor's local X axis, in degrees, relative to
#   a common building frame. The sensors were installed in a non-standard
#   orientation, so combining them (torsion, mode shapes) needs this rotation.
#   Leave at 0.0 if unknown; it can be estimated later by cross-correlation.
#
# Layout: MOF00134 is the base (-1); MNAT0031/MNAT0034/MOF00135 form a vertical
# array along the stairwell (floors 2/3/4); MOF00135 + MOF00136 sit on floor 4
# (stairwell + cantilever meeting room) and form the torsion pair.
SENSOR_GEOMETRY = {
    "MOF00134": {"floor": -1, "label": "Sala electrica subterraneo", "E": None, "N": None, "elev": None, "azimuth": 0.0},
    "MNAT0031": {"floor":  2, "label": "Cielo piso 2 (escaleras)",   "E": None, "N": None, "elev": None, "azimuth": 0.0},
    "MNAT0034": {"floor":  3, "label": "Cielo piso 3 (escaleras)",   "E": None, "N": None, "elev": None, "azimuth": 0.0},
    "MOF00135": {"floor":  4, "label": "Cielo piso 4 (escaleras)",   "E": None, "N": None, "elev": None, "azimuth": 0.0},
    "MOF00136": {"floor":  4, "label": "Cielo voladizo p4",          "E": None, "N": None, "elev": None, "azimuth": 0.0},
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
