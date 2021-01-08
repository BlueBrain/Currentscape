"""Currents class."""

# pylint: disable=wrong-import-position, super-with-arguments
import numpy as np
import matplotlib

matplotlib.use("agg")  # to avoid tkinter error
import matplotlib.pyplot as plt

from currentscape.datasets import DataSet
from currentscape.data_processing import (
    reordered_idx,
    reorder,
    remove_zero_arrays,
)
from currentscape.plotting import (
    remove_ticks_and_frame_for_bar_plot,
    set_label,
    apply_labels_ticks_and_lims,
    select_color,
    stackplot_with_bars,
    black_line_log_scale,
)
from currentscape.legends import (
    set_legend_with_hatches,
    set_legend_with_hatches_and_linestyles,
    set_legend,
)
from currentscape.mapper import create_mapper


class CurrentPlottingMixin:
    """All current plotting methods to be inherited by the Currents class."""

    def plot_sum(self, c, row, rows_tot, positive=True):
        """Plot outward or inward current sum in log scale.

        Args:
            c (dict): config
            row (int): row of subplot
            rows_tot (int): total number of subplots in the figure
            positive (bool): True to plot positive currents subplot.
                False to plot negative currents subplot
        """
        if positive:
            curr = self.pos_sum
        else:
            curr = self.neg_sum

        ax = plt.subplot2grid((rows_tot, 1), (row, 0), rowspan=1)
        ax.fill_between(
            np.arange(self.x_size),
            curr,
            color=c["current"]["color"],
            lw=c["lw"],
            zorder=2,
        )
        apply_labels_ticks_and_lims(
            ax, c, self.x_size, list(c["current"]["ylim"]), positive, "current"
        )

    def plot_shares_with_bars(self, c, row, rows_tot, cmap):
        """Plot current percentages with barplots.

        Args:
            c (dict): config
            row (int): row of subplot
            rows_tot (int): total number of subplots in the figure
            cmap (matplotlib.colors.Colormap): colormap
        """
        # outward currents
        ax = plt.subplot2grid((rows_tot, 1), (row, 0), rowspan=2)
        size = stackplot_with_bars(
            ax, self.pos_norm, self.idxs, cmap, c, self.N, self.mapper
        )

        # add at black line a the bottom of the plot.
        # cannot use spines because with subplot_adjust(h=0),
        # spines overlap on neighboor plot and hide part of the data
        y_bottom = -c["current"]["black_line_thickness"] / 100.0
        ax.fill_between([0, size], [y_bottom, y_bottom], color="black", lw=0)

        ax.set_ylim(y_bottom, 1)
        ax.set_xlim(0, size)
        remove_ticks_and_frame_for_bar_plot(ax)

        # labels
        if c["show"]["labels"]:
            ax.set_ylabel(c["currentscape"]["out_label"], labelpad=c["labelpad"])

        # legend
        # place legend here so that legend top is at the level of share plot top
        if c["show"]["legend"]:
            if c["show"]["all_currents"] and not c["current"]["stackplot"]:
                set_legend_with_hatches_and_linestyles(
                    ax, cmap, self.mapper, c, self.idxs
                )
            else:
                set_legend_with_hatches(ax, cmap, self.mapper, c, self.idxs)

        # inward currents
        ax = plt.subplot2grid((rows_tot, 1), (row + 2, 0), rowspan=2)
        size = stackplot_with_bars(
            ax, self.neg_norm, self.idxs, cmap, c, self.N, self.mapper
        )

        ax.set_ylim(0, 1)
        ax.set_xlim(0, size)
        remove_ticks_and_frame_for_bar_plot(ax)

        # labels
        if c["show"]["labels"]:
            ax.set_ylabel(c["currentscape"]["in_label"], labelpad=c["labelpad"])

    def plot_shares_with_imshow(self, c, row, rows_tot, cmap):
        """Plot current percentage using imshow.

        Args:
            c (dict): config
            row (int): row of subplot
            rows_tot (int): total number of subplots in the figure
            cmap (matplotlib.colors.Colormap): colormap
        """
        resy = c["currentscape"]["y_resolution"]
        black_line_size = int(resy * c["current"]["black_line_thickness"] / 100.0)

        ax = plt.subplot2grid((rows_tot, 1), (row, 0), rowspan=3)
        im = ax.imshow(
            self.image[::1, ::1],
            interpolation="nearest",
            aspect="auto",
            cmap=cmap,
        )

        plt.gca().xaxis.set_major_locator(plt.NullLocator())
        plt.gca().yaxis.set_major_locator(plt.NullLocator())

        # set limits
        ax.set_ylim(2 * resy + black_line_size, 0)
        ax.set_xlim(0, self.x_size)
        # set number of colors
        # data + black for separating line + white for empty data = (N-1)+1+1
        im.set_clim(0, self.N + 1)

        # remove top and bottom frame that hide some data
        ax.spines["top"].set_visible(False)
        ax.spines["bottom"].set_visible(False)

        # labels
        if c["show"]["labels"]:
            # cheat to set two labels at the right places for 1 axis
            set_label(
                ax,
                x=0,
                y=3 * resy / 2,
                label=c["currentscape"]["in_label"],
                textsize=c["textsize"],
            )
            set_label(
                ax,
                x=0,
                y=resy / 2,
                label=c["currentscape"]["out_label"],
                textsize=c["textsize"],
            )

        # legend
        if c["show"]["legend"]:
            set_legend(
                ax,
                im.cmap,
                c["current"]["names"],
                c["legend"]["bgcolor"],
                c["legend"]["ypos"],
                self.idxs,
            )

    def plot_with_lines(self, ax, selected_currs, c, cmap):
        """Plot all the positive (or negative) currents with lines.

        Args:
            ax (matplotlib.axes): currentscape axis
            selected_currs (ndarray of ndarrays): positive or negative currents data
            c (dict): config
            cmap (matplotlib.colors.Colormap): colormap
        """
        n_colors = c["colormap"]["n_colors"]
        ls = c["line"]["styles"]
        lw = c["lw"]

        x = np.arange(self.x_size)

        # here, use currs.idxs to have the same colors as in currs.names
        # can do it because selected_currs have same shape as self (no zero arrays removed)
        for i, curr in enumerate(selected_currs[self.idxs]):
            if not np.all(curr == 0):
                if c["pattern"]["use"]:
                    color = cmap((self.mapper * i) % n_colors)
                    linestyle = ls[((self.mapper * i) // n_colors) % len(ls)]
                else:
                    color = select_color(cmap, i, self.N)
                    linestyle = "solid"

                ax.plot(x, curr, color=color, ls=linestyle, lw=lw, zorder=2)

    def plot(self, c, row, rows_tot, cmap, positive=True):
        """Plot all the positive (or negative) currents.

        Args:
            c (dict): config
            row (int): row of subplot
            rows_tot (int): total number of subplots in the figure
            cmap (matplotlib.colors.Colormap): colormap
            positive (bool): True to plot positive currents subplot.
                False to plot negative currents subplot
        """
        ylim = list(c["current"]["ylim"])
        xmax = self.x_size

        ax = plt.subplot2grid((rows_tot, 1), (row, 0), rowspan=1)

        # select currents (positive or negative)
        if positive:
            selected_currs = self.get_positive_data()
        else:
            selected_currs = np.abs(self.get_negative_data())

        # plot selected currents, either with stackplot or with lines.
        if c["current"]["stackplot"]:
            # create dataset from reordered selected currents
            sorted_idxs = reordered_idx(selected_currs)
            sel_currs = DataSet(data=selected_currs[sorted_idxs], names=self.names)
            sel_currs.idxs = sorted_idxs

            xmax = stackplot_with_bars(
                ax, sel_currs, self.idxs, cmap, c, self.N, self.mapper, False
            )
        else:
            self.plot_with_lines(ax, selected_currs, c, cmap)

        # add black line separating positive currents from negative currents
        if positive and c["current"]["stackplot"]:
            ylim = black_line_log_scale(
                ax, ylim, xmax, c["current"]["black_line_thickness"]
            )

        apply_labels_ticks_and_lims(ax, c, xmax, ylim, positive, "current")


class Currents(CurrentPlottingMixin, DataSet):
    """Class containing current data."""

    def __init__(self, data, c):
        """Constructor.

        Args:
            data (list of lists): data
                all lists are expected to have the same size.
            c (dict): config

        Attributes:
            pos_norm (ndarray of ndarrays): norm of positive data
            neg_norm (ndarray of ndarrays): - norm of negative data
            pos_sum (ndarray of floats): summed positive data along axis=0
            neg_sum (ndarray of floats): summed negative data along axis=0
            image (ndarray of ndarrays): currentscape image to be shown with imshow
            mapper (int): number used to mix colors and patterns
        """
        reorder_ = c["current"]["reorder"]
        resy = c["currentscape"]["y_resolution"]
        lw = c["current"]["black_line_thickness"]
        use_pattern = c["pattern"]["use"]
        n_patterns = len(c["pattern"]["patterns"])

        super(Currents, self).__init__(data=data, names=c["current"]["names"])

        # self.idxs may be modified in the method below
        self.pos_norm, self.neg_norm, self.pos_sum, self.neg_sum = self.data_processing(
            reorder_
        )

        if use_pattern:
            # check this before creating mapper
            # this change should persist even outside the class
            if c["colormap"]["n_colors"] > self.N:
                c["colormap"]["n_colors"] = self.N

            self.image = None
            self.mapper = create_mapper(c["colormap"]["n_colors"], n_patterns)
        else:
            self.image = self.create_cscape_image(resy, lw)
            self.mapper = None

    def data_processing(self, reorder_):
        """Separate into positive and negative currents.

        Remove 0s arrays. Reorder if asked. Record reordered name indexes.
        Return the sum and the fraction with its reordered indexes.

        Returns:
            pos_norm (ndarray of ndarrays): arrays containing norm
                of positive currents
            neg_norm (ndarray of ndarrays): arrays containing (-1)* norm
                of negative currents
            normapos (ndarray): summed positive currents
            normaneg (ndarray): summed (absolute values of) negative currents
        """
        cpos = self.get_positive_data()
        cneg = self.get_negative_data()

        normapos = np.sum(np.abs(np.array(cpos)), axis=0)
        normaneg = np.sum(np.abs(np.array(cneg)), axis=0)

        # replace 0s by 1s in norma* to avoid 0/0 error.
        # When norma* is 0, all values it divides are 0s, so even when replaced by 1s,
        #   the result is 0.
        # We want the result to be 0 in that case because there is no current.
        cnorm_pos = np.abs(cpos) / [x if x != 0 else 1.0 for x in normapos]
        cnorm_neg = -(np.abs(cneg) / [x if x != 0 else 1.0 for x in normaneg])

        if reorder_:
            cnorm_pos, cnorm_neg, idx_pos, idx_neg = self.reorder_currents_and_names(
                cnorm_pos, cnorm_neg
            )
        else:
            cnorm_pos, idx_pos = remove_zero_arrays(cnorm_pos)
            cnorm_neg, idx_neg = remove_zero_arrays(cnorm_neg)

        pos_norm = DataSet(cnorm_pos)
        pos_norm.idxs = idx_pos
        neg_norm = DataSet(cnorm_neg)
        neg_norm.idxs = idx_neg

        return (
            pos_norm,
            neg_norm,
            normapos,
            normaneg,
        )

    def reorder_currents_and_names(self, cnorm_pos, cnorm_neg):
        """Reorder positive currents, negative currents, and current names.

        Reorder from overall largest contribution to smallest contribution.
        Reordering the current names (for legend display) is not essential,
        but is more pleasant to the eye.

        Returns:
            trimmed and reordered positive currents array
            trimmed and reordered negative currents array
            indexes that currents (in the pos array) used to have in the original curr array
            indexes that currents (in the neg array) used to have in the original curr array
        """
        cnorm_pos, idx_pos = reorder(cnorm_pos)
        cnorm_neg, idx_neg = reorder(cnorm_neg)

        # for the order of names, just stack the positive and negative order,
        # while removing duplicates.
        # also stack arange in case a current is zero for all the sim -> avoid index errors later
        idx_names = []
        _ = [
            idx_names.append(x)
            for x in np.concatenate((idx_pos, idx_neg, np.arange(self.N)))
            if x not in idx_names
        ]
        self.idxs = idx_names  # pylint: disable=attribute-defined-outside-init

        return cnorm_pos, cnorm_neg, idx_pos, idx_neg

    def create_black_line(self, resy, lw):
        """Create a black line to separate inward and outward current shares.

        Args:
            resy (int): y-axis resolution
                (must be high >>1000 or else rounding errors produce white pixels)
            lw (int): black line (separating the two currentscape plots) thickness
                in percentage of the plot height.
        """
        line_thickness = int(resy * lw / 100.0)
        if line_thickness < 1:
            line = np.full((1, self.x_size), self.N)
        else:
            line = np.full((line_thickness, self.x_size), self.N)

        return line

    def create_cscape_image(self, resy, lw):
        """Create currentscape image.

        Args:
            resy (int): y-axis resolution
                (must be high >>1000 or else rounding errors produce white pixels)
            lw (int): black line (separating the two currentscape plots) thickness
                in percentage of the plot height.
        """
        # idexes to map to re-ordered current names
        # interchange index and values of inames to create imap
        # that way, imap[idx] gives index in inames
        imap = np.zeros(self.N, dtype=int)
        imap[self.idxs] = np.arange(self.N)

        times = np.arange(0, self.x_size)
        impos = np.full((resy, self.x_size), self.N + 1)
        imneg = np.full((resy, self.x_size), self.N + 1)

        for t in times:
            lastpercent = 0
            for idx, curr in zip(self.pos_norm.idxs, self.pos_norm.data):
                if curr[t] > 0:
                    numcurr = imap[idx]
                    percent = int(abs(curr[t]) * (resy))
                    impos[lastpercent : lastpercent + percent, t] = numcurr
                    lastpercent = lastpercent + percent
        for t in times:
            lastpercent = 0
            for idx, curr in zip(self.neg_norm.idxs, self.neg_norm.data):
                if curr[t] < 0:
                    numcurr = imap[idx]
                    percent = int(abs(curr[t]) * (resy))
                    imneg[lastpercent : lastpercent + percent, t] = numcurr
                    lastpercent = lastpercent + percent

        # append fake data to produce a black line separating inward & outward
        # cannot draw with plot, because that would hide data because of adjust (h=0)
        line = self.create_black_line(resy, lw)

        return np.vstack((impos, line, imneg))
