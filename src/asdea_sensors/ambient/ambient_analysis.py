"""AmbientAnalysis: stateful, step-by-step ambient vibration analysis.

Runs the routines in order (STA/LTA -> window selection -> taper -> FFT ->
Konno-Ohmachi -> average), each step a separate method that stores its output.
You can call the steps one by one to inspect them, or ask for a final result
and the missing steps run lazily in order.

No filtering happens here: the signal is expected to be filtered upstream
with ``SignalData.filter``.
"""


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
        self.signal = signal
        self.config = config

    def sta_lta(self):
        """Step 1: compute the STA/LTA ratio."""
        raise NotImplementedError

    def select_windows(self, manual=None):
        """Step 2: select windows by STA/LTA, or use a manual list of bounds."""
        raise NotImplementedError

    def taper(self):
        """Step 3: apply the Tukey taper to the selected windows."""
        raise NotImplementedError

    def fft(self, apply_filter=False):
        """Step 4: FFT of each window."""
        raise NotImplementedError

    def smooth(self):
        """Step 5: Konno-Ohmachi smoothing of the per-window spectra."""
        raise NotImplementedError

    def average(self):
        """Step 6: average the smoothed spectra into the mean spectrum."""
        raise NotImplementedError
