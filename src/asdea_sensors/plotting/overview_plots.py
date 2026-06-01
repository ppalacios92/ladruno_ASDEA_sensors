"""Overview plot of every sensor.

A schematic 3 x N grid (rows X/Y/Z, one column per device) showing the whole
record, with the selected time window marked by red dashed lines.

The downsampling is automatic and peak-preserving, so the user never sets a
sample count:

* the number of points is taken from the figure width in pixels (you cannot
  draw more points than pixels);
* each series is reduced by min-max decimation -- per bin the minimum and the
  maximum are kept -- so transient peaks (e.g. an earthquake) never disappear,
  unlike plain striding;
* the plotted arrays are cast to float16 (enough for a picture, light on memory).

Files are read one at a time, so it stays light even over long records. The raw
.h5 acceleration is in g, so the default factor is 1.0 (g).
"""

import numpy as np


def _to_dt64(value):
    """Turn a datetime / string into numpy datetime64."""
    return np.datetime64(value)


def _minmax(values, times, n_bins):
    """Min-max decimate a series into ~2*n_bins points, preserving peaks."""
    n = values.shape[0]
    if n_bins < 1 or n <= 2 * n_bins:
        return times, values.astype(np.float16)
    edges = np.linspace(0, n, n_bins + 1).astype(int)
    xs = np.empty(2 * n_bins, dtype=times.dtype)
    ys = np.empty(2 * n_bins, dtype=np.float16)
    for b in range(n_bins):
        a, c = edges[b], edges[b + 1]
        if c <= a:
            c = a + 1
        seg = values[a:c]
        tmid = times[min((a + c) // 2, n - 1)]
        xs[2 * b] = tmid
        xs[2 * b + 1] = tmid
        ys[2 * b] = seg.min()
        ys[2 * b + 1] = seg.max()
    return xs, ys


def _read_device(dataset, device, target, window=None):
    """Read one device and return (t, x, y, z) decimated.

    Without a window: streams every file, min-max decimating each to a share of
    ``target`` (peak memory is one file). With a window: reads only the files
    overlapping it, trims to the exact bounds, then decimates the result.
    """
    import h5py

    axes = tuple(dataset.axes_map.get(device, (0, 1, 2)))
    dt = dataset.dt
    key = "Devices/%s/Acceleration" % device

    # Windowed: read only the overlapping files (few), concatenate, trim, decimate.
    if window is not None:
        w0, w1 = _to_dt64(window[0]), _to_dt64(window[1])
        paths = set(dataset._index.in_range(window[0], window[1]))
        acc_parts, t_parts = [], []
        for file_dt, path in dataset._index.files:
            if path not in paths:
                continue
            with h5py.File(path, "r") as f:
                if key not in f:
                    continue
                arr = f[key][:, :]
            n = arr.shape[0]
            if n == 0:
                continue
            cols = axes if max(axes) < arr.shape[1] else (0, 1, 2)
            times = _to_dt64(file_dt) + (np.arange(n) * dt * 1e9).astype("timedelta64[ns]")
            acc_parts.append(arr[:, cols])
            t_parts.append(times)
        if not acc_parts:
            empty = np.array([], dtype=np.float16)
            return np.array([], dtype="datetime64[ns]"), empty, empty, empty
        acc = np.concatenate(acc_parts)
        t = np.concatenate(t_parts)
        m = (t >= w0) & (t <= w1)
        acc, t = acc[m], t[m]
        tx, x = _minmax(acc[:, 0], t, target)
        _, y = _minmax(acc[:, 1], t, target)
        _, z = _minmax(acc[:, 2], t, target)
        return tx, x, y, z

    # Whole record: stream file by file.
    total = max(1, dataset.n_samples.get(device, 0))
    t_parts, x_parts, y_parts, z_parts = [], [], [], []
    for file_dt, path in dataset._index.files:
        with h5py.File(path, "r") as f:
            if key not in f:
                continue
            arr = f[key][:, :]                       # one file in memory
        n = arr.shape[0]
        if n == 0:
            continue
        cols = axes if max(axes) < arr.shape[1] else (0, 1, 2)
        t0 = _to_dt64(file_dt)
        times = t0 + (np.arange(n) * dt * 1e9).astype("timedelta64[ns]")
        bins = max(1, int(round(target * n / total)))
        tx, x = _minmax(arr[:, cols[0]], times, bins)
        _, y = _minmax(arr[:, cols[1]], times, bins)
        _, z = _minmax(arr[:, cols[2]], times, bins)
        t_parts.append(tx)
        x_parts.append(x)
        y_parts.append(y)
        z_parts.append(z)

    if not t_parts:
        empty = np.array([], dtype=np.float16)
        return np.array([], dtype="datetime64[ns]"), empty, empty, empty

    return (np.concatenate(t_parts), np.concatenate(x_parts),
            np.concatenate(y_parts), np.concatenate(z_parts))


def plot_overview(dataset, devices=None, titles=None, factor=1.0, unit="g",
                  number_max_points=None, window=None, xlim=None, figsize=None,
                  save=None):
    """Plot a downsampled overview of every sensor with the window marked.

    Parameters
    ----------
    dataset : SensorDataset
        Source dataset (provides the file index, dt and the axis map).
    devices : list of str or None
        Devices to show, in column order. ``None`` uses ``dataset.devices``.
    titles : dict or None
        Per-device column label, e.g. ``{"MOF00134": "Subterraneo"}``.
    factor : float, default 1.0
        Multiplier on the raw acceleration. The raw .h5 is in g, so 1.0 shows g
        and 9.81 shows m/s^2.
    unit : str, default "g"
        Unit label for the y axes.
    number_max_points : int or None, default None
        Optional override for the points drawn per series. ``None`` resolves it
        automatically from the figure width (recommended); pass a number only
        to force finer or coarser detail.
    window : tuple or None
        ``(start, end)`` (datetime or string) drawn as red dashed lines.
    xlim : tuple or None
        ``(start, end)`` (datetime or string) to zoom the x axis to a date
        range. Independent of ``window``: you can zoom to a region and still
        mark the analysis window inside it. ``None`` shows the whole record.
    figsize : tuple or None
        Figure size; the downsampling resolution is taken from its width.
    save : str or None
        Format ("pdf"/"svg"/"png") or a path to save; ``None`` shows the figure.

    Returns
    -------
    None or str
        The saved path when ``save`` is given, otherwise ``None``.
    """
    import matplotlib.pyplot as plt
    import matplotlib.dates as mdates

    devices = list(devices) if devices is not None else list(dataset.devices)
    titles = titles if titles is not None else getattr(dataset, "titles", {})
    titles = titles or {}
    n_dev = len(devices)

    if figsize is None:
        figsize = (3.4 * n_dev, 7)

    fig, axes = plt.subplots(3, n_dev, figsize=figsize, sharex="col", squeeze=False)
    dpi = fig.get_dpi()

    # Points per series. By default it is the figure width in pixels (you
    # cannot draw more points than pixels); min-max keeps the peaks. Passing
    # number_max_points overrides it for finer or coarser detail.
    if number_max_points is not None:
        target = max(2, int(number_max_points))
    else:
        target = max(200, int(figsize[0] * dpi / max(1, n_dev)))

    rows = [("x", "Acc X [%s]" % unit),
            ("y", "Acc Y [%s]" % unit),
            ("z", "Acc Z [%s]" % unit)]

    # One color per device (column), taken from the dataset; same color for the
    # three rows of that sensor.
    colors = getattr(dataset, "device_colors", {}) or {}

    # If the dataset is windowed (ds.window/get_window), read only that window
    # and zoom to it; on a full dataset the read stays full and `window` just
    # marks a candidate range with red lines (the "pick a window" use case).
    read_window = getattr(dataset, "_default_window", None)
    if window is None:
        window = read_window
    if xlim is None and read_window is not None:
        xlim = read_window

    w0 = _to_dt64(window[0]) if window else None
    w1 = _to_dt64(window[1]) if window else None
    fmt = mdates.DateFormatter("%Y-%m-%d %H:%M:%S")

    for j, device in enumerate(devices):
        t, x, y, z = _read_device(dataset, device, target, window=read_window)
        series = {"x": x, "y": y, "z": z}
        label = titles.get(device, device)
        color = colors.get(device, "C%d" % (j % 10))
        for i, (comp, ylab) in enumerate(rows):
            ax = axes[i][j]
            vals = np.asarray(series[comp], dtype=float) * factor
            if t.size:
                ax.plot(t, vals, color=color, lw=0.6)
            if w0 is not None:
                ax.axvline(w0, color="red", ls="--", lw=1.0)
                ax.axvline(w1, color="red", ls="--", lw=1.0)
                # Scale the y axis to the data inside the window, not the whole
                # record, so the windowed motion is not dwarfed by peaks
                # elsewhere.
                in_win = (t >= w0) & (t <= w1)
                if in_win.any():
                    lo, hi = float(vals[in_win].min()), float(vals[in_win].max())
                    pad = 0.05 * (hi - lo) if hi > lo else (abs(hi) * 0.05 or 1e-9)
                    ax.set_ylim(lo - pad, hi + pad)
            if i == 0:
                ax.set_title("%s - %s" % (device, label), fontsize=9, fontweight="bold")
            if j == 0:
                ax.set_ylabel(ylab)
            ax.grid(True, alpha=0.3)
            if xlim is not None:
                ax.set_xlim(_to_dt64(xlim[0]), _to_dt64(xlim[1]))
            if i == 2:
                ax.xaxis.set_major_formatter(fmt)

    for ax in axes[2]:
        for lbl in ax.get_xticklabels():
            lbl.set_rotation(90)
    fig.tight_layout()

    if save is None:
        plt.show()
        return None
    if save.lower() in ("png", "svg", "pdf", "jpg", "jpeg"):
        fname = "overview." + save.lower()
    else:
        fname = save
    fig.savefig(fname, bbox_inches="tight")
    plt.close(fig)
    return fname
