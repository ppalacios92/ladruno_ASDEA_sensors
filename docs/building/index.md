# Building

`building/`

Structural characterization of the building from the sensor data. This layer
sits on top of the signal machinery and the **sensor geometry**
(`config.SENSOR_GEOMETRY`) and works across **all** sensors, not just a pair.

## Sensor layout it relies on

| Sensor | Floor | Role |
|--------|-------|------|
| MOF00134 | -1 | base / input, base rocking |
| MNAT0031 | 2 | vertical array |
| MNAT0034 | 3 | vertical array |
| MOF00135 | 4 | vertical array + torsion pair |
| MOF00136 | 4 | torsion pair (cantilever) |

- **Vertical array** (base -> 2 -> 3 -> 4, along the stairwell): mode shapes,
  damping, drift profile, transfer functions, story envelopes.
- **Floor-4 pair** (MOF00135 + MOF00136): floor rotation `theta(t)`, torsional
  frequency, orbit.

## Modules

| Module | What it gives |
|--------|---------------|
| `geometry` | plan distances, grouping by floor, ordering by height, azimuth rotation |
| `transfer_function` | FRF single pair, or stacked base -> each floor |
| `coherence` | single pair, or matrix across all pairs |
| `modal` | modal frequencies, mode shapes, damping, modal tracking |
| `torsion` | floor rotation, torsional spectrum, torsion ratio, orbit |
| `drift` | interstory drift, drift profile, story envelopes |
| `base_rocking` | foundation rocking from the base sensor |

## Geometry dependency

The combining methods (torsion, mode shapes) need each sensor's plan position
and **azimuth** to rotate the local axes into a common building frame, because
the sensors were installed in a non-standard orientation. Fill
`config.SENSOR_GEOMETRY` with the UTM coordinates and headings; until then the
floors are known but the spatial methods stay symbolic.

## Dataset API

```python
ds.transfer_function(base="MOF00134", floors="all", component="x")
ds.mode_shapes(component="x")
ds.coherence_matrix(component="x")
ds.torsion(floor=4, component="x")
ds.drift_profile(component="x")
ds.base_rocking()
```
