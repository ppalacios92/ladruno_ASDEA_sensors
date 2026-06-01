"""Plots of the Fourier amplitude spectrum."""


def _finish(fig, save, default_name):
    """Show the figure or save it under a format/path."""
    import matplotlib.pyplot as plt

    if save is None:
        plt.show()
        return None
    if save.lower() in ("png", "svg", "pdf", "jpg", "jpeg"):
        fname = "{}.{}".format(default_name, save.lower())
    else:
        fname = save
    fig.savefig(fname, bbox_inches="tight")
    plt.close(fig)
    return fname


def plot_fourier(result, component="x", smooth=None, unit=None,
                 figsize=None, xlim=None, ylim=None, save=None):
    """Plot a Fourier spectrum and mark its dominant frequencies.

    Parameters
    ----------
    result : dict
        Output of ``seismic.fourier.compute``.
    component : str, default "x"
    smooth : {None, "konno"}, default None
    unit : str or None, default None
        Y-axis unit label; if None the default "m/s^2 . s" is used.
    figsize : tuple or None, default None
        Figure size; if None a default is used.
    xlim, ylim : tuple or None, default None
        Axis limits applied when not None.
    save : str or None, default None
    """
    import matplotlib.pyplot as plt

    freqs = result["freqs"]
    spectrum = result["spectrum"]
    unit = unit if unit is not None else "m/s^2 . s"

    fig, ax = plt.subplots(figsize=figsize or (10, 4.5))
    ax.plot(freqs, spectrum, lw=0.9, color="C0", label="amplitude")

    dom_freqs = result.get("dom_freqs")
    dom_peaks = result.get("dom_peaks")
    if dom_freqs is not None and dom_peaks is not None:
        ax.plot(dom_freqs, dom_peaks, "rv", ms=8, label="dominant peaks")
        for f, p in zip(dom_freqs, dom_peaks):
            ax.annotate("{:.2f} Hz".format(f), (f, p),
                        textcoords="offset points", xytext=(0, 8),
                        ha="center", fontsize=8)

    ax.set_xlabel("Frequency [Hz]")
    ax.set_ylabel("Fourier amplitude [{}]".format(unit))
    ax.set_title("Fourier amplitude spectrum - component {}".format(component),
                 fontweight="bold")
    ax.grid(True, alpha=0.3)
    ax.legend()
    if xlim is not None:
        ax.set_xlim(xlim)
    if ylim is not None:
        ax.set_ylim(ylim)
    fig.tight_layout()

    return _finish(fig, save, "fourier_{}".format(component))


def plot_fourier_all(dataset, devices=None, start_time=None, end_time=None,
                     components=("x", "y", "z"), baseline=False,
                     fmin=None, fmax=None, smooth=None, bexp=40,
                     overlay_raw=False, group=False, num_frequencies=4,
                     figsize=None, xlim=(0, 25), ylim=None, save=None):
    """Fourier spectra of several sensors over a window (no manual loop).

    Reads each device, baseline-corrects and band-passes it, then computes the
    Fourier amplitude spectrum of each component.

    Parameters
    ----------
    dataset : SensorDataset
    devices : list of str
        Device ids.
    start_time, end_time : datetime or str
        Window applied to every device.
    components : sequence of str, default ("x", "y", "z")
        Components to show (one row each).
    baseline : bool, default True
        Baseline-correct before computing the spectrum.
    fmin, fmax : float, default 0.1, 24.9
        Band-pass edges for the filtered spectrum.
    smooth : {None, "konno"}, default None
    bexp : int, default 40
    overlay_raw : bool, default False
        Also draw the unfiltered (raw) spectrum dashed, to compare filtered vs
        unfiltered. Ignored when ``group=True``.
    group : bool, default False
        ``False`` -> one figure per device. ``True`` -> overlay all devices
        (filtered only), one row per component.
    num_frequencies, figsize, xlim, ylim, save
        Plot controls (xlim defaults to 0-25 Hz).

    Returns
    -------
    list or str or None
    """
    import matplotlib.pyplot as plt

    from ..seismic import fourier as _fourier

    if isinstance(components, str):
        components = (components,)
    devices = list(dataset.devices) if devices is None else list(devices)
    colors = getattr(dataset, "device_colors", {}) or {}

    def spectra(handle):
        sig = handle.signal(components="all")
        out = {}
        for c in components:
            out[c] = _fourier.compute(sig.component(c), sig.dt,
                                      num_frequencies=num_frequencies,
                                      smooth=smooth, bexp=bexp)
        return out

    filt_by_dev, raw_by_dev = {}, {}
    for device in devices:
        base = dataset.device(device)
        if start_time is not None and end_time is not None:
            base = base.get_window(start_time, end_time)
        # The object may already be conditioned (ds.baseline()/filter()); only
        # apply extra steps here when explicitly requested.
        proc = base
        if baseline:
            proc = proc.baseline()
        if fmin is not None and fmax is not None:
            proc = proc.filter(fmin, fmax, engine="scipy")
        filt_by_dev[device] = spectra(proc)
        if overlay_raw and not group:
            raw_by_dev[device] = spectra(base)

    if not group:
        paths = []
        for device in devices:
            fig, axes = plt.subplots(len(components), 1, sharex=True,
                                     figsize=figsize or (10, 2.6 * len(components)))
            if len(components) == 1:
                axes = [axes]
            for ax, c in zip(axes, components):
                fr = filt_by_dev[device][c]
                if overlay_raw:
                    rr = raw_by_dev[device][c]
                    ax.semilogy(rr["freqs"], rr["spectrum"] + 1e-20,
                                lw=0.6, color="0.6", label="raw")
                ax.semilogy(fr["freqs"], fr["spectrum"] + 1e-20,
                            lw=0.9, color="C0",
                            label="filtered %.1f-%.1f Hz" % (fmin, fmax))
                ax.set_ylabel("%s\n[m/s^2 . s]" % c.upper())
                ax.grid(True, alpha=0.3)
                if xlim is not None:
                    ax.set_xlim(xlim)
                if ylim is not None:
                    ax.set_ylim(ylim)
            axes[0].legend(fontsize=8)
            axes[-1].set_xlabel("Frequency [Hz]")
            axes[0].set_title("Fourier spectrum - %s" % device, fontweight="bold")
            fig.tight_layout()
            paths.append(_finish(fig, save, "fourier_all_%s" % device))
        return paths

    # group=True: overlay devices, one row per component.
    fig, axes = plt.subplots(len(components), 1, sharex=True,
                             figsize=figsize or (11, 2.6 * len(components)))
    if len(components) == 1:
        axes = [axes]
    for ax, c in zip(axes, components):
        for k, device in enumerate(devices):
            fr = filt_by_dev[device][c]
            ax.semilogy(fr["freqs"], fr["spectrum"] + 1e-20, lw=0.8,
                        color=colors.get(device, "C%d" % (k % 10)), label=device)
        ax.set_ylabel("%s\n[m/s^2 . s]" % c.upper())
        ax.grid(True, alpha=0.3)
        if xlim is not None:
            ax.set_xlim(xlim)
        if ylim is not None:
            ax.set_ylim(ylim)
    axes[0].legend(loc="upper right", ncol=len(devices), fontsize=8)
    axes[-1].set_xlabel("Frequency [Hz]")
    axes[0].set_title("Fourier spectrum - %d sensors (filtered)" % len(devices),
                      fontweight="bold")
    fig.tight_layout()
    return _finish(fig, save, "fourier_all")
