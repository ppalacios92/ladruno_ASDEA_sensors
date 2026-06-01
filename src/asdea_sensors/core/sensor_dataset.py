"""SensorDataset: the main object. Give it a path, it indexes the .h5 files and
exposes per-sensor reading, processing and analysis with a result cache.

Cheap to instantiate: the constructor only builds the file index and reads
metadata (no signal data). Heavy reads happen on demand and are cached.
"""

import copy
import os

import numpy as np

from ..config import settings
from . import memory
from .cache import ResultCache
from .device_handle import DeviceHandle
from .h5_index import H5Index
from .h5_reader import H5Reader


class SensorDataset:
    """Entry point for a folder of accelerometer .h5 files.

    Parameters
    ----------
    path : str
        Folder containing the .h5 files (names like ``YYYYMMDDHHMMSS.h5``).
    pattern : str, default "*.h5"
        Glob used to pick the files to index.
    date_source : {"filename", "timestamp"}, default "filename"
        Where each file's date comes from. "filename" parses the name
        ``YYYYMMDDHHMMSS`` (canonical). "timestamp" reads the embedded clock.
    devices : list of str or None, default None
        Restrict to these device ids. ``None`` keeps every device found.
    load_mode : {"auto", "ram", "lazy"}, default "auto"
        "ram" loads windows fully into memory, "lazy" reads only the requested
        slice from disk, "auto" decides with ``ram_fraction`` and psutil.
    ram_fraction : float, default 0.5
        In "auto" mode, switch to lazy when the data would exceed this fraction
        of the available RAM.
    axes_map : dict or None, default None
        Per-sensor axis mapping ``{device: (ix, iy, iz)}``. ``None`` uses
        ``config.settings.SENSOR_AXES`` (sensors installed in a non-standard
        orientation, see the note there).
    verbose : bool, default True
        Print the summary block when the dataset is built.

    Attributes
    ----------
    devices : list of str
    fs : float
        Sampling frequency in Hz, measured from the Timestamp dataset.
    dt : float
        Sampling interval in seconds.
    time_span : tuple
        ``(first_datetime, last_datetime)`` across the indexed files.
    axes_map : dict
        Active per-sensor axis mapping.

    Notes
    -----
    Per-sensor access uses attribute syntax, e.g. ``ds.MOF00135`` returns a
    :class:`~asdea_sensors.core.device_handle.DeviceHandle`. Calling an analysis
    method on ``ds`` itself broadcasts it to every device (parallel, via the
    internal batch engine controlled by ``n_jobs`` / ``parallel``).
    Internal units are SI: acceleration m/s^2, velocity m/s, displacement m.
    """

    def __init__(self, path, pattern="*.h5", date_source="filename",
                 devices=None, titles=None, device_colors=None,
                 load_mode="auto", ram_fraction=0.5, axes_map=None,
                 parallel=False, n_jobs=4, verbose=True):
        self.path = path
        self.pattern = pattern
        self.date_source = date_source
        self.load_mode = load_mode
        self.ram_fraction = ram_fraction
        self.verbose = verbose

        # Batch engine for broadcasts (ds.fourier(), ds.psd(), ...).
        # parallel=False (default) runs them in-process, which reuses the shared
        # conditioned-signal cache across analyses and avoids the per-process
        # spawn + numba recompile cost; best for a few sensors over a window.
        # parallel=True spreads devices over n_jobs processes (no shared cache).
        self.n_jobs = n_jobs
        self.parallel = parallel

        # Build the file index (this only reads metadata, never signal data).
        self._index = H5Index(path, pattern=pattern, date_source=date_source)

        # Devices: those found in the files, optionally restricted and reordered
        # by the argument (the given order is kept).
        found = list(self._index.devices)
        if devices is not None:
            found = [d for d in devices if d in found]
        self.devices = found

        # Per-sensor labels live on the object so plots don't need them passed.
        # Default to config.FLOOR_TITLES; settable later as ds.titles = {...}.
        if titles is not None:
            self.titles = dict(titles)
        else:
            self.titles = dict(getattr(settings, "FLOOR_TITLES", {}) or {})

        # Per-sensor plot color, on the object so plots never need it passed.
        # Defaults to the matplotlib tab cycle, one color per device in order.
        _tab = ["tab:blue", "tab:orange", "tab:green", "tab:red", "tab:purple",
                "tab:brown", "tab:pink", "tab:gray", "tab:olive", "tab:cyan"]
        if device_colors is not None:
            self.device_colors = dict(device_colors)
        else:
            self.device_colors = {d: _tab[i % len(_tab)]
                                  for i, d in enumerate(self.devices)}

        self.fs = self._index.fs
        self.dt = self._index.dt

        # Total samples available per device, and the largest one as a metric
        # of how much data there is to plot.
        self.n_samples = dict(self._index.n_samples)
        self.max_points = self._index.max_points

        if self._index.files:
            self.time_span = (self._index.files[0][0], self._index.files[-1][0])
        else:
            self.time_span = None

        if self.time_span is not None:
            self.duration = (self.time_span[1] - self.time_span[0]).total_seconds()
        else:
            self.duration = 0.0

        # Active axis mapping and the reader built on top of it.
        self.axes_map = axes_map if axes_map is not None else settings.SENSOR_AXES
        self._reader = H5Reader(self.axes_map)

        # Result cache: keep the object (for keying/get/set) and expose its
        # underlying dict as self._cache (the io.exporter iterates over it).
        self._cache_obj = ResultCache()
        self._cache = self._cache_obj._store

        # Shared store of conditioned signals, keyed by (device, components,
        # remove_mean, signal_state). Built once per sensor and reused by every
        # analysis, so the read + baseline + filter + derive runs a single time.
        self._signal_store = {}

        # Dataset-level resample target (set by resample()); None = native dt.
        self._resample_dt = None

        # Dataset-level default window (set by get_window()/window()); when set,
        # every per-sensor read is restricted to it. None = whole record.
        self._default_window = None

        # Dataset-level processing pipeline (set by baseline()/filter()/derive()).
        # Each read replays these steps on the SignalData, so the object carries
        # its own conditioning and the plots only visualize it. List of
        # (step_name, kwargs).
        self._pipeline = []

        self.units = "SI"

        if self.verbose:
            self.summary()

    # -- inspection ----------------------------------------------------

    def _summary_lines(self):
        """Build the summary block lines (ASCII only)."""
        sep = "-" * 60
        lines = [sep, "SensorDataset", sep]
        lines.append("path        : %s" % self.path)
        lines.append("files       : %d" % len(self._index.files))
        if self.time_span is not None:
            lines.append("time span   : %s  ->  %s"
                         % (self.time_span[0], self.time_span[1]))
            lines.append("duration    : %.1f s" % self.duration)
        lines.append("devices     : %s" % ", ".join(self.devices))
        if self.fs is not None:
            lines.append("fs / dt     : %.4f Hz / %.6f s" % (self.fs, self.dt))
        lines.append(sep)
        lines.append("axes / samples (per sensor):")
        for dev in self.devices:
            axes = self.axes_map.get(dev, (0, 1, 2))
            n = self.n_samples.get(dev, 0)
            label = self.titles.get(dev, "") if hasattr(self, "titles") else ""
            suffix = ("  |  %s" % label) if label else ""
            lines.append("  %-10s -> %-9s  %s samples/axis%s"
                         % (dev, str(tuple(axes)), format(n, ","), suffix))
        lines.append(sep)

        total = 0
        for _when, p in self._index.files:
            try:
                total += os.path.getsize(p)
            except OSError:
                pass
        lines.append("on-disk size: %.2f MB" % (total / (1024.0 * 1024.0)))

        used, available, percent = memory.ram_status()
        lines.append("RAM         : used %.2f GB / avail %.2f GB (%.0f%%)"
                     % (used / 1e9, available / 1e9, percent))
        lines.append(sep)
        return lines

    def summary(self):
        """Print the summary block (files, fs/dt, devices, axes, RAM)."""
        for line in self._summary_lines():
            print(line)

    def cache_summary(self):
        """Print what is cached and how much RAM the cache uses."""
        sep = "-" * 60
        n = len(self._cache)
        ram = self._cache_obj.ram_bytes()
        print(sep)
        print("cache: %d entries, %.2f MB" % (n, ram / (1024.0 * 1024.0)))
        print("hint: call clear_cache() to free it")
        print(sep)

    def clear_cache(self):
        """Drop every cached result and free the memory."""
        self._cache_obj.clear()

    # -- per-sensor access ---------------------------------------------

    def device(self, name):
        """Return the :class:`DeviceHandle` for one device id."""
        return DeviceHandle(self, name, window=self._default_window)

    def __getattr__(self, name):
        """Allow ``ds.MOF00135`` to return that device's handle."""
        # Access __dict__ directly to avoid recursion during construction.
        devices = self.__dict__.get("devices", [])
        if name in devices:
            return DeviceHandle(self, name,
                                window=self.__dict__.get("_default_window"))
        raise AttributeError(name)

    # -- windowing (whole dataset) -------------------------------------

    def _exact_window_n(self, t0, t1):
        """Exact number of samples in ``[t0, t1]`` (matches the reader trim).

        Computed without reading the data: the read anchors the time vector at
        the first overlapping file's start and keeps samples with
        ``t0 <= t_abs <= t1`` (both ends inclusive), so the count is
        ``floor((t1-start)/dt) - ceil((t0-start)/dt) + 1``.
        """
        files = self._index.in_range(t0, t1)
        if not files or not self.dt:
            return 0
        start = self._index.parse_date(os.path.basename(files[0]))
        if start is None:
            return 0
        s0 = float((np.datetime64(t0) - np.datetime64(start)) / np.timedelta64(1, "s"))
        s1 = float((np.datetime64(t1) - np.datetime64(start)) / np.timedelta64(1, "s"))
        k0 = int(np.ceil(s0 / self.dt))
        k1 = int(np.floor(s1 / self.dt))
        return max(0, k1 - k0 + 1)

    def _window_summary(self):
        """Print the windowed-dataset properties (span, duration, samples)."""
        sep = "-" * 60
        t0, t1 = self._default_window
        dur = float((np.datetime64(t1) - np.datetime64(t0))
                    / np.timedelta64(1, "s"))
        n = self._exact_window_n(t0, t1)
        print(sep)
        print("windowed dataset")
        print("  span    : %s  ->  %s" % (t0, t1))
        print("  duration: %.1f s" % dur)
        print("  fs / dt : %.4f Hz / %.6f s" % (self.fs, self.dt))
        print("  devices : %s" % ", ".join(self.devices))
        print("  samples : %s / axis / device" % format(n, ","))
        print(sep)

    def _windowed_copy(self, bounds):
        new = copy.copy(self)
        new._default_window = bounds
        # Fresh cache so windowed results never collide with the full-record ones.
        new._cache_obj = ResultCache()
        new._cache = new._cache_obj._store
        new._signal_store = {}
        if self.verbose:
            new._window_summary()
        return new

    def get_window(self, t0, t1):
        """Return a dataset whose every read is restricted to ``[t0, t1]``.

        The returned dataset behaves like the original but every per-sensor read
        (``ds_w.MOF00135.signal()``, broadcasts, building methods, and the
        ``*_all`` plot helpers) is limited to this window, so you set it once.
        """
        from . import window_service as _window
        dev0 = self.devices[0] if self.devices else None
        bounds = _window.window_from_bounds(self._index, dev0, t0, t1)
        return self._windowed_copy(bounds)

    def window(self, start, length):
        """Return a dataset windowed to ``[start, start + length]`` (all reads)."""
        from . import window_service as _window
        dev0 = self.devices[0] if self.devices else None
        bounds = _window.window_from_start(self._index, dev0, start, length)
        return self._windowed_copy(bounds)

    # -- processing pipeline (whole dataset) ---------------------------
    # baseline/filter/derive return a new dataset carrying the step. Every read
    # replays the pipeline, so the object is "already conditioned" and the plots
    # only visualize it. Keep raw and conditioned datasets side by side.

    def _pipelined_copy(self, step, kwargs, message):
        new = copy.copy(self)
        new._pipeline = self._pipeline + [(step, dict(kwargs))]
        new._cache_obj = ResultCache()
        new._cache = new._cache_obj._store
        new._signal_store = {}
        if self.verbose:
            print("[%s] %s" % (step, message))
        return new

    def baseline(self, method="polynomial", components="all"):
        """Return a dataset with a baseline-correction step added to the pipeline.

        Parameters
        ----------
        method : {"polynomial", "linear", "mean"}, default "polynomial"
        components : {"x", "y", "z", "all"}, default "all"
        """
        return self._pipelined_copy(
            "baseline", {"method": method, "components": components},
            "%s on %s" % (method, components))

    def filter(self, fmin, fmax, engine="obspy", corners=4, zerophase=True,
               components="all"):
        """Return a dataset with a band-pass step added to the pipeline.

        Parameters
        ----------
        fmin, fmax : float
            Band edges in Hz.
        engine : {"obspy", "scipy"}, default "obspy"
        corners : int, default 4
            Number of filter corners (the Butterworth order).
        zerophase : bool, default True
            Zero-phase (forward-backward) filtering.
        components : {"x", "y", "z", "all"}, default "all"
        """
        # SignalData.filter names the corners argument ``order``.
        return self._pipelined_copy(
            "filter",
            {"fmin": fmin, "fmax": fmax, "engine": engine, "order": corners,
             "zerophase": zerophase, "components": components},
            "bandpass %.3g-%.3g Hz (%s, corners=%d, zerophase=%s)"
            % (fmin, fmax, engine, corners, zerophase))

    def derive(self, method="trapezoid", remove_mean=True, components="all"):
        """Return a dataset with an integration step (acc->vel->disp) in the pipeline."""
        return self._pipelined_copy(
            "derive",
            {"method": method, "remove_mean": remove_mean, "components": components},
            "integrate acc -> vel -> disp")

    # -- preprocessing -------------------------------------------------

    def resample(self, dt=None, fs=None):
        """Return a new dataset resampled to a target ``dt`` (all sensors).

        Pass ``dt`` (``fs`` is an optional alternative). Every read from the
        returned dataset is resampled to this rate. Prints a short summary when
        ``verbose``, with the rescaled per-sensor sample counts.
        """
        from . import resample_service as _resample
        target = _resample.target_dt(dt=dt, fs=fs)

        new = copy.copy(self)
        old_dt, old_fs = self.dt, self.fs
        new._resample_dt = target
        # Fresh cache so resampled results never collide with the originals.
        new._cache_obj = ResultCache()
        new._cache = new._cache_obj._store
        new._signal_store = {}

        # The resampled dataset reports the new rate and the rescaled counts.
        ratio = (old_dt / target) if (old_dt and target) else 1.0
        new.dt = target
        new.fs = 1.0 / target
        new.n_samples = {d: int(round(n * ratio)) for d, n in self.n_samples.items()}
        new.max_points = max(new.n_samples.values()) if new.n_samples else 0

        if self.verbose:
            sep = "-" * 60
            print(sep)
            print("resample : dt %.6f -> %.6f s   |   fs %.4f -> %.4f Hz"
                  % (old_dt, target, old_fs, new.fs))
            print("max points: %s samples/axis (largest device, rescaled)"
                  % format(new.max_points, ","))
            for d in new.devices:
                print("  %-10s -> %s samples/axis"
                      % (d, format(new.n_samples.get(d, 0), ",")))
            print(sep)
        return new

    # -- broadcast helper ----------------------------------------------

    def _broadcast(self, method_name, **kwargs):
        """Run a per-device handle method over every device, return a dict."""
        def run(dev):
            # device() carries the dataset window so broadcasts read the same
            # conditioned window as ds.MOF00135 and share its cached signal.
            handle = self.device(dev)
            return getattr(handle, method_name)(**kwargs)

        if self.parallel:
            from ..batch.processor import BatchEngine
            engine = BatchEngine(n_jobs=self.n_jobs, parallel=True)
            try:
                results = engine.map(run, self.devices)
                return dict(zip(self.devices, results))
            except NotImplementedError:
                # Batch engine not available; fall back to a serial loop.
                pass
        return {dev: run(dev) for dev in self.devices}

    # -- broadcast analysis (all devices) ------------------------------
    # Each one runs per device through the batch engine and returns a dict
    # keyed by device id. Per-sensor variants live on DeviceHandle.

    def newmark(self, component="x", **kwargs):
        """Newmark response spectrum for every device. See DeviceHandle.newmark."""
        return self._broadcast("newmark", component=component, **kwargs)

    def rotd(self, **kwargs):
        """RotD spectrum for every device. See DeviceHandle.rotd."""
        return self._broadcast("rotd", **kwargs)

    def arias(self, component="x", **kwargs):
        """Arias intensity for every device. See DeviceHandle.arias."""
        return self._broadcast("arias", component=component, **kwargs)

    def fourier(self, component="x", **kwargs):
        """Fourier spectrum for every device. See DeviceHandle.fourier."""
        return self._broadcast("fourier", component=component, **kwargs)

    def psd(self, component="x", **kwargs):
        """PSD for every device. See DeviceHandle.psd."""
        return self._broadcast("psd", component=component, **kwargs)

    def peaks(self, component="all", **kwargs):
        """PGA/PGV/PGD for every device. See DeviceHandle.peaks."""
        return self._broadcast("peaks", component=component, **kwargs)

    def ambient_mean(self, config, component="x"):
        """Ambient mean spectrum for every device. See DeviceHandle.ambient_mean."""
        return self._broadcast("ambient_mean", config=config, component=component)

    # -- building characterization (multi-sensor) ----------------------
    # These use the sensor geometry (config.SENSOR_GEOMETRY) and work across
    # all sensors, not just a pair. See the building.* modules.

    def _read_component(self, device, component):
        """Read one device and return one acceleration component array.

        Goes through device() so the dataset window and conditioning pipeline
        apply (building methods read the same windowed signal as the rest).
        """
        return self.device(device)._signal().component(component)

    @staticmethod
    def _align(*arrays):
        """Trim arrays to their common length.

        Different sensors can hold a slightly different number of samples (each
        device's .h5 files have independent lengths), so any operation that
        combines two signals sample-by-sample must align them first.
        """
        n = min(a.shape[0] for a in arrays)
        return [a[:n] for a in arrays]

    def transfer_function(self, numerator=None, denominator=None, base=None,
                          floors="all", component="x", **kwargs):
        """Floor/base transfer function, single pair or stacked over the array.

        Give ``numerator``/``denominator`` for one pair, or ``base`` plus
        ``floors`` to stack the FRF of every floor against the base.
        See building.transfer_function.
        """
        from ..building import transfer_function as _tf

        if base is not None:
            base_sig = self._read_component(base, component)
            if floors == "all":
                floor_devices = [d for d in self.devices if d != base]
            else:
                floor_devices = list(floors)
            signals = {d: self._read_component(d, component)
                       for d in floor_devices}
            return _tf.stack(signals, base_sig, self.dt, **kwargs)

        num = self._read_component(numerator, component)
        den = self._read_component(denominator, component)
        return _tf.compute(num, den, self.dt, **kwargs)

    def coherence(self, sensor_a, sensor_b, component="x", **kwargs):
        """Coherence between two sensors. See building.coherence.compute."""
        from ..building import coherence as _coh
        a = self._read_component(sensor_a, component)
        b = self._read_component(sensor_b, component)
        return _coh.compute(a, b, self.dt, **kwargs)

    def coherence_matrix(self, component="x", **kwargs):
        """Coherence between every pair of sensors. See building.coherence.matrix."""
        from ..building import coherence as _coh
        signals = {d: self._read_component(d, component) for d in self.devices}
        return _coh.matrix(signals, self.dt, **kwargs)

    def modal_frequencies(self, component="x", **kwargs):
        """Modal frequencies shared by the sensors. See building.modal."""
        from ..building import modal as _modal
        signals = {d: self._read_component(d, component) for d in self.devices}
        return _modal.modal_frequencies(signals, self.dt, **kwargs)

    def mode_shapes(self, component="x", **kwargs):
        """Mode shapes (amplitude/phase per floor). See building.modal.mode_shapes."""
        from ..building import modal as _modal
        signals = {d: self._read_component(d, component) for d in self.devices}
        return _modal.mode_shapes(signals, settings.SENSOR_GEOMETRY, self.dt,
                                  component=component, **kwargs)

    def torsion(self, floor, component="x", **kwargs):
        """Torsion of a floor from its sensor pair. See building.torsion."""
        from ..building import geometry as _geom
        from ..building import torsion as _torsion

        geometry = settings.SENSOR_GEOMETRY
        by_floor = _geom.sensors_by_floor(geometry)
        members = [d for d in by_floor.get(floor, []) if d in self.devices]
        if len(members) < 2:
            raise ValueError("torsion: floor %r needs two sensors, found %s"
                             % (floor, members))
        dev_a, dev_b = members[0], members[1]

        # Rotate each sensor's horizontals into the common building frame.
        sig_a = self.device(dev_a)._signal()
        sig_b = self.device(dev_b)._signal()
        az_a = geometry[dev_a].get("azimuth", 0.0) or 0.0
        az_b = geometry[dev_b].get("azimuth", 0.0) or 0.0
        ax_a, ay_a = _geom.rotate_to_common(sig_a.acc_x, sig_a.acc_y, az_a)
        ax_b, ay_b = _geom.rotate_to_common(sig_b.acc_x, sig_b.acc_y, az_b)
        comp_a = ax_a if component == "x" else ay_a
        comp_b = ax_b if component == "x" else ay_b
        comp_a, comp_b = self._align(comp_a, comp_b)

        distance = _geom.plan_distance(geometry, dev_a, dev_b)
        theta = _torsion.floor_rotation(comp_a, comp_b, distance,
                                        component=component)
        spec = _torsion.torsional_spectrum(theta, self.dt, **kwargs)
        ratio = _torsion.torsion_ratio(theta, comp_a, distance / 2.0)

        return {
            "floor": floor,
            "devices": (dev_a, dev_b),
            "theta": theta,
            "torsional_freq": spec["torsional_freq"],
            "freqs": spec["freqs"],
            "spectrum": spec["spectrum"],
            "torsion_ratio": ratio["max_ratio"],
            "ratio": ratio["ratio"],
        }

    def interstory_drift(self, upper, lower, component="x", **kwargs):
        """Interstory drift between two floors. See building.drift."""
        from ..building import drift as _drift
        sig_u = self.device(upper)._signal().derive()
        sig_l = self.device(lower)._signal().derive()
        disp_u = getattr(sig_u, "disp_" + component)
        disp_l = getattr(sig_l, "disp_" + component)
        disp_u, disp_l = self._align(disp_u, disp_l)
        return _drift.interstory_drift(disp_u, disp_l, **kwargs)

    def drift_profile(self, component="x", **kwargs):
        """Drift profile along the height. See building.drift.drift_profile."""
        from ..building import drift as _drift
        from ..building import geometry as _geom

        geometry = settings.SENSOR_GEOMETRY
        ordered = _geom.order_by_height(geometry, self.devices)
        floor_heights = _geom.heights(geometry, ordered)
        disps = {}
        for dev in ordered:
            sig = self.device(dev)._signal().derive()
            disps[dev] = getattr(sig, "disp_" + component)
        # Align every floor to the common sample count (lengths differ slightly).
        aligned = self._align(*disps.values())
        disps = {dev: arr for dev, arr in zip(disps.keys(), aligned)}
        return _drift.drift_profile(disps, floor_heights, **kwargs)

    def base_rocking(self, **kwargs):
        """Base rocking from the base sensor. See building.base_rocking."""
        from ..building import base_rocking as _rocking
        from ..building import geometry as _geom

        geometry = settings.SENSOR_GEOMETRY
        by_floor = _geom.sensors_by_floor(geometry)
        base_devices = [d for d in by_floor.get(-1, []) if d in self.devices]
        if not base_devices:
            raise ValueError("base_rocking: no base sensor (floor -1) found")
        sig = self.device(base_devices[0])._signal()
        return _rocking.compute(sig.acc_z, self.dt, **kwargs)

    def amplification(self, ref, others, basis="fourier", component="x", **kwargs):
        """Spectral amplification between sensors. See ambient.amplification."""
        from ..ambient import amplification as _amp
        ref_sig = self._read_component(ref, component)
        other_sigs = {d: self._read_component(d, component) for d in others}
        config = kwargs.pop("config", None)
        return _amp.compute(ref_sig, other_sigs, self.dt, basis=basis,
                            config=config, **kwargs)

    # -- export --------------------------------------------------------

    def export_h5(self, path, analyses=None, components="all"):
        """Export every cached result to a self-describing .h5 with Provenance.

        Parameters
        ----------
        path : str
            Output .h5 path.
        analyses : list of str or None
            Restrict to these analyses; ``None`` exports everything cached.
        components : {"x", "y", "z", "all"}, default "all"

        Notes
        -----
        Delegates to ``io.exporter.export_dataset``. The per-sensor form is
        ``ds.MOF00135.export_h5(...)``.
        """
        from ..io import exporter
        return exporter.export_dataset(self, path, analyses=analyses,
                                       components=components)

    # -- batch sweep ---------------------------------------------------

    def sweep(self, devices="all", length="60min", overlap=0.0,
              analyses=None, component="x", config=None):
        """Run a set of analyses over fixed time blocks for the given devices.

        Parameters
        ----------
        devices : "all" or list of str
        length : str or float
            Block size, e.g. "60min", "300sec", "2hour", or seconds.
        overlap : float, default 0.0
            Fractional overlap between consecutive blocks.
        analyses : list of str
            Analysis names to run on each block (e.g. ["newmark", "arias"]).
        component : str, default "x"
        config : dict or None
            Configuration passed to the ambient analyses.
        """
        from datetime import timedelta

        from . import window_service as _window

        if self.time_span is None:
            return {}
        if devices == "all":
            devices = list(self.devices)
        if analyses is None:
            analyses = ["newmark"]

        block = _window.parse_duration(length)
        step = block * (1.0 - overlap) if overlap else block

        # Build the block boundaries across the whole span.
        t0, t_end = self.time_span
        blocks = []
        start = t0
        while start < t_end:
            stop = start + timedelta(seconds=block)
            blocks.append((start, stop))
            start = start + timedelta(seconds=step)

        results = {}
        for dev in devices:
            results[dev] = []
            for (b0, b1) in blocks:
                handle = DeviceHandle(self, dev).get_window(b0, b1)
                block_res = {"window": (b0, b1)}
                for analysis in analyses:
                    method = getattr(handle, analysis)
                    if analysis in ("hvsr", "amplification"):
                        block_res[analysis] = method(config=config)
                    else:
                        block_res[analysis] = method(component=component)
                results[dev].append(block_res)
        return results
