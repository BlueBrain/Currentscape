"""Currentscape subplots."""

# pylint: disable=too-many-statements, wrong-import-position
import numpy as np
import matplotlib

matplotlib.use("agg")  # to avoid tkinter error
import matplotlib.pyplot as plt

from currentscape.plotting import remove_ticks_and_frame


def plot_voltage_trace(c, voltage, row, rows_tot):
    """Plot voltage trace.

    Args:
        c (dict): config
        voltage (ndarray): voltage data
        row (int): row of subplot
        rows_tot (int): total number of subplots in the figure
    """
    ax = plt.subplot2grid((rows_tot, 1), (row, 0), rowspan=2)

    xmax = len(voltage)
    t = np.arange(xmax)

    ax.plot(t, voltage, color=c["voltage"]["color"], lw=1.0)

    ax.plot(
        t,
        np.ones(xmax) * c["voltage"]["ticks"][0],
        ls="dashed",
        color="black",
        lw=0.75,
    )

    ax.vlines(
        1, c["voltage"]["ticks"][0], c["voltage"]["ticks"][-1], lw=1, color="black"
    )

    ax.set_ylim(c["voltage"]["ylim"])
    ax.set_xlim(0, xmax)
    if c["show"]["labels"]:
        ax.set_ylabel(c["voltage"]["units"], labelpad=c["labelpad"])
    if c["show"]["ticklabels"]:
        ax.set_yticks(c["voltage"]["ticks"])
    remove_ticks_and_frame(ax)
