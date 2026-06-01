"""AmbientAnalysis: stateful, step-by-step ambient vibration analysis.

Runs the routines in order (STA/LTA -> window selection -> taper -> FFT ->
Konno-Ohmachi -> average), each step a separate method that stores its output.
You can call the steps one by one to inspect them, or ask for a final result
and the missing steps run lazily in order.

No filtering happens here: the signal is expected to be filtered upstream
with ``SignalData.filter``.
"""

import numpy as np

from . import sta_lta as _sta_lta
from . import window_selector as _window_selector
from . import taper as _taper
from . import fft_windows as _fft_windows
from . import konno_ohmachi as _konno_ohmachi
from . import average as _average


class AmbientAnalysis:
    """Step-by-step ambient analysis bound to one signal component.

    Parameters
    ----------
    signal : np.ndarray
        Single-component signal (already baseline-corrected / filtered).
    config : dict
        Configuration: Fs, STA, LTA, vent, vmin, vmax, p, bexp, f1, f2,
        vent_seismic.

    Attributes
    ----------
    sta_lta_ratio, sta, lta : np.ndarray
        Filled by :meth:`sta_lta`.
    windows_signal, windows_time, win_ids, windows_pos : np.ndarray
        Filled by :meth:`select_windows`.
    taper_window : np.ndarray
    fft_complex, fft_abs, freqs : np.ndarray
    smoothed : np.ndarray
    mean_spectrum : np.ndarray
    dominant_period : float
    """

    def __init__(self, signal, config):
        self.signal = np.asarray(signal, dtype=float)
        self.config = config

        # Sampling frequency: explicit "Fs" in config, else from "dt".
        if "Fs" in config:
            self.fs = float(config["Fs"])
        elif "dt" in config:
            self.fs = 1.0 / float(config["dt"])
        else:
            raise KeyError("config must provide 'Fs' or 'dt'")

        # Step outputs.
        self.sta_lta_ratio = self.sta = self.lta = None
        self.windows_signal = self.windows_time = None
        self.win_ids = self.windows_pos = None
        self.taper_window = self.tapered_windows = None
        self.freqs = self.fft_complex = self.fft_abs = None
        self.smoothed = None
        self.mean_spectrum = None
        self.dominant_period = None

        # Names of completed steps, in order.
        self._done = []

    def sta_lta(self):
        """Step 1: compute the STA/LTA ratio.

        The signal is normalized first, exactly as AmbientSoilPeriod's
        BuildPeriod did: remove the mean, divide by the standard deviation, then
        by the peak amplitude. The windows are still cut from the original
        signal in ``select_windows``; only the ratio uses the normalized copy.
        """
        sta = float(self.config["STA"])
        lta = float(self.config["LTA"])

        v = self.signal - np.mean(self.signal)
        std = np.std(v)
        if std > 0:
            v = v / std
        peak = np.max(np.abs(v))
        if peak > 0:
            v = v / peak
        self.signal_normalized = v

        self.sta_lta_ratio, self.sta, self.lta = _sta_lta.compute(
            v, self.fs, sta, lta)
        if "sta_lta" not in self._done:
            self._done.append("sta_lta")
        print("- sta_lta: ratio computed (STA=%g s, LTA=%g s)" % (sta, lta))
        return self

    def select_windows(self, manual=None):
        """Step 2: select windows by STA/LTA, or use a manual list of bounds."""
        if "sta_lta" not in self._done:
            self.sta_lta()

        n = len(self.signal)
        time = np.arange(n) / self.fs

        if manual is not None:
            # Build windows from explicit (t0, t1) bounds.
            cols_t, cols_v, positions, ids = [], [], [], []
            for k, (t0, t1) in enumerate(manual):
                a = int(round(t0 * self.fs))
                b = int(round(t1 * self.fs))
                a = max(a, 0)
                b = min(b, n)
                if b <= a:
                    continue
                cols_t.append(time[a:b])
                cols_v.append(self.signal[a:b])
                positions.append(a)
                ids.append(k)
            self.windows_time = np.column_stack(cols_t) if cols_t else np.empty((0, 0))
            self.windows_signal = np.column_stack(cols_v) if cols_v else np.empty((0, 0))
            self.windows_pos = np.array(positions)
            self.win_ids = np.array(ids)
        elif self.config.get("vent_seismic", False):
            # Single full-length window.
            self.windows_time = time[:, None]
            self.windows_signal = self.signal[:, None]
            self.windows_pos = np.array([0])
            self.win_ids = np.array([0])
        else:
            MT, MV, positions, ids = _window_selector.compute(
                self.fs, time, self.signal, self.sta_lta_ratio,
                float(self.config["vent"]),
                float(self.config["vmin"]),
                float(self.config["vmax"]),
            )
            if MV.ndim != 2 or MV.shape[1] == 0:
                # No window passed the STA/LTA test (typically the analysis
                # window is short relative to vent). Fall back to a single
                # full-length window so the downstream steps still run.
                import warnings
                warnings.warn("ambient: no STA/LTA window selected; using the "
                              "whole signal as one window")
                self.windows_time = time[:, None]
                self.windows_signal = self.signal[:, None]
                self.windows_pos = np.array([0])
                self.win_ids = np.array([0])
            else:
                self.windows_time = MT
                self.windows_signal = MV
                self.windows_pos = positions
                self.win_ids = ids

        if "select_windows" not in self._done:
            self._done.append("select_windows")
        n_win = self.windows_signal.shape[1] if self.windows_signal.ndim == 2 else 0
        print("- select_windows: %d window(s) selected" % n_win)
        return self

    def taper(self):
        """Step 3: apply the Tukey taper to the selected windows."""
        if "select_windows" not in self._done:
            self.select_windows()
        p = float(self.config["p"])
        self.tapered_windows, self.taper_window = _taper.compute(
            self.windows_signal, p)
        if "taper" not in self._done:
            self._done.append("taper")
        print("- taper: Tukey taper applied (p=%g)" % p)
        return self

    def fft(self, apply_filter=False):
        """Step 4: FFT of each window."""
        if "taper" not in self._done:
            self.taper()
        f1 = float(self.config["f1"])
        f2 = float(self.config["f2"])
        self.freqs, self.fft_complex, self.fft_abs = _fft_windows.compute(
            self.fs, self.tapered_windows, apply_filter, f1, f2)
        if "fft" not in self._done:
            self._done.append("fft")
        print("- fft: per-window FFT computed")
        return self

    def smooth(self):
        """Step 5: Konno-Ohmachi smoothing of the per-window spectra."""
        if "fft" not in self._done:
            self.fft()
        bexp = float(self.config["bexp"])
        self.smoothed = _konno_ohmachi.compute(self.freqs, self.fft_abs, bexp)
        if "smooth" not in self._done:
            self._done.append("smooth")
        print("- smooth: Konno-Ohmachi smoothing applied (bexp=%g)" % bexp)
        return self

    def average(self):
        """Step 6: average the smoothed spectra into the mean spectrum."""
        if "smooth" not in self._done:
            self.smooth()
        self.mean_spectrum = _average.compute(self.smoothed)

        # Dominant period from the peak of the mean spectrum.
        freq_axis = self.freqs[:, 0] if self.freqs.ndim == 2 else self.freqs
        peak = int(np.argmax(self.mean_spectrum))
        f_peak = freq_axis[peak]
        self.dominant_period = 1.0 / f_peak if f_peak > 0 else float("inf")

        if "average" not in self._done:
            self._done.append("average")
        print("- average: mean spectrum computed (T=%.4f s)" % self.dominant_period)
        return self
