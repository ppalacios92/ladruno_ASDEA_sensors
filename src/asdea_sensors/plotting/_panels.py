"""Shared layout for the analysis ``*_all`` plots.

The compute lives on the object (``ds.fourier()``, ``ds.psd()``, ...); these
helpers only draw the result. One function, :func:`draw_analysis`, picks the
layout from the shape of the result so every analysis behaves the same:

* ``{device: {comp: result}}``  (whole dataset, x/y/z)  -> grid, rows =
  components, columns = sensors (overview style);
* ``{comp: result}``            (one sensor, x/y/z)      -> a single axes with
  the components overlaid;
* ``{device: result}``          (one series per sensor)  -> sensors overlaid on
  one axes (force ``layout="grid"`` for one panel per sensor);
* ``result``                    (a single result)        -> one curve.

The caller passes a ``curve(result) -> (x, y)`` function plus labels, so each
analysis stays a thin wrapper.
"""


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


def comp_list(components):
    """Normalize the ``components`` argument into a list."""
    if components == "all":
        return ["x", "y", "z"]
    if isinstance(components, str):
        return [components]
    return list(components)


def resolve(arg1, arg2):
    """Accept both ``plot(results)`` and the old ``plot(dataset, results)``.

    Returns ``(results, dataset)``. ``results`` carries its own ``.dataset``
    (a :class:`BroadcastResult`), so the new form needs only the result; the old
    form (dataset first, results second) is still supported.
    """
    if arg2 is not None:                       # old: (dataset, results)
        return arg2, arg1
    return arg1, getattr(arg1, "dataset", None)


def _shape(results):
    """Classify the result container: raw / comp / device_flat / device_comp.

    Dataset-free: a *raw* result has only array/scalar values; a *comp* result
    is keyed by x/y/z; otherwise the keys are devices (flat or nested).
    """
    comp_set = {"x", "y", "z"}
    if not isinstance(results, dict) or not results:
        return "raw"
    values = list(results.values())
    if all(not isinstance(v, dict) for v in values):
        return "raw"
    if set(results) <= comp_set:
        return "comp"
    sub = values[0]
    if isinstance(sub, dict) and set(sub) <= comp_set:
        return "device_comp"
    return "device_flat"


def _layout_from_group(layout, group):
    """Back-compat: a bool ``group`` maps to a layout when given."""
    if group is None:
        return layout
    return "overlay" if group else "grid"


def draw_analysis(results, curve, *, dataset=None, components="all",
                  layout="auto", group=None, yscale="linear", xlabel="",
                  ylabel_unit="", title_word="", name="plot", mark=None,
                  figsize=None, xlim=None, ylim=None, save=None):
    """Draw a precomputed analysis result, picking the layout from its shape.

    Parameters
    ----------
    results : dict
        See the module docstring for the accepted shapes. A ``BroadcastResult``
        carries its own ``.dataset`` (device order, colors, titles); pass
        ``dataset`` only to override it.
    curve : callable
        ``curve(one_result) -> (x, y)`` arrays to plot.
    dataset : SensorDataset or None
        Source object override; defaults to ``results.dataset``.
    curve : callable
        ``curve(one_result) -> (x, y)`` arrays to plot.
    components : str or sequence, default "all"
        Components to include when the result is component-keyed.
    layout : {"auto", "grid", "overlay"}, default "auto"
        ``auto`` -> grid for multi-sensor multi-component, overlay otherwise.
    group : bool or None
        Back-compat alias: ``True`` -> overlay, ``False`` -> grid.
    yscale : {"linear", "log"}, default "linear"
    xlabel, ylabel_unit, title_word : str
        Axis labels (y reads ``"<title_word> [<ylabel_unit>]"`` or per-row
        ``"<COMP>\\n[<ylabel_unit>]"``).
    name : str
        Base filename used when ``save`` is a bare format.
    mark : callable or None
        Optional ``mark(ax, one_result, color)`` to add extras (e.g. peaks).
    figsize, xlim, ylim, save
        Plot controls.
    """
    import matplotlib.pyplot as plt

    if dataset is None:
        dataset = getattr(results, "dataset", None)
    layout = _layout_from_group(layout, group)
    shape = _shape(results)
    colors = getattr(dataset, "device_colors", {}) or {}
    titles = getattr(dataset, "titles", {}) or {}
    comps = comp_list(components)

    def draw(ax, x, y, **kw):
        (ax.semilogy if yscale == "log" else ax.plot)(x, y, **kw)

    def style(ax):
        ax.grid(True, alpha=0.3)
        if xlim is not None:
            ax.set_xlim(xlim)
        if ylim is not None:
            ax.set_ylim(ylim)

    # -- single result -------------------------------------------------
    if shape == "raw":
        fig, ax = plt.subplots(figsize=figsize or (9, 5))
        x, y = curve(results)
        draw(ax, x, y, lw=1.3, color="C0")
        if mark:
            mark(ax, results, "C0")
        ax.set_xlabel(xlabel)
        ax.set_ylabel("%s [%s]" % (title_word, ylabel_unit))
        style(ax)
        fig.tight_layout()
        return _finish(fig, save, name)

    # -- one sensor, components overlaid on one axes -------------------
    if shape == "comp":
        avail = [c for c in comps if c in results]
        fig, ax = plt.subplots(figsize=figsize or (10, 5))
        for i, c in enumerate(avail):
            x, y = curve(results[c])
            draw(ax, x, y, lw=1.1, color="C%d" % i, label=c.upper())
        ax.set_xlabel(xlabel)
        ax.set_ylabel("%s [%s]" % (title_word, ylabel_unit))
        ax.legend(fontsize=8)
        style(ax)
        fig.tight_layout()
        return _finish(fig, save, name)

    devices = ([d for d in dataset.devices if d in results]
               if dataset is not None else list(results))

    # -- multi-sensor, one series each ---------------------------------
    if shape == "device_flat":
        if layout == "grid":
            n = len(devices)
            fig, axes = plt.subplots(1, n, figsize=figsize or (3.6 * n, 4.2),
                                     squeeze=False)
            for j, d in enumerate(devices):
                ax = axes[0][j]
                x, y = curve(results[d])
                draw(ax, x, y, lw=1.1, color=colors.get(d, "C%d" % (j % 10)))
                ax.set_title("%s - %s" % (d, titles.get(d, "")),
                             fontsize=9, fontweight="bold")
                ax.set_xlabel(xlabel)
                if j == 0:
                    ax.set_ylabel("%s [%s]" % (title_word, ylabel_unit))
                style(ax)
            fig.tight_layout()
            return _finish(fig, save, name)
        fig, ax = plt.subplots(figsize=figsize or (10, 5))
        for j, d in enumerate(devices):
            x, y = curve(results[d])
            draw(ax, x, y, lw=1.0, color=colors.get(d, "C%d" % (j % 10)), label=d)
        ax.set_xlabel(xlabel)
        ax.set_ylabel("%s [%s]" % (title_word, ylabel_unit))
        ax.legend(fontsize=8)
        style(ax)
        fig.tight_layout()
        return _finish(fig, save, name)

    # -- multi-sensor, multi-component (device_comp) -------------------
    rows = comps
    if layout == "overlay":
        fig, axes = plt.subplots(len(rows), 1, sharex=True,
                                 figsize=figsize or (11, 2.6 * len(rows)),
                                 squeeze=False)
        for i, c in enumerate(rows):
            ax = axes[i][0]
            for j, d in enumerate(devices):
                if c not in results[d]:
                    continue
                x, y = curve(results[d][c])
                draw(ax, x, y, lw=0.9, color=colors.get(d, "C%d" % (j % 10)),
                     label=d)
            ax.set_ylabel("%s\n[%s]" % (c.upper(), ylabel_unit))
            style(ax)
        axes[0][0].legend(loc="upper right", ncol=len(devices), fontsize=8)
        axes[-1][0].set_xlabel(xlabel)
        fig.tight_layout()
        return _finish(fig, save, name)

    # grid: rows = components, columns = sensors (overview style).
    nrow, ncol = len(rows), len(devices)
    fig, axes = plt.subplots(nrow, ncol, sharex=True,
                             figsize=figsize or (3.4 * ncol, 2.4 * nrow),
                             squeeze=False)
    for j, d in enumerate(devices):
        color = colors.get(d, "C%d" % (j % 10))
        for i, c in enumerate(rows):
            ax = axes[i][j]
            if c in results[d]:
                x, y = curve(results[d][c])
                draw(ax, x, y, lw=0.9, color=color)
                if mark:
                    mark(ax, results[d][c], color)
            if i == 0:
                ax.set_title("%s - %s" % (d, titles.get(d, "")),
                             fontsize=9, fontweight="bold")
            if j == 0:
                ax.set_ylabel("%s\n[%s]" % (c.upper(), ylabel_unit))
            style(ax)
        axes[-1][j].set_xlabel(xlabel)
    fig.tight_layout()
    return _finish(fig, save, name)
