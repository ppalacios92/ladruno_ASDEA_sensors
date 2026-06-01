"""DeviceHandle: a thin per-sensor view returned by ``ds.MOF00135``.

It binds a device id to the parent :class:`SensorDataset` and exposes the full
analysis API for that single sensor. Every result is stored in the parent
dataset's cache, so asking for it again returns the cached value.
"""


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
        self.window = window

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
        raise NotImplementedError

    def window(self, start, length):
        """Return a new handle restricted to ``[start, start + length]``.

        Parameters
        ----------
        start : str, datetime or int
            Window start (ISO string, datetime, or sample index).
        length : str or float
            Duration, e.g. "60min", "300sec", "2hour", or seconds.
        """
        raise NotImplementedError

    def get_window(self, t0, t1):
        """Return a new handle restricted to the explicit bounds ``[t0, t1]``."""
        raise NotImplementedError

    def resample(self, dt=None, fs=None):
        """Return a new handle resampled to a target ``dt`` or ``fs``."""
        raise NotImplementedError

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
        raise NotImplementedError

    def rotd(self, comp_x="x", comp_y="y", rotd=50, damping=0.05,
             angle_step=5, max_period=5.01, dT=0.01):
        """Rotated response spectrum percentile (ROTD).

        Parameters
        ----------
        comp_x, comp_y : str
            The two horizontal components to rotate.
        rotd : {0, 50, 100}, default 50
            Which percentile to return. The full 0-180 PSa matrix is computed
            once and cached, so other percentiles reuse it.
        damping : float, default 0.05
        angle_step : int, default 5
            Rotation step in degrees (0 to 180).
        max_period : float, default 5.01
        dT : float, default 0.01
        """
        raise NotImplementedError

    def arias(self, component="x", low=5, high=95):
        """Arias intensity curve and significant duration.

        Parameters
        ----------
        component : {"x", "y", "z", "all"}, default "x"
        low, high : float, default 5, 95
            Percentages bounding the significant duration.
        """
        raise NotImplementedError

    def cav(self, component="x"):
        """Cumulative Absolute Velocity (integral of |acceleration|)."""
        raise NotImplementedError

    def housner(self, component="x", T1=0.1, T2=2.5, zeta=0.05):
        """Housner spectral intensity (integral of PSv between T1 and T2)."""
        raise NotImplementedError

    def peaks(self, component="all"):
        """Peak ground values PGA / PGV / PGD (needs derived vel/disp)."""
        raise NotImplementedError

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
        raise NotImplementedError

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
        raise NotImplementedError

    def stft(self, component="x", nperseg=256, noverlap=224, window="hann",
             fmax=25.0):
        """Short-time Fourier transform (spectrogram)."""
        raise NotImplementedError

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
        raise NotImplementedError

    def hvsr(self, config, comp_h=("x", "y"), comp_v="z", combine="geometric"):
        """Horizontal-to-Vertical Spectral Ratio (Nakamura)."""
        raise NotImplementedError

    def amplification(self, basis="hvsr", config=None, component="x"):
        """Spectral amplification for this sensor (e.g. HVSR)."""
        raise NotImplementedError

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
        raise NotImplementedError
