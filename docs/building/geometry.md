# Geometry

`building/geometry.py`

Spatial relations between sensors, read from `config.SENSOR_GEOMETRY`.

## What to implement

- **`plan_distance(geometry, a, b)`**: Euclidean distance between two sensors in
  the E-N plane (`sqrt(dE^2 + dN^2)`).
- **`plan_vector(geometry, a, b)`**: the `(dE, dN)` vector from `a` to `b`.
- **`sensors_by_floor(geometry)`**: `{floor: [device, ...]}`.
- **`order_by_height(geometry, devices)`**: device ids sorted by `elev`.
- **`heights(geometry, devices)`**: the elevations, ordered.
- **`rotate_to_common(acc_x, acc_y, azimuth)`**: rotate a sensor's horizontal
  pair by `azimuth` degrees into the common building frame
  (`x' = x cos a - y sin a`, `y' = x sin a + y cos a`).

## Why it matters

Only relative geometry is used (plan distances, height differences), so UTM
coordinates are fine without any datum conversion. The **azimuth** is essential:
combining sensors for torsion or mode shapes requires them in a shared frame,
and these sensors are not aligned to a common north.

## Inputs

`geometry` is `config.SENSOR_GEOMETRY`: per device a dict with `floor`, `E`,
`N`, `elev`, `azimuth`. Missing coordinates (`None`) should raise a clear error
in the methods that need them.
