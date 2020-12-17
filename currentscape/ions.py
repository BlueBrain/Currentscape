"""Ion concentrations class."""

# pylint: disable=wrong-import-position, super-with-arguments
import numpy as np
import matplotlib

matplotlib.use("agg")  # to avoid tkinter error
import matplotlib.pyplot as plt

from currentscape.datasets import DataSet
from currentscape.data_processing import reorder
from currentscape.plotting import (
    apply_labels_ticks_and_lims,
    select_color,
)
from currentscape.legends import (
    set_legend,
)


class IonConcentrations(DataSet):
    """Class containing ion concentrations data."""

    def __init__(self, data, names, reorder_):
        """Constructor.

        Args:
            data (list of lists): data
                all lists are expected to have the same size.
            names (list of str): ion names
            reorder_ (bool): set to True to reorder ions from largest to smallest
        """
        super(IonConcentrations, self).__init__(data=data, names=names)

        if self.data is not None and reorder_:
            _, self.idxs = reorder(self.data)

    def plot(
        self,
        c,
        row,
        rows_tot,
        cmap,
    ):
        """Plot positive (or negative) ionic concentration.

        Args:
            c (dict): config
            row (int): row of subplot
            rows_tot (int): total number of subplots in the figure
            cmap (matplotlib.colors.Colormap): colormap
        """
        ax = plt.subplot2grid((rows_tot, 1), (row, 0), rowspan=1)

        # plot ion concentrations with lines.
        x = np.arange(self.x_size)
        for i, ion in enumerate(self.data[self.idxs]):
            if not np.all(ion == 0):
                color = select_color(cmap, i, self.N)

                ax.plot(
                    x,
                    ion,
                    color=color,
                    ls="solid",
                    lw=c["current"]["lw"],
                    zorder=2,
                )

        # legend
        # place legend here so that legend top is at the level of share plot top
        if c["show"]["legend"]:
            set_legend(
                ax,
                cmap,
                c["ions"]["names"],
                c["legend"]["bgcolor"],
                c["legend"]["ypos"],
                self.idxs,
            )

        apply_labels_ticks_and_lims(
            ax, c, self.x_size, list(c["ions"]["ylim"]), True, "ions"
        )
