"""Overview plot of every sensor.

A schematic 3 x N grid (rows X/Y/Z, one column per device) showing the whole
record downsampled, with the selected time window marked by red dashed lines.
It reads the .h5 files one at a time with a stride, so it stays light even over
long records. The raw acceleration is in g, so the default factor is 1.0 (g).
"""

import numpy as np


def _to_dt64(value):
    """Turn a datetime / string into numpy datetime64."""
    return np.datetime64(value)


def _read_downsampled(dataset, device, pts_per_file):
    """Read one device across all files, strided, returning (times, x, y, z).

    Reads each file's Acceleration fully (a few MB) then keeps every stride-th
    sample, so peak memory is one file. Times are rebuilt from each file's
    start datetime and the sampling interval.
    """
    import h5py

    axes = tuple(dataset.axes_map.get(device, (0, 1, 2)))
    dt = dataset.dt

    t_parts, x_parts, y_parts, z_parts = [], [], [], []
    for file_dt, path in dataset._index.files:
        with h5py.File(path, "r") as f:
            key = "Devices/%s/Acceleration" % device
            if key not in f:
                continue
            arr = f[key][:, :]                      # one file in memory (~MB)
        n = arr.shape[0]
        if n == 0:
            continue
        cols = axes if max(axes) < arr.shape[1] else (0, 1, 2)
        stride = max(1, n // max(1, pts_per_file))
        sub = arr[::stride, :]
        k = np.arange(sub.shape[0])
        t0 = _to_dt64(file_dt)
        secs = (k * stride * dt)
        times = t0 + (secs * 1e9).astype("timedelta64[ns]")
        t_parts.append(times)
        x_parts.append(sub[:, cols[0]])
        y_parts.append(sub[:, cols[1]])
        z_parts.append(sub[:, cols[2]])

    if not t_parts:
        empty = np.array([])
        return np.array([], dtype="datetime64[ns]"), empty, empty, empty

    return (np.concatenate(t_parts), np.concatenate(x_parts),
            np.concatenate(y_parts), np.concatenate(z_parts))


def plot_overview(dataset, devices=None, titles=None, factor=1.0, unit="g",
                  number_max_points=2000, window=None, figsize=None, save=None):
    """Plot a downsampled overview of every sensor with the window marked.

    Parameters
    ----------
    dataset : SensorDataset
        Source dataset (provides the file index, dt and the axis map).
    devices : list of str or None
        Devices to show, in column order. ``None`` uses ``dataset.devices``.
    titles : dict or None
        Per-device column label, e.g. ``{"MOF00134": "Subterraneo"}``. Missing
        devices fall back to their id.
    factor : float, default 1.0
        Multiplier on the raw acceleration. The raw .h5 is in g, so 1.0 shows g
        and 9.81 shows m/s^2.
    unit : str, default "g"
        Unit label for the y axes.
    number_max_points : int, default 2000
        Approximate total points per series (schematic downsample).
    window : tuple or None
        ``(start, end)`` (datetime or string) drawn as red dashed lines.
    figsize : tuple or None
        Figure size; defaults to a width that grows with the number of devices.
    save : str or None
        Format ("pdf"/"svg"/"png") or a path to save; ``None`` shows the figure.

    Returns
    -------
    None or str
        The saved path when ``save`` is given, otherwise ``None``.
    """
    import matplotlib.pyplot as plt

    devices = list(devices) if devices is not None else list(dataset.devices)
    titles = titles or {}
    n_dev = len(devices)
    n_files = max(1, len(dataset._index.files))
    pts_per_file = max(1, number_max_points // n_files)

    rows = [("x", "Acc X [%s]" % unit, "C0"),
            ("y", "Acc Y [%s]" % unit, "C1"),
            ("z", "Acc Z [%s]" % unit, "C2")]

    if figsize is None:
        figsize = (3.4 * n_dev, 7)
    fig, axes = plt.subplots(3, n_dev, figsize=figsize, sharex="col", squeeze=False)

    w0 = _to_dt64(window[0]) if window else None
    w1 = _to_dt64(window[1]) if window else None

    for j, device in enumerate(devices):
        t, x, y, z = _read_downsampled(dataset, device, pts_per_file)
        data = {"x": x * factor, "y": y * factor, "z": z * factor}
        label = titles.get(device, device)
        for i, (comp, ylab, color) in enumerate(rows):
            ax = axes[i][j]
            if t.size:
                ax.plot(t, data[comp], color=color, lw=0.6)
            if w0 is not None:
                ax.axvline(w0, color="red", ls="--", lw=1.0)
                ax.axvline(w1, color="red", ls="--", lw=1.0)
            if i == 0:
                ax.set_title("%s - %s" % (device, label), fontsize=9, fontweight="bold")
            if j == 0:
                ax.set_ylabel(ylab)
            ax.grid(True, alpha=0.3)

    fig.autofmt_xdate(rotation=90)
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
