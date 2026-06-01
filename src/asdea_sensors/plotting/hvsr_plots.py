"""HVSR (Nakamura) plots: mean H/V + log-normal bands + per-window curves + f0.

Mirrors Geopsy's H/V panel: the per-window ratios in light grey, the mean curve
(geometric) with its +/-1 sigma band, and a vertical marker at f0.

``plot_hvsr`` draws one result; ``plot_hvsr_all`` draws ``{device: result}``
(from ``ds.hvsr(...)``) as a grid, one panel per sensor.
"""

import numpy as np

from ._panels import _finish


def _draw_hvsr(ax, result, *, show_windows=True, logx=True, color="C0"):
    """Draw one HVSR result on ``ax``. Returns nothing."""
    f = np.asarray(result["freqs"], float)
    hv = np.asarray(result["HV"], float)
    lo = np.asarray(result["HV_low"], float)
    hi = np.asarray(result["HV_high"], float)
    f0 = float(result.get("f0", 0.0))
    f0_std = float(result.get("f0_std", 0.0))
    m = f > 0
    plot = ax.semilogx if logx else ax.plot

    if show_windows and result.get("per_window_HV") is not None:
        r = np.asarray(result["per_window_HV"], float)
        for k in range(r.shape[1]):
            plot(f[m], r[m, k], color="0.75", lw=0.5, alpha=0.6, zorder=1)

    ax.fill_between(f[m], lo[m], hi[m], color=color, alpha=0.2, zorder=2,
                    label=r"$\pm1\sigma$")
    plot(f[m], hv[m], color=color, lw=2.0, zorder=3, label="mean H/V")

    if f0 > 0:
        label = "f0 = %.2f Hz" % f0
        if f0_std > 1.0:
            # f0_std is the log-normal (multiplicative) std; show the band as an
            # explicit Hz range [f0/sigma, f0*sigma] instead of the cryptic "x/".
            label += "  [%.2f-%.2f Hz]" % (f0 / f0_std, f0 * f0_std)
        ax.axvline(f0, color="r", ls="--", lw=1.2, zorder=4, label=label)
    ax.grid(True, which="both", alpha=0.3)


def plot_hvsr(result, *, show_windows=True, logx=True, figsize=None,
              xlim=None, ylim=None, save=None):
    """Plot one HVSR result (see :func:`ambient.nakamura.compute`).

    Parameters
    ----------
    result : dict
        Keys ``freqs, HV, HV_low, HV_high, f0, f0_std, per_window_HV``.
    show_windows : bool, default True
        Draw the individual per-window H/V curves in light grey.
    logx : bool, default True
        Logarithmic frequency axis (Geopsy style).
    figsize, xlim, ylim, save
        Plot controls (``save``: ``None`` | format | path).
    """
    import matplotlib.pyplot as plt

    fig, ax = plt.subplots(figsize=figsize or (8, 5))
    _draw_hvsr(ax, result, show_windows=show_windows, logx=logx)
    ax.set_xlabel("Frequency [Hz]")
    ax.set_ylabel("H/V")
    ax.set_title("HVSR (Nakamura) - %d windows" % result.get("n_windows", 0))
    if xlim is not None:
        ax.set_xlim(xlim)
    if ylim is not None:
        ax.set_ylim(ylim)
    ax.legend(fontsize=8)
    fig.tight_layout()
    return _finish(fig, save, "hvsr")


def plot_hvsr_all(results, dataset=None, *, show_windows=True, logx=True,
                  figsize=None, xlim=None, ylim=None, save=None):
    """Plot ``{device: result}`` (from ``ds.hvsr(...)`` / ``mt.hvsr()``).

    Accepts the new single-argument form (the result carries its dataset) or
    the old ``(dataset, results)``. One panel per sensor.

    Parameters
    ----------
    results : BroadcastResult or dict
        ``{device: hvsr_result}`` (carries ``.dataset`` when from a broadcast).
    dataset : SensorDataset, optional
        Source object (device order, colors, titles).
    show_windows, logx, figsize, xlim, ylim, save
        As in :func:`plot_hvsr`.
    """
    import matplotlib.pyplot as plt

    from ._panels import resolve
    results, dataset = resolve(results, dataset)
    devices = ([d for d in dataset.devices if d in results]
               if dataset is not None else list(results))
    if not devices:
        raise ValueError("plot_hvsr_all: no matching devices in results")
    colors = getattr(dataset, "device_colors", {}) or {}
    titles = getattr(dataset, "titles", {}) or {}

    n = len(devices)
    fig, axes = plt.subplots(1, n, figsize=figsize or (4.2 * n, 4.4),
                             squeeze=False)
    for j, d in enumerate(devices):
        ax = axes[0][j]
        _draw_hvsr(ax, results[d], show_windows=show_windows, logx=logx,
                   color=colors.get(d, "C%d" % (j % 10)))
        ax.set_title("%s - %s" % (d, titles.get(d, "")), fontsize=9,
                     fontweight="bold")
        ax.set_xlabel("Frequency [Hz]")
        if j == 0:
            ax.set_ylabel("H/V")
        if xlim is not None:
            ax.set_xlim(xlim)
        if ylim is not None:
            ax.set_ylim(ylim)
        ax.legend(fontsize=7)
    fig.tight_layout()
    return _finish(fig, save, "hvsr_all")
