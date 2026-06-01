"""DeviceHandle: a thin per-sensor view returned by ``ds.MOF00135``.

It binds a device id to the parent :class:`SensorDataset` and exposes the full
analysis API for that single sensor. Every result is stored in the parent
dataset's cache, so asking for it again returns the cached value.
"""

import os

import numpy as np

from ..model.signal_data import SignalData
from . import window_service as _window
from .cache import _freeze


class DeviceHandle:
    """Per-sensor view over a :class:`SensorDataset`.

    Parameters
    ----------
    dataset : SensorDataset
        Parent dataset (owns the file index and the result cache).
    device : str
        Device id this handle is bound to.
    window : tuple or None, default None
        Optional ``(t_start, t_end)`` restricting every read to a time window.
    """

    def __init__(self, dataset, device, window=None):
        self.dataset = dataset
        self.device = device
        # Stored as a private attribute so it does not shadow the window()
        # method (the public API exposes window() to set bounds on a copy).
        self._window = window
        # Ordered processing pipeline: list of (step_name, kwargs) applied to
        # the freshly read SignalData. resample is carried separately so it is
        # applied right after the read (before any pipeline step).
        self._pipeline = []
        self._resample_dt = None
        # Light per-handle cache of the built SignalData keyed by components.
        self._signal_cache = {}

    # -- internal: copy / read / build ---------------------------------

    def _clone(self):
        """Return a copy of this handle (shares dataset, copies the pipeline)."""
        new = DeviceHandle(self.dataset, self.device, window=self._window)
        new._pipeline = list(self._pipeline)
        new._resample_dt = self._resample_dt
        return new

    def _pipeline_steps(self):
        """The full pipeline: the dataset's steps first, then the handle's."""
        return list(getattr(self.dataset, "_pipeline", [])) + self._pipeline

    def _signal_state(self):
        """Hashable fingerprint of the source signal for cache keys."""
        return (tuple(self._pipeline_steps()), self._window, self._resample_dt)

    def _files(self):
        """Resolve the file paths this handle reads from (window or all)."""
        index = self.dataset._index
        if self._window is not None:
            files = index.in_range(*self._window)
        else:
            files = [p for (_when, p) in index.files]
        return files

    def _read_signal(self, components="all", remove_mean=False):
        """Read the device acceleration and build a :class:`SignalData`."""
        files = self._files()
        out = self.dataset._reader.read(files, self.device, components="all",
                                        remove_mean=remove_mean)
        acc = out["acc"]
        sig = SignalData(
            device=self.device,
            acc_x=acc[:, 0],
            acc_y=acc[:, 1],
            acc_z=acc[:, 2],
            time=out["time"],
            dt=out["dt"],
            axes=out["axes"],
        )
        # Dataset-level resample (carried by ds.resample) applied on read.
        res_dt = self._resample_dt
        if res_dt is None:
            res_dt = getattr(self.dataset, "_resample_dt", None)
        if res_dt is not None:
            sig = sig.resample(dt=res_dt)

        # Absolute time per sample, anchored at the first file's start datetime.
        # Lets plots show real dates instead of seconds from zero.
        if files:
            start = self.dataset._index.parse_date(os.path.basename(files[0]))
            if start is not None:
                sig.t_abs = (np.datetime64(start)
                             + (sig.time * 1e9).astype("timedelta64[ns]"))

        # Trim to the exact window. in_range returns the files overlapping the
        # window (whole 10-min files), so here we cut to the requested bounds.
        if self._window is not None and getattr(sig, "t_abs", None) is not None:
            t0 = np.datetime64(self._window[0])
            t1 = np.datetime64(self._window[1])
            mask = (sig.t_abs >= t0) & (sig.t_abs <= t1)
            for name in ("acc_x", "acc_y", "acc_z"):
                arr = getattr(sig, name)
                if arr is not None:
                    setattr(sig, name, arr[mask])
            sig.t_abs = sig.t_abs[mask]
            sig.time = sig.time[mask]
            if sig.time.size:
                sig.time = sig.time - sig.time[0]   # relative time starts at 0
        return sig

    def _signal(self, components="all", remove_mean=False):
        """Read the signal and apply the processing pipeline in order.

        The built signal is cached on the parent dataset (shared across handles)
        so the read + baseline + filter + derive runs once per sensor and every
        analysis reuses it.
        """
        store = getattr(self.dataset, "_signal_store", None)
        if store is None:                       # standalone handle, no dataset store
            store = self._signal_cache
        cache_key = (self.device, components, remove_mean,
                     _freeze(self._signal_state()))
        cached = store.get(cache_key)
        if cached is not None:
            return cached
        sig = self._read_signal(components=components, remove_mean=remove_mean)
        for step, kw in self._pipeline_steps():
            sig = getattr(sig, step)(**kw)
        store[cache_key] = sig
        return sig

    def _log(self, line):
        """Print an internal line when the parent dataset is verbose."""
        if getattr(self.dataset, "verbose", False):
            print(line)

    def _components(self, component):
        """Resolve a component spec into the list of axis names to run."""
        if component == "all":
            return ["x", "y", "z"]
        return [component]

    def _cached_analysis(self, analysis, params, builder, log):
        """Return a cached analysis result or compute, cache and log it."""
        cache = self.dataset._cache_obj
        key = cache.key(self.device, analysis, params, self._signal_state())
        hit = cache.get(key)
        if hit is not None:
            self._log(log(hit, True))
            return hit
        result = builder()
        cache.set(key, result)
        self._log(log(result, False))
        return result

    def _effective_dt(self):
        """The dt the reads will use (handle resample, dataset resample, native)."""
        return (self._resample_dt
                or getattr(self.dataset, "_resample_dt", None)
                or self.dataset.dt)

    def summary(self):
        """Print the window's data properties (span, duration, fs/dt, samples)."""
        sep = "-" * 60
        dt = self._effective_dt()
        print(sep)
        print("window : %s" % self.device)
        if self._window is not None:
            t0, t1 = self._window
            dur = float((np.datetime64(t1) - np.datetime64(t0)) / np.timedelta64(1, "s"))
            n = self._exact_n(t0, t1, dt)
            label = "  samples : %s / axis"
            print("  span    : %s  ->  %s" % (t0, t1))
        else:
            t0, t1 = self.dataset.time_span if self.dataset.time_span else (None, None)
            dur = self.dataset.duration
            n = int(round(dur / dt)) if dt else 0
            label = "  samples : ~%s / axis (full record)"
            print("  span    : full record  (%s  ->  %s)" % (t0, t1))
        print("  duration: %.1f s" % dur)
        print("  fs / dt : %.4f Hz / %.6f s" % (1.0 / dt, dt))
        print(label % format(n, ","))
        print(sep)

    def _exact_n(self, t0, t1, dt):
        """Exact samples in ``[t0, t1]`` for the effective ``dt`` (matches read)."""
        idx = self.dataset._index
        files = idx.in_range(t0, t1)
        if not files or not dt:
            return 0
        start = idx.parse_date(os.path.basename(files[0]))
        if start is None:
            return 0
        s0 = float((np.datetime64(t0) - np.datetime64(start)) / np.timedelta64(1, "s"))
        s1 = float((np.datetime64(t1) - np.datetime64(start)) / np.timedelta64(1, "s"))
        return max(0, int(np.floor(s1 / dt)) - int(np.ceil(s0 / dt)) + 1)

    def _maybe_summary(self):
        if getattr(self.dataset, "verbose", False):
            self.summary()

    # -- reading and windowing -----------------------------------------

    def signal(self, components="all", mode="auto", workers=4, remove_mean=False):
        """Read the continuous acceleration and return a :class:`SignalData`.

        Parameters
        ----------
        components : {"x", "y", "z", "all"}, default "all"
        mode : {"auto", "ram", "lazy"}, default "auto"
        workers : int, default 4
            Threads used to read the file slices in parallel.
        remove_mean : bool, default False
            Subtract the mean of each component while concatenating.
        """
        sig = self._signal(components=components, remove_mean=remove_mean)
        self._log("[signal] %s n=%d dt=%.6f comps=%s"
                  % (self.device, sig.n, sig.dt, components))
        return sig

    def window(self, start, length):
        """Return a new handle restricted to ``[start, start + length]``.

        Parameters
        ----------
        start : str, datetime or int
            Window start (ISO string, datetime, or sample index).
        length : str or float
            Duration, e.g. "60min", "300sec", "2hour", or seconds.
        """
        new = self._clone()
        new._window = _window.window_from_start(self.dataset._index, self.device,
                                                start, length)
        new._signal_cache = {}
        new._maybe_summary()
        return new

    def get_window(self, t0, t1):
        """Return a new handle restricted to the explicit bounds ``[t0, t1]``."""
        new = self._clone()
        new._window = _window.window_from_bounds(self.dataset._index, self.device,
                                                 t0, t1)
        new._signal_cache = {}
        new._maybe_summary()
        return new

    def resample(self, dt=None, fs=None):
        """Return a new handle resampled to a target ``dt`` or ``fs``."""
        from . import resample_service as _resample
        new = self._clone()
        new._resample_dt = _resample.target_dt(dt=dt, fs=fs)
        new._signal_cache = {}
        return new

    # -- pipeline steps (each returns a new handle) --------------------

    def baseline(self, **kwargs):
        """Return a new handle with a baseline-correction step appended."""
        new = self._clone()
        new._pipeline.append(("baseline", dict(kwargs)))
        new._signal_cache = {}
        return new

    def filter(self, fmin, fmax, **kwargs):
        """Return a new handle with a band-pass filter step appended."""
        kw = dict(kwargs)
        kw["fmin"] = fmin
        kw["fmax"] = fmax
        new = self._clone()
        new._pipeline.append(("filter", kw))
        new._signal_cache = {}
        return new

    def derive(self, **kwargs):
        """Return a new handle with an integration (acc->vel->disp) step appended."""
        new = self._clone()
        new._pipeline.append(("derive", dict(kwargs)))
        new._signal_cache = {}
        return new

    # -- seismic -------------------------------------------------------

    def newmark(self, component="x", source="acc", zeta=0.05,
                max_period=5.01, dT=0.01, factor=1.0):
        """Newmark response spectrum (linear acceleration, beta method).

        Parameters
        ----------
        component : {"x", "y", "z", "all"}, default "x"
        source : str, default "acc"
            Which signal to use as ground acceleration.
        zeta : float, default 0.05
            Damping ratio.
        max_period : float, default 5.01
            Maximum period in seconds.
        dT : float, default 0.01
            Period step in seconds.
        factor : float, default 1.0
            Presentation multiplier applied to the acceleration spectra
            (PSa, Sa). Use ``1/9.81`` to show them in g. PSv (m/s) and Sd (m)
            are not affected.

        Returns
        -------
        dict
            Keys T, PSa, PSv, Sd, Sv, Sa, u, v, a, at (or a dict per axis if
            ``component="all"``).
        """
        from ..seismic import newmark as _newmark

        if component == "all":
            return {c: self.newmark(component=c, source=source, zeta=zeta,
                                    max_period=max_period, dT=dT, factor=factor)
                    for c in ["x", "y", "z"]}

        params = dict(component=component, source=source, zeta=zeta,
                      max_period=max_period, dT=dT, factor=factor)

        def builder():
            sig = self._signal()
            acc = sig.component(component)
            return _newmark.compute(acc, sig.dt, zeta=zeta,
                                    max_period=max_period, dT=dT, factor=factor)

        def log(res, cached):
            return ("[newmark] %s comp=%s zeta=%s Tmax=%s dT=%s -> %d periods (%s)"
                    % (self.device, component, zeta, max_period, dT,
                       len(res["T"]), "cached" if cached else "computed"))

        return self._cached_analysis("newmark", params, builder, log)

    def rotd(self, comp_x="x", comp_y="y", rotd=50, damping=0.05,
             angle_step=5, max_period=5.01, dT=0.01):
        """Rotated response spectrum percentile (ROTD).

        Parameters
        ----------
        comp_x, comp_y : str
            The two horizontal components to rotate.
        rotd : int or sequence of int, default 50
            Percentile(s) to return, e.g. ``50`` or ``[0, 50, 100]``. The full
            0-180 PSa matrix is computed once and cached, so several percentiles
            cost the same as one.
        damping : float, default 0.05
        angle_step : int, default 5
            Rotation step in degrees (0 to 180).
        max_period : float, default 5.01
        dT : float, default 0.01
        """
        from ..seismic import rotd as _rotd

        params = dict(comp_x=comp_x, comp_y=comp_y, rotd=rotd, damping=damping,
                      angle_step=angle_step, max_period=max_period, dT=dT)

        def builder():
            sig = self._signal()
            ax = sig.component(comp_x)
            ay = sig.component(comp_y)
            return _rotd.compute(ax, ay, sig.dt, rotd=rotd, damping=damping,
                                 angle_step=angle_step, max_period=max_period,
                                 dT=dT)

        def log(res, cached):
            return ("[rotd] %s %s/%s rotd=%s -> %d periods (%s)"
                    % (self.device, comp_x, comp_y, rotd, len(res["T"]),
                       "cached" if cached else "computed"))

        return self._cached_analysis("rotd", params, builder, log)

    def arias(self, component="x", low=5, high=95):
        """Arias intensity curve and significant duration.

        Parameters
        ----------
        component : {"x", "y", "z", "all"}, default "x"
        low, high : float, default 5, 95
            Percentages bounding the significant duration.
        """
        from ..seismic import arias as _arias

        if component == "all":
            return {c: self.arias(component=c, low=low, high=high)
                    for c in ["x", "y", "z"]}

        params = dict(component=component, low=low, high=high)

        def builder():
            sig = self._signal()
            return _arias.compute(sig.component(component), sig.dt,
                                  low=low, high=high)

        def log(res, cached):
            return ("[arias] %s comp=%s low=%s high=%s (%s)"
                    % (self.device, component, low, high,
                       "cached" if cached else "computed"))

        return self._cached_analysis("arias", params, builder, log)

    def cav(self, component="x"):
        """Cumulative Absolute Velocity (integral of |acceleration|)."""
        from ..seismic import cav as _cav

        if component == "all":
            return {c: self.cav(component=c) for c in ["x", "y", "z"]}

        params = dict(component=component)

        def builder():
            sig = self._signal()
            return _cav.compute(sig.component(component), sig.dt)

        def log(res, cached):
            return ("[cav] %s comp=%s (%s)"
                    % (self.device, component, "cached" if cached else "computed"))

        return self._cached_analysis("cav", params, builder, log)

    def housner(self, component="x", T1=0.1, T2=2.5, zeta=0.05):
        """Housner spectral intensity (integral of PSv between T1 and T2)."""
        from ..seismic import housner as _housner

        if component == "all":
            return {c: self.housner(component=c, T1=T1, T2=T2, zeta=zeta)
                    for c in ["x", "y", "z"]}

        params = dict(component=component, T1=T1, T2=T2, zeta=zeta)

        def builder():
            sig = self._signal()
            return _housner.compute(sig.component(component), sig.dt,
                                    T1=T1, T2=T2, zeta=zeta)

        def log(res, cached):
            return ("[housner] %s comp=%s T1=%s T2=%s (%s)"
                    % (self.device, component, T1, T2,
                       "cached" if cached else "computed"))

        return self._cached_analysis("housner", params, builder, log)

    def peaks(self, component="all"):
        """Peak ground values PGA / PGV / PGD (needs derived vel/disp)."""
        from ..seismic import peaks as _peaks

        if component == "all":
            return {c: self.peaks(component=c) for c in ["x", "y", "z"]}

        params = dict(component=component)

        def builder():
            # Derive once so velocity/displacement are available for PGV/PGD.
            sig = self._signal().derive()
            acc = sig.component(component)
            vel = getattr(sig, "vel_" + component)
            disp = getattr(sig, "disp_" + component)
            return _peaks.compute(acc, vel, disp)

        def log(res, cached):
            return ("[peaks] %s comp=%s PGA=%.4g (%s)"
                    % (self.device, component, res["PGA"],
                       "cached" if cached else "computed"))

        return self._cached_analysis("peaks", params, builder, log)

    def fourier(self, component="x", num_frequencies=4, prominence=1e-6,
                distance_frac=0.02, smooth=None, bexp=40):
        """Fourier amplitude spectrum and dominant frequencies.

        Parameters
        ----------
        component : {"x", "y", "z", "all"}, default "x"
        num_frequencies : int, default 4
            How many dominant peaks to return.
        prominence : float, default 1e-6
            Minimum peak prominence.
        distance_frac : float, default 0.02
            Minimum peak spacing as a fraction of the spectrum length.
        smooth : {None, "konno"}, default None
            Optional Konno-Ohmachi smoothing.
        bexp : int, default 40
            Smoothing bandwidth coefficient when ``smooth="konno"``.
        """
        from ..seismic import fourier as _fourier

        if component == "all":
            return {c: self.fourier(component=c,
                                    num_frequencies=num_frequencies,
                                    prominence=prominence,
                                    distance_frac=distance_frac,
                                    smooth=smooth, bexp=bexp)
                    for c in ["x", "y", "z"]}

        params = dict(component=component, num_frequencies=num_frequencies,
                      prominence=prominence, distance_frac=distance_frac,
                      smooth=smooth, bexp=bexp)

        def builder():
            sig = self._signal()
            return _fourier.compute(sig.component(component), sig.dt,
                                    num_frequencies=num_frequencies,
                                    prominence=prominence,
                                    distance_frac=distance_frac,
                                    smooth=smooth, bexp=bexp)

        def log(res, cached):
            return ("[fourier] %s comp=%s nfreq=%d smooth=%s (%s)"
                    % (self.device, component, num_frequencies, smooth,
                       "cached" if cached else "computed"))

        return self._cached_analysis("fourier", params, builder, log)

    def psd(self, component="x", nperseg=256, noverlap=128, window="hann",
            bands=None, detrend="constant"):
        """Power spectral density (Welch) and energy per frequency band.

        Parameters
        ----------
        component : {"x", "y", "z", "all"}, default "x"
        nperseg : int, default 256
        noverlap : int, default 128
        window : str, default "hann"
        bands : list of (float, float) or None
            Frequency bands for the band-energy summary. ``None`` uses
            ``config.settings.PSD["FREQ_BANDS"]``.
        detrend : str, default "constant"
        """
        from ..seismic import psd as _psd

        if component == "all":
            return {c: self.psd(component=c, nperseg=nperseg, noverlap=noverlap,
                                window=window, bands=bands, detrend=detrend)
                    for c in ["x", "y", "z"]}

        params = dict(component=component, nperseg=nperseg, noverlap=noverlap,
                      window=window, bands=bands, detrend=detrend)

        def builder():
            sig = self._signal()
            return _psd.compute(sig.component(component), sig.dt,
                                nperseg=nperseg, noverlap=noverlap,
                                window=window, bands=bands, detrend=detrend)

        def log(res, cached):
            return ("[psd] %s comp=%s nperseg=%d (%s)"
                    % (self.device, component, nperseg,
                       "cached" if cached else "computed"))

        return self._cached_analysis("psd", params, builder, log)

    def stft(self, component="x", nperseg=256, noverlap=224, window="hann",
             fmax=25.0):
        """Short-time Fourier transform (spectrogram)."""
        from ..seismic import stft as _stft

        if component == "all":
            return {c: self.stft(component=c, nperseg=nperseg,
                                 noverlap=noverlap, window=window, fmax=fmax)
                    for c in ["x", "y", "z"]}

        params = dict(component=component, nperseg=nperseg, noverlap=noverlap,
                      window=window, fmax=fmax)

        def builder():
            sig = self._signal()
            return _stft.compute(sig.component(component), sig.dt,
                                 nperseg=nperseg, noverlap=noverlap,
                                 window=window, fmax=fmax)

        def log(res, cached):
            return ("[stft] %s comp=%s nperseg=%d fmax=%s (%s)"
                    % (self.device, component, nperseg, fmax,
                       "cached" if cached else "computed"))

        return self._cached_analysis("stft", params, builder, log)

    def ambient_mean(self, config, component="x"):
        """Ambient mean spectrum for this device.

        Runs the ambient pipeline (STA/LTA windowing -> taper -> FFT ->
        Konno-Ohmachi -> average) on the conditioned signal and returns the
        mean spectrum with its dominant frequency.

        Parameters
        ----------
        config : dict
            Ambient configuration (Fs, STA, LTA, vent, vmin, vmax, p, bexp, ...).
        component : {"x", "y", "z"}, default "x"

        Returns
        -------
        dict
            ``{"freqs": ..., "spectrum": ..., "f_dom": ...}``.
        """
        amb = self.signal(components="all").ambient(config, component=component)
        amb.average()
        f_dom = 1.0 / amb.dominant_period if amb.dominant_period else float("nan")
        freqs = amb.freqs[:, 0] if getattr(amb.freqs, "ndim", 1) == 2 else amb.freqs
        return {"freqs": freqs, "spectrum": amb.mean_spectrum, "f_dom": f_dom}

    def ambient(self, sta=1.0, lta=30.0, vent=20.0, vmin=0.2, vmax=2.5,
                p=0.05, bexp=40, component="x"):
        """Ambient (microtremor) analysis for this device.

        Runs the whole pipeline internally (STA/LTA windowing -> taper -> FFT ->
        Konno-Ohmachi -> mean spectrum) and returns one result dict with
        everything the plots need. The sampling rate is taken from the signal,
        so you pass only the analysis parameters; filtering is your choice when
        you condition the object.

        Parameters
        ----------
        sta, lta : float
            Short- and long-term average windows [s] for the STA/LTA trigger.
        vent : float
            Window length [s].
        vmin, vmax : float
            STA/LTA acceptance band (a window is kept only if its ratio stays
            inside it).
        p : float
            Cosine taper fraction.
        bexp : int
            Konno-Ohmachi smoothing exponent.
        component : {"x", "y", "z"}, default "x"

        Returns
        -------
        dict
            Keys: fs, vmin, vmax, vent, signal, sta_lta_ratio, sta, lta,
            windows_pos, windows_signal, freqs, per_window_spectra, spectrum
            (mean), mean_spectrum, f_dom, dominant_period.
        """
        import numpy as np

        params = dict(sta=sta, lta=lta, vent=vent, vmin=vmin, vmax=vmax, p=p,
                      bexp=bexp, component=component)

        def builder():
            sig = self._signal()
            cfg = {"Fs": 1.0 / sig.dt, "STA": sta, "LTA": lta, "vent": vent,
                   "vmin": vmin, "vmax": vmax, "p": p, "bexp": bexp}
            amb = sig.ambient(cfg, component=component)
            amb.average()
            freqs = (amb.freqs[:, 0]
                     if getattr(amb.freqs, "ndim", 1) == 2 else amb.freqs)
            f_dom = (1.0 / amb.dominant_period
                     if amb.dominant_period else float("nan"))
            return {
                "fs": amb.fs, "vmin": vmin, "vmax": vmax, "vent": vent,
                "signal": amb.signal,
                "sta_lta_ratio": amb.sta_lta_ratio, "sta": amb.sta, "lta": amb.lta,
                "windows_pos": amb.windows_pos, "windows_signal": amb.windows_signal,
                "freqs": freqs, "per_window_spectra": amb.fft_abs,
                "spectrum": amb.mean_spectrum, "mean_spectrum": amb.mean_spectrum,
                "f_dom": f_dom, "dominant_period": amb.dominant_period,
            }

        def log(res, cached):
            return ("[ambient] %s comp=%s T=%.4f s (%s)"
                    % (self.device, component, res["dominant_period"] or float("nan"),
                       "cached" if cached else "computed"))

        return self._cached_analysis("ambient", params, builder, log)

    # -- structural (single sensor side) -------------------------------

    def modal_tracking(self, component="x", window="10min", overlap=0.5,
                       fband=(1.0, 8.0), n_modes=2, smooth="konno", bexp=40):
        """Track modal frequencies over time with a moving window.

        Parameters
        ----------
        component : {"x", "y", "z"}, default "x"
        window : str or float, default "10min"
            Moving window length.
        overlap : float, default 0.5
        fband : (float, float), default (1.0, 8.0)
            Frequency band to search the modes in.
        n_modes : int, default 2
            Number of modes (peaks) to follow.
        smooth : {None, "konno"}, default "konno"
        bexp : int, default 40
        """
        from ..building import modal as _modal

        params = dict(component=component, window=window, overlap=overlap,
                      fband=fband, n_modes=n_modes, smooth=smooth, bexp=bexp)

        def builder():
            sig = self._signal()
            return _modal.tracking(sig.component(component), sig.dt,
                                   window=window, overlap=overlap, fband=fband,
                                   n_modes=n_modes, smooth=smooth, bexp=bexp)

        def log(res, cached):
            return ("[modal_tracking] %s comp=%s window=%s n_modes=%d (%s)"
                    % (self.device, component, window, n_modes,
                       "cached" if cached else "computed"))

        return self._cached_analysis("modal_tracking", params, builder, log)

    def hvsr(self, config, comp_h=("x", "y"), comp_v="z", combine="geometric"):
        """Horizontal-to-Vertical Spectral Ratio (Nakamura)."""
        from ..ambient import hvsr as _hvsr

        params = dict(comp_h=tuple(comp_h), comp_v=comp_v, combine=combine)

        def builder():
            sig = self._signal()
            h1 = sig.component(comp_h[0])
            h2 = sig.component(comp_h[1])
            v = sig.component(comp_v)
            return _hvsr.compute(h1, h2, v, config, combine=combine)

        def log(res, cached):
            return ("[hvsr] %s h=%s v=%s combine=%s (%s)"
                    % (self.device, comp_h, comp_v, combine,
                       "cached" if cached else "computed"))

        return self._cached_analysis("hvsr", params, builder, log)

    def amplification(self, basis="hvsr", config=None, component="x"):
        """Spectral amplification for this sensor (e.g. HVSR)."""
        from ..ambient import hvsr as _hvsr

        params = dict(basis=basis, component=component)

        def builder():
            # For a single sensor the natural amplification basis is HVSR.
            sig = self._signal()
            h1 = sig.component("x")
            h2 = sig.component("y")
            v = sig.component("z")
            return _hvsr.compute(h1, h2, v, config or {}, combine="geometric")

        def log(res, cached):
            return ("[amplification] %s basis=%s (%s)"
                    % (self.device, basis, "cached" if cached else "computed"))

        return self._cached_analysis("amplification", params, builder, log)

    # -- plotting trampolines (thin) -----------------------------------

    def plot_signals(self, components="all", kind="acc", save=None):
        """Plot the time histories of this sensor's signal."""
        from ..plotting import signal_plots
        return signal_plots.plot_signals(self._signal(components), components,
                                         kind=kind, save=save)

    def plot_newmark(self, component="x", quantity="PSa", save=None, **kwargs):
        """Compute and plot the Newmark spectrum."""
        from ..plotting import newmark_plots
        result = self.newmark(component=component, **kwargs)
        return newmark_plots.plot_newmark(result, component=component,
                                          quantity=quantity, save=save)

    def plot_rotd(self, rotd=(0, 50, 100), save=None, **kwargs):
        """Compute and plot the RotD spectrum."""
        from ..plotting import rotd_plots
        result = self.rotd(**kwargs)
        return rotd_plots.plot_rotd(result, rotd=rotd, save=save)

    def plot_fourier(self, component="x", smooth=None, save=None, **kwargs):
        """Compute and plot the Fourier amplitude spectrum."""
        from ..plotting import fourier_plots
        result = self.fourier(component=component, smooth=smooth, **kwargs)
        return fourier_plots.plot_fourier(result, component=component,
                                          smooth=smooth, save=save)

    def plot_stft(self, component="x", save=None, **kwargs):
        """Compute and plot the spectrogram."""
        from ..plotting import stft_plots
        result = self.stft(component=component, **kwargs)
        return stft_plots.plot_stft(result, component=component, save=save)

    def plot_psd(self, component="x", save=None, **kwargs):
        """Compute and plot the power spectral density."""
        from ..plotting import psd_plots
        result = self.psd(component=component, **kwargs)
        return psd_plots.plot_psd(result, component=component, save=save)

    def plot_arias(self, component="x", save=None, **kwargs):
        """Compute and plot the Arias intensity curve."""
        from ..plotting import arias_plots
        result = self.arias(component=component, **kwargs)
        return arias_plots.plot_arias(result, component=component, save=save)

    def plot_modal_tracking(self, component="x", save=None, **kwargs):
        """Compute and plot the modal-frequency tracking."""
        from ..plotting import modal_plots
        result = self.modal_tracking(component=component, **kwargs)
        return modal_plots.plot_modal_tracking(result, save=save)

    # -- export --------------------------------------------------------

    def export_h5(self, path, analyses=None, components="all"):
        """Export this sensor's cached results to a self-describing .h5.

        Parameters
        ----------
        path : str
            Output .h5 path.
        analyses : list of str or None
            Restrict to these analyses; ``None`` exports everything cached.
        components : {"x", "y", "z", "all"}, default "all"

        Notes
        -----
        Delegates to ``io.exporter.export_device``.
        """
        from ..io import exporter
        return exporter.export_device(self, path, analyses=analyses,
                                      components=components)
