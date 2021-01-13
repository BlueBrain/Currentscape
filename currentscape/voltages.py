"""Voltages class."""

# pylint: disable=wrong-import-position, super-with-arguments
import numpy as np
import matplotlib

matplotlib.use("agg")  # to avoid tkinter error
import matplotlib.pyplot as plt

from currentscape.datasets import DataSet
from currentscape.plotting import remove_ticks_and_frame, show_xgridlines


class Voltages(DataSet):
    """Class containing voltage data."""

    def __init__(self, data, c, time):
        """Constructor.

        Args:
            data (list): data
            c (dict): config
            time (list): time of the data
        """
        # DataSet expect a list of lists as data
        super(Voltages, self).__init__(
            data=[data], names=None, time=time, xticks=c["xaxis"]["xticks"]
        )

    def plot(self, c, row, rows_tot):
        """Plot voltage trace.

        Args:
            c (dict): config
            row (int): row of subplot
            rows_tot (int): total number of subplots in the figure
        """
        ax = plt.subplot2grid((rows_tot, 1), (row, 0), rowspan=2)

        ax.plot(self.time, self.data[0], color=c["voltage"]["color"], lw=c["lw"])

        ax.plot(
            self.time,
            np.ones(self.x_size) * c["voltage"]["ticks"][0],
            ls="dashed",
            color="black",
            lw=0.75,
        )

        ax.vlines(
            1, c["voltage"]["ticks"][0], c["voltage"]["ticks"][-1], lw=1, color="black"
        )

        ax.set_ylim(c["voltage"]["ylim"])
        ax.set_xlim([self.time[0], self.time[-1]])

        # show x axis gridline
        if c["show"]["xgridlines"]:
            show_xgridlines(ax, c, self.xticks, c["voltage"]["ylim"])

        if c["show"]["ylabels"]:
            ax.set_ylabel(c["voltage"]["units"], labelpad=c["labelpad"])
        if c["show"]["yticklabels"]:
            ax.set_yticks(c["voltage"]["ticks"])

        remove_ticks_and_frame(ax)
