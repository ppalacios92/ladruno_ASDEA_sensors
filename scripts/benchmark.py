# -*- coding: utf-8 -*-
"""Benchmark across devices / windows / components / analyses.

Runs >1000 analysis calls over the example data, measuring per-analysis timing
and checking that results are finite. Edit FOLDER for your data.

    python scripts/benchmark.py
"""
import time
import statistics
import warnings
from collections import defaultdict
from datetime import datetime, timedelta

import numpy as np

from asdea_sensors import SensorDataset
from asdea_sensors.seismic import (newmark, rotd, arias, cav, housner, peaks,
                                    fourier, psd, stft)
from asdea_sensors.ambient import hvsr
from asdea_sensors.ambient.ambient_analysis import AmbientAnalysis
from asdea_sensors.building import transfer_function, coherence
from asdea_sensors.derive import integrate

warnings.filterwarnings("ignore")

FOLDER = r"C:\Users\ppala\Desktop\02_31MAY2026"
DT = 0.004
FMIN, FMAX = 0.2, 20.0
WLENS = [30, 60, 120, 300]                                  # seconds
STARTS = [datetime(2026, 5, 31, 17, 30, 0), datetime(2026, 5, 31, 18, 30, 0)]
CONFIG = {"Fs": round(1 / DT), "vent": 30, "vent_seismic": False,
          "STA": 1, "LTA": 30, "vmin": 0.010, "vmax": 5.50,
          "p": 0.05, "f1": 0.20, "f2": 20.0, "bexp": 1e2}

ds = SensorDataset(FOLDER, verbose=False).resample(dt=DT)
DEVICES = ds.devices

timings = defaultdict(list)
sanity = defaultdict(lambda: [0, 0])
errors = []
nruns = [0]


def _finite(r):
    if isinstance(r, dict):
        return all(not (isinstance(v, np.ndarray) and v.size and
                        not np.all(np.isfinite(v))) for v in r.values())
    if isinstance(r, np.ndarray):
        return r.size == 0 or bool(np.all(np.isfinite(r)))
    return True


def run(name, fn):
    nruns[0] += 1
    t0 = time.perf_counter()
    try:
        r = fn()
    except Exception as e:
        timings[name].append(time.perf_counter() - t0)
        sanity[name][1] += 1
        if len(errors) < 20:
            errors.append("%s: %s" % (name, e))
        return None
    timings[name].append(time.perf_counter() - t0)
    sanity[name][0 if _finite(r) else 1] += 1
    return r


t_total = time.perf_counter()
for start in STARTS:
    for wlen in WLENS:
        end = start + timedelta(seconds=wlen)
        sigs = {}
        for d in DEVICES:
            sigs[d] = run("read", (lambda d=d: ds.device(d).get_window(start, end)
                                   .baseline().filter(FMIN, FMAX, engine="scipy")
                                   .signal(components="all")))
        for d in DEVICES:
            sig = sigs[d]
            if sig is None:
                continue
            dt = sig.dt
            for comp in ("x", "y", "z"):
                a = sig.component(comp)
                vel, disp = integrate.derive(a, dt)
                run("newmark", lambda a=a, dt=dt: newmark.compute(a, dt, max_period=3.0, dT=0.02))
                run("fourier", lambda a=a, dt=dt: fourier.compute(a, dt))
                run("psd", lambda a=a, dt=dt: psd.compute(a, dt))
                run("stft", lambda a=a, dt=dt: stft.compute(a, dt))
                run("arias", lambda a=a, dt=dt: arias.compute(a, dt))
                run("cav", lambda a=a, dt=dt: cav.compute(a, dt))
                run("housner", lambda a=a, dt=dt: housner.compute(a, dt))
                run("peaks", lambda a=a, vel=vel, disp=disp: peaks.compute(a, vel, disp))
            x, y, z = sig.acc_x, sig.acc_y, sig.acc_z
            run("fourier_konno", lambda x=x, dt=dt: fourier.compute(x, dt, smooth="konno", bexp=40))
            run("rotd", lambda x=x, y=y, dt=dt: rotd.compute(x, y, dt, rotd=50, angle_step=15, max_period=3.0, dT=0.02))
            run("ambient", lambda x=x: AmbientAnalysis(x, CONFIG).average())
            run("hvsr", lambda x=x, y=y, z=z: hvsr.compute(x, y, z, CONFIG))
        order = ["MOF00134", "MNAT0031", "MNAT0034", "MOF00135"]
        for i in range(1, len(order)):
            a, b = sigs.get(order[i]), sigs.get(order[0])
            if a is None or b is None:
                continue
            xa, xb = a.acc_x, b.acc_x
            n = min(len(xa), len(xb))
            run("transfer", lambda xa=xa, xb=xb, n=n: transfer_function.compute(xa[:n], xb[:n], DT, smooth=None, fmax=25.0))
            run("coherence", lambda xa=xa, xb=xb, n=n: coherence.compute(xa[:n], xb[:n], DT))

elapsed = time.perf_counter() - t_total

print("=" * 78)
print("BENCHMARK  -  total runs: %d  |  wall time: %.1f s" % (nruns[0], elapsed))
print("=" * 78)
print("%-16s %5s %9s %9s %9s %9s   %s"
      % ("analysis", "n", "min[ms]", "med[ms]", "p95[ms]", "max[ms]", "ok/bad"))
print("-" * 78)
for name in sorted(timings):
    ts = sorted(t * 1000 for t in timings[name])
    n = len(ts)
    p95 = ts[min(n - 1, int(0.95 * n))]
    ok, bad = sanity[name]
    print("%-16s %5d %9.2f %9.2f %9.2f %9.2f   %d/%d"
          % (name, n, ts[0], statistics.median(ts), p95, ts[-1], ok, bad))
print("-" * 78)
if errors:
    print("errors (first %d):" % len(errors))
    for e in errors:
        print("  ", e)
else:
    print("no errors.")
print("=" * 78)
