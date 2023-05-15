"""Ion concentrations class."""

# Copyright 2023 Blue Brain Project / EPFL

# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at

#     http://www.apache.org/licenses/LICENSE-2.0

# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

# pylint: disable=wrong-import-position, super-with-arguments
import numpy as np
import matplotlib

matplotlib.use("agg")  # to avoid tkinter error
import matplotlib.pyplot as plt

from currentscape.datasets import DataSet
from currentscape.data_processing import reorder
from currentscape.plotting import (
    get_colors_hatches_lines_lists,
    apply_labels_ticks_and_lims,
    select_color,
)
from currentscape.legends import (
    set_legend,
    set_legend_with_lines,
)
from currentscape.mapper import create_mapper


class IonConcentrations(DataSet):
    """Class containing ion concentrations data."""

    def __init__(self, data, c, time=None):
        """Constructor.

        Args:
            data (list of lists): data
                all lists are expected to have the same size.
            c (dict): config
            time (list): time of the data

        Attributes:
            mapper (int): number used to mix colors and patterns / linestyles
        """
        reorder_ = c["ions"]["reorder"]
        use_patterns = c["pattern"]["use"]
        n_patterns = len(c["pattern"]["patterns"])

        super(IonConcentrations, self).__init__(
            data=data, names=c["ions"]["names"], time=time, xticks=c["xaxis"]["xticks"]
        )

        self.mapper = None

        if self.data is not None:
            if reorder_:
                _, self.idxs = reorder(self.data)

            if use_patterns:
                n_colors = min([c["colormap"]["n_colors"], self.N])
                self.mapper = create_mapper(n_colors, n_patterns)

    def plot_with_linestyles(self, c, row, rows_tot, cmap):
        """Plot all the ion concentration with linestyles.

        Args:
            c (dict): config
            row (int): row of subplot
            rows_tot (int): total number of subplots in the figure
            cmap (matplotlib.colors.Colormap): colormap
        """
        lw = c["lw"]

        ylim = list(c["ions"]["ylim"])

        ax = plt.subplot2grid((rows_tot, 1), (row, 0), rowspan=1)

        x = np.arange(self.x_size)

        # here, use currs.idxs to have the same colors as in currs.names
        # can do it because selected_currs have same shape as self (no zero arrays removed)
        for i, ion in enumerate(self.data[self.idxs]):
            if not np.all(ion == 0):
                color, _, linestyle = get_colors_hatches_lines_lists(
                    c, i, cmap, self.mapper
                )
                ax.plot(x, ion, color=color, ls=linestyle, lw=lw, zorder=2)

        # legend
        # place legend here so that legend top is at the level of share plot top
        if c["show"]["legend"]:
            set_legend_with_lines(
                ax, cmap, self.mapper, c, self.idxs, c["ions"]["names"]
            )

        apply_labels_ticks_and_lims(
            ax,
            c,
            self.xticks,
            [self.time[0], self.time[-1]],
            ylim,
            True,
            "ions",
        )

    def plot(self, c, row, rows_tot, cmap):
        """Plot positive (or negative) ionic concentration.

        Args:
            c (dict): config
            row (int): row of subplot
            rows_tot (int): total number of subplots in the figure
            cmap (matplotlib.colors.Colormap): colormap
        """
        ax = plt.subplot2grid((rows_tot, 1), (row, 0), rowspan=1)

        # plot ion concentrations with lines.
        for i, ion in enumerate(self.data[self.idxs]):
            if not np.all(ion == 0):
                color = select_color(cmap, i, self.N)

                ax.plot(
                    self.time,
                    ion,
                    color=color,
                    ls="solid",
                    lw=c["lw"],
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
            ax,
            c,
            self.xticks,
            [self.time[0], self.time[-1]],
            list(c["ions"]["ylim"]),
            True,
            "ions",
        )
