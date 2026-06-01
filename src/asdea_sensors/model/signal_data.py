"""SignalData: a lightweight container for one device's continuous signal.

Holds acceleration (and, once derived, velocity and displacement) plus the
time base. The processing steps are decoupled and chainable; each one returns
a new SignalData so the order is up to the caller:

    sig.baseline().filter(0.1, 24.9).derive()

Internal units are SI: acceleration m/s^2, velocity m/s, displacement m.
"""


class SignalData:
    """Continuous signal of a single device.

    Parameters
    ----------
    device : str
        Device id.
    acc_x, acc_y, acc_z : np.ndarray or None
        Acceleration components in m/s^2.
    time : np.ndarray
        Time vector in seconds from the window start.
    dt : float
        Sampling interval in seconds.
    t_abs : np.ndarray or None, default None
        Absolute datetimes for each sample.
    axes : tuple or None, default None
        The physical column mapping ``(ix, iy, iz)`` used to read this device.

    Attributes
    ----------
    vel_x, vel_y, vel_z : np.ndarray or None
        Velocity in m/s (filled by :meth:`derive`).
    disp_x, disp_y, disp_z : np.ndarray or None
        Displacement in m (filled by :meth:`derive`).
    fs : float
        Sampling frequency in Hz.
    n : int
        Number of samples.
    """

    def __init__(self, device, acc_x=None, acc_y=None, acc_z=None,
                 time=None, dt=None, t_abs=None, axes=None):
        self.device = device
        self.acc_x = acc_x
        self.acc_y = acc_y
        self.acc_z = acc_z
        self.vel_x = self.vel_y = self.vel_z = None
        self.disp_x = self.disp_y = self.disp_z = None
        self.time = time
        self.dt = dt
        self.t_abs = t_abs
        self.axes = axes

    @property
    def fs(self):
        """Sampling frequency in Hz."""
        raise NotImplementedError

    @property
    def n(self):
        """Number of samples."""
        raise NotImplementedError

    @property
    def duration(self):
        """Signal duration in seconds."""
        raise NotImplementedError

    # -- decoupled processing steps (each returns a new SignalData) -----

    def baseline(self, method="polynomial", components="all"):
        """Baseline-correct the acceleration only.

        Parameters
        ----------
        method : {"polynomial", "linear", "mean"}, default "polynomial"
            "polynomial" removes the drift with the polynomial correction.
        components : {"x", "y", "z", "all"}, default "all"
        """
        raise NotImplementedError

    def filter(self, fmin, fmax, engine="obspy", order=4, zerophase=True,
               components="all"):
        """Band-pass filter the acceleration only.

        Parameters
        ----------
        fmin, fmax : float
            Band edges in Hz (validated against Nyquist).
        engine : {"obspy", "scipy"}, default "obspy"
        order : int, default 4
            Filter order / corners.
        zerophase : bool, default True
        components : {"x", "y", "z", "all"}, default "all"
        """
        raise NotImplementedError

    def derive(self, method="trapezoid", remove_mean=True, components="all"):
        """Integrate the current acceleration to velocity and displacement.

        Parameters
        ----------
        method : str, default "trapezoid"
            Cumulative integration scheme.
        remove_mean : bool, default True
            Remove the mean before integrating to limit drift.
        components : {"x", "y", "z", "all"}, default "all"
        """
        raise NotImplementedError

    def resample(self, dt=None, fs=None):
        """Return a new SignalData resampled to a target ``dt`` or ``fs``."""
        raise NotImplementedError

    def component(self, name):
        """Return the acceleration array for "x", "y" or "z"."""
        raise NotImplementedError

    # -- analysis entry point ------------------------------------------

    def ambient(self, config, component="x"):
        """Return an :class:`AmbientAnalysis` bound to this signal.

        Parameters
        ----------
        config : dict
            Ambient configuration (Fs, STA, LTA, vent, vmin, vmax, p, bexp,
            f1, f2, ...).
        component : {"x", "y", "z"}, default "x"
        """
        raise NotImplementedError
