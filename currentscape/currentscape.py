"""Module to plot currentscapes.

As in https://datadryad.org/stash/dataset/doi:10.5061/dryad.d0779mb.
The main function is based on scripts from the susmentioned article,
that are under the CC0 1.0 Universal (CC0 1.0) Public Domain Dedication license.
"""

# pylint: disable=too-many-statements
import json
import logging
from math import gcd
import os

import numpy as np
import matplotlib
import matplotlib.pyplot as plt

import palettable as pltb

logger = logging.getLogger(__name__)


def replace_defaults(config, new_config):
    """Recursive fct. Replace defaults value with user input."""
    for key, item in new_config.items():
        if isinstance(item, dict):
            item = replace_defaults(config[key], item)
        config[key] = item

    return config


def set_default_config(c):
    """Set non-specified values in config to default.

    Args:
        c (str or dict): config dict or path to json config.
            values from c are added or replace those from default config.
    """
    if c is None:
        c = {}
    elif isinstance(c, str):
        with open(c, "r") as f:
            c = json.load(f)

    config = {}
    show = {}
    show["labels"] = True
    show["ticklabels"] = True
    show["legend"] = True
    config["show"] = show

    current = {}
    current["ticks"] = [5, 50, 500]
    current["ylim"] = (0.01, 1500)
    current["units"] = "[pA]"
    current["color"] = "black"
    config["current"] = current

    currentscape = {}
    currentscape["in_label"] = "inward %"
    currentscape["out_label"] = "outward %"
    # if too low, white pixels can appear at the bottom of currentscape plots
    # because of rounding errors.
    currentscape["y_resolution"] = 10000
    # thickness of black line separating the two inward & outward currentscapes.
    # in %age of y size of plot.
    currentscape["black_line_thickness"] = 2
    # data along x axis are summed up into chunks when pattern use is True. Put to 1 to disable.
    currentscape["x_chunksize"] = 50
    config["currentscape"] = currentscape

    colormap = {}
    colormap["name"] = "Set1"
    # color number. Taken into account only if pattern use is True
    colormap["n_colors"] = 8
    config["colormap"] = colormap

    pattern = {}
    pattern["use"] = False
    pattern["patterns"] = ["", "/", "\\", "x", ".", "o", "+"]
    pattern["density"] = 5
    pattern["linewidth"] = 0.2
    pattern["color"] = "black"
    config["pattern"] = pattern

    voltage = {}
    voltage["ticks"] = (-50, -20)
    voltage["ylim"] = (-90, 30)
    voltage["units"] = "[mV]"
    voltage["color"] = "black"
    voltage["horizontal_lines"] = True
    config["voltage"] = voltage

    output = {}
    output["savefig"] = False
    output["dir"] = "."
    output["fname"] = "fig"
    output["extension"] = "png"
    output["dpi"] = 400
    output["transparent"] = False
    config["output"] = output

    legend = {}
    legend["textsize"] = 6
    legend["bgcolor"] = "lightgrey"
    # 1. : top of legend is at the same level as top of currentscape plot.
    # higher value put legend higher in figure.
    legend["ypos"] = 1.0
    legend["handlelength"] = 1.4  # forced to 0 if pattern use is False
    config["legend"] = legend

    config["title"] = None
    config["figsize"] = (3, 4)
    config["labelpad"] = 1
    config["textsize"] = 6
    config["titlesize"] = 12

    adjust_ = {}
    adjust_["left"] = None
    adjust_["right"] = 0.85
    adjust_["top"] = None
    adjust_["bottom"] = None
    config["adjust"] = adjust_

    new_config = replace_defaults(config, c)

    # for compatibility with older versions
    if "cmap" in new_config["currentscape"]:
        new_config["colormap"]["name"] = new_config["currentscape"]["cmap"]
    if "legendtextsize" in new_config:
        new_config["legend"]["textsize"] = new_config["legendtextsize"]
    if "legendbgcolor" in config:
        new_config["legend"]["bgcolor"] = new_config["legendbgcolor"]

    return new_config


def remove_ticks_and_frame(ax):
    """Remove ticks (but not ytick label) and frame."""
    ax.tick_params(
        axis="x",  # changes apply to the x-axis
        which="both",  # both major and minor ticks are affected
        bottom=False,  # ticks along the bottom edge are off
        top=False,  # ticks along the top edge are off
        labelbottom=False,  # labels along the bottom edge are off
    )
    ax.tick_params(
        axis="y",  # changes apply to the x-axis
        which="both",  # both major and minor ticks are affected
        left=False,  # ticks along the bottom edge are off
        right=False,  # ticks along the top edge are off
        pad=0,
    )
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.spines["bottom"].set_visible(False)
    ax.spines["left"].set_visible(False)


def remove_ticks_and_frame_for_bar_plot(ax):
    """Remove all ticks (including ytick label) and top & bottom frames."""
    ax.tick_params(
        axis="x",  # changes apply to the x-axis
        which="both",  # both major and minor ticks are affected
        bottom=False,  # ticks along the bottom edge are off
        top=False,  # ticks along the top edge are off
        labelbottom=False,  # labels along the bottom edge are off
    )
    ax.tick_params(
        axis="y",  # changes apply to the x-axis
        which="both",  # both major and minor ticks are affected
        left=False,  # ticks along the bottom edge are off
        right=False,  # ticks along the top edge are off
        labelleft=False,  # labels along left edge are off
    )
    ax.spines["top"].set_visible(False)
    ax.spines["bottom"].set_visible(False)


def adjust(adjust_left, adjust_right, adjust_top, adjust_bottom):
    """Adjust Subplots."""
    plt.subplots_adjust(wspace=0, hspace=0)
    if adjust_left:
        plt.subplots_adjust(left=adjust_left)
    if adjust_right:
        plt.subplots_adjust(right=adjust_right)
    if adjust_top:
        plt.subplots_adjust(top=adjust_top)
    if adjust_bottom:
        plt.subplots_adjust(bottom=adjust_bottom)


def set_label(ax, x, y, label, textsize):
    """Set text as label on the y axis."""
    ax.text(
        x,
        y,
        label,
        horizontalalignment="right",
        verticalalignment="center",
        rotation="vertical",
        size=textsize,
    )


def set_legend(ax, im, curr_names, bg_color, ypos):
    """Set each current name color-coded in legend.

    Args:
        ax (matplotlib.axes): currentscape axis
        im (matplotlib.image.AxesImage): currentscape image
        curr_names (list of str): legend labels / current names
        bg_color (color): background color for legend box
        ypos (float): y-axis position of legend box. 1 is top of axis.
    """
    # create a patch (proxy artist) for every current
    patches = [
        matplotlib.patches.Patch(label=curr_names[i]) for i in range(len(curr_names))
    ]
    # put those patched as legend-handles into the legend
    leg = ax.legend(
        handles=patches,
        bbox_to_anchor=(1.01, ypos),
        loc=2,
        borderaxespad=0.0,
        facecolor=bg_color,
        edgecolor="black",
        fancybox=False,  # disable round edges
    )
    leg.get_frame().set_linewidth(0.5)  # set border thickness
    # set legend label color & boldness
    for i_color, text in enumerate(leg.texts):
        text.set_color(im.cmap(im.norm(i_color)))
        text.set_weight("bold")


def set_legend_with_hatches(ax, cmap, bg_color, ypos, n_colors, mapper):
    """Create legend and color each current name.

    Args:
        ax (matplotlib.axes): currentscape axis
        cmap (matplotlib.colors.Colormap): colormap
        bg_color (color): background color for legend box
        ypos (float): y-axis position of legend box. 1 is top of axis.
        n_colors (int): number of colors used to display data
        mapper (int): number used to mix color and patterns
    """
    leg = ax.legend(
        bbox_to_anchor=(1.01, ypos),
        loc=2,
        borderaxespad=0.0,
        facecolor=bg_color,
        edgecolor="black",
        fancybox=False,  # disable round edges
    )

    leg.get_frame().set_linewidth(0.5)  # set border thickness
    # set legend label color & boldness
    for i_color, text in enumerate(leg.texts):
        text.set_color(cmap((mapper * i_color) % n_colors))
        text.set_weight("bold")


def create_cscape_image(cnorm, resy, lw):
    """Create currentscape image.

    Args:
        cnorm (numpy matrix): contains fractions of current for each time, from 0 to 1 (or -1).
        resy (int): y-axis resolution
            (must be high >>1000 or else rounding errors produce white pixels)
        lw (int): black line (separating the two currentscape plots) thickness
            in percentage of the plot height.
    """
    # fill with a number that do not correspond to a current, in case there is no current.
    impos = np.full((resy, np.shape(cnorm)[-1]), np.shape(cnorm)[0] + 1)
    imneg = np.full((resy, np.shape(cnorm)[-1]), np.shape(cnorm)[0] + 1)

    times = np.arange(0, np.shape(cnorm)[-1])
    for t in times:
        lastpercent = 0
        for numcurr, curr in enumerate(cnorm):
            if curr[t] > 0:
                percent = int(curr[t] * (resy))
                impos[lastpercent : lastpercent + percent, t] = numcurr
                lastpercent = lastpercent + percent
    for t in times:
        lastpercent = 0
        for numcurr, curr in enumerate(cnorm):
            if curr[t] < 0:
                percent = int(abs(curr[t]) * (resy))
                imneg[lastpercent : lastpercent + percent, t] = numcurr
                lastpercent = lastpercent + percent
    # append fake data to produce a black line separating inward & outward
    # cannot draw with plot, because that would hide data because of adjust (h=0)
    line_thickness = int(resy * lw / 100.0)
    if line_thickness < 1:
        line = np.full((1, np.shape(cnorm)[-1]), np.shape(cnorm)[0])
    else:
        line = np.full((line_thickness, np.shape(cnorm)[-1]), np.shape(cnorm)[0])
    return np.vstack((impos, line, imneg))


def data_processing(currents, c):
    """Process data for the plot."""
    # make a copy of currents
    curr = np.array(currents)
    cpos = curr.copy()
    cpos[curr < 0] = 0
    cneg = curr.copy()
    cneg[curr > 0] = 0

    normapos = np.sum(abs(np.array(cpos)), axis=0)
    normaneg = np.sum(abs(np.array(cneg)), axis=0)
    npPD = normapos
    nnPD = normaneg
    cnorm = curr.copy()
    cnorm[curr > 0] = (abs(curr) / normapos)[curr > 0]
    cnorm[curr < 0] = -(abs(curr) / normaneg)[curr < 0]

    if c["pattern"]["use"]:
        im0 = [cpos / npPD, abs(cneg) / nnPD]
    else:
        im0 = create_cscape_image(
            cnorm,
            c["currentscape"]["y_resolution"],
            c["currentscape"]["black_line_thickness"],
        )

    N_curr = len(cnorm)  # number of currents

    return im0, npPD, nnPD, N_curr


def get_colors(cmap, n_col):
    """Get colors from colormap, depending on maximum number of colors.

    Args:
        cmap (str): colormap name
        n_col (int): number of colors to extract
    Returns:
        a list of matplotlib colors
    """
    if "." in cmap:  # is from palettable module
        x = pltb
        # we want to retrieve e.g. pltb.cartocolors.qualitative.Antique_8.mpl_colors
        # from string "cartocolors.qualitative.Antique_8"
        for attr in cmap.split("."):
            x = getattr(x, attr)
        return x.mpl_colors[:n_col]
    else:  # is from matplotlib
        new_cmap = matplotlib.cm.get_cmap(cmap, n_col)
        return list(new_cmap(range(n_col)))


def get_colormap(cmap, n_colors, use_patterns, N_curr):
    """Get colormap according to input, and add black then white colors at the end.

    Args:
        cmap (str): colormap name
        n_colors (int): number of colors to extract IF use_patterns and n_colors>N_curr
        use_patterns (bool): True if currentscape plot uses bars and mixes color and pattern
        N_curr (int): number of currents
    """
    if use_patterns and N_curr > n_colors:
        colors = get_colors(cmap, n_colors)
    else:
        colors = get_colors(cmap, N_curr)

    colors.append(
        np.array([0.0, 0.0, 0.0, 1.0])
    )  # append black, for black line separating currentscapes
    colors.append(
        np.array([1.0, 1.0, 1.0, 1.0])
    )  # append white. default color when there is no current.

    return matplotlib.colors.ListedColormap(colors)


def has_common_divisor(n1, n2, n):
    """Return True if n has a common divisor with either n1 or n2."""
    if gcd(n, n1) == 1 and gcd(n, n2) == 1:
        return False
    return True


def create_mapper(n_colors, n_patterns):
    """Find a number n that will be useful to find pairs (color, pattern).

    Those pairs should not have the same color in a row and the same pattern in a row.
    n should work as in the following example.

    Example:
        for i in range(currents):
            color = (n*i) % n_colors
            pattern = ( (n*i) // n_colors) % n_patterns

    Constraints:
        * For two patterns to be different in a row: n>=n_patterns
        * n, n_colors, n_patterns should not have a common divisor.
    """
    mapper = n_patterns
    while has_common_divisor(n_colors, n_patterns, mapper):
        mapper += 1
    return mapper


def sum_chunks(x, chunk_size):
    """Compute the sums of parts of an array.

    Taken from https://stackoverflow.com/questions/18582544/sum-parts-of-numpy-array.
    """
    rows, cols = x.shape
    x = x.reshape(int(x.size / chunk_size), chunk_size)
    return x.sum(axis=1).reshape(rows, int(cols / chunk_size))


def chunksize_warning(cs, len_curr, new_cs):
    """Warns that chunksize has been re-set."""
    logger.warning(
        "x-chunksize (%d) should be a divisor of data size (%d)." % (cs, len_curr)
        + " x-chunksize has been reset to %d." % new_cs
    )


def check_chunksize(cs, len_curr):
    """Set chunksize to a divisor of the data size if not the case.

    Args:
        cs (int): chunksize of data to check
        len_curr (int): data size (length of one current list)
    """
    if cs > len_curr:
        chunksize_warning(cs, len_curr, len_curr)
        return len_curr
    elif cs < 1:
        chunksize_warning(cs, len_curr, 1)
        return 1

    # if chunksize is a divisor: end of loop.
    # else: decrement chunksize by one and retest until a divisor is found.
    i = 0
    while len_curr // (cs - i) != len_curr / (cs - i):
        i += 1

    if i != 0:
        chunksize_warning(cs, len_curr, cs - i)
    return cs - i


def plot_currentscape_with_bars(ax, currs, cmap, c, mapper, add_black_line=False):
    """Plot currentscape using bars instead of imshow.

    That way, hatches (patterns) can be used.

    Args:
        ax (matplotlib.axes): currentscape axis
        currs (list of list of floats): currents fraction (from 0 to 1(or -1))
        cmap (matplotlib.colors.Colormap): colormap
        c (dict): config
        mapper (int): number used to mix color and patterns
        add_black_line (bool): True to add a black line at the bottom of the plot.
    """
    patterns = [x * c["pattern"]["density"] for x in c["pattern"]["patterns"]]
    n_colors = c["colormap"]["n_colors"]
    chunksize = c["currentscape"]["x_chunksize"]

    chunksize = check_chunksize(int(chunksize), len(currs[0]))

    currs = sum_chunks(currs, chunksize)  # reduce data x resolution

    size = len(currs[0])
    x = range(size)
    # stack from the top to bottom, like in create_cscape_image func.
    bottom = np.full(size, float(chunksize))
    for i, curr in enumerate(currs):
        bottom -= curr
        ax.bar(
            x,
            curr,
            color=cmap((mapper * i) % n_colors),
            edgecolor=c["pattern"]["color"],
            linewidth=0,  # do not draw edges
            width=1,  # fill all the space between two bars
            hatch=patterns[((mapper * i) // n_colors) % len(patterns)],
            bottom=bottom,
            align="edge",  # Align the left edges of the bars with the x positions.
            label=c["current"]["names"][i],  # for legend
        )
    # add at black line a the bottom of the plot.
    # cannot use spines because with subplot_adjust(h=0),
    # spines overlap on neighboor plot and hide part of the data
    if add_black_line:
        y_bottom = -chunksize * c["currentscape"]["black_line_thickness"] / 100.0
        ax.fill_between([0, size], [y_bottom, y_bottom], color="black")
        ax.set_ylim(y_bottom, chunksize)
    else:
        ax.set_ylim(0, chunksize)
    ax.set_xlim(0, size)


def plot_voltage_trace(c, voltage, rows_tot, xmax):
    """Plot voltage trace."""
    ax = plt.subplot2grid((rows_tot, 1), (0, 0), rowspan=2)
    t = np.arange(0, len(voltage))
    ax.plot(t, voltage, color=c["voltage"]["color"], lw=1.0)
    ax.plot(
        t,
        np.ones(len(t)) * c["voltage"]["ticks"][0],
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


def plot_inward_current(c, npPD, rows_tot, xmax):
    """Plot inward current in log scale."""
    ax = plt.subplot2grid((rows_tot, 1), (2, 0), rowspan=1)
    ax.fill_between(np.arange(len((npPD))), (npPD), color=c["current"]["color"])
    for tick in c["current"]["ticks"]:
        ax.plot(tick * np.ones(len(npPD)), color="black", ls=":", lw=1)
    ax.set_yscale("log")
    ax.set_ylim(c["current"]["ylim"])
    ax.set_xlim(0, xmax)
    if c["show"]["labels"]:
        ax.set_ylabel("+" + c["current"]["units"], labelpad=c["labelpad"])
    if c["show"]["ticklabels"]:
        ax.set_yticks(c["current"]["ticks"])
        ax.get_yaxis().set_major_formatter(matplotlib.ticker.ScalarFormatter())
    remove_ticks_and_frame(ax)


def plot_outward_current(c, nnPD, rowspan, rows_tot, xmax):
    """Plot outward current in log scale."""
    ax = plt.subplot2grid((rows_tot, 1), (rowspan + 3, 0), rowspan=1)
    ax.fill_between(np.arange(len((nnPD))), (nnPD), color=c["current"]["color"])
    for tick in c["current"]["ticks"]:
        ax.plot(tick * np.ones(len(nnPD)), color="black", ls=":", lw=1)
    ax.set_yscale("log")
    if c["show"]["labels"]:
        ax.set_ylabel("-" + c["current"]["units"], labelpad=c["labelpad"])
    if c["show"]["ticklabels"]:
        ax.set_yticks(c["current"]["ticks"])
        ax.get_yaxis().set_major_formatter(matplotlib.ticker.ScalarFormatter())
    remove_ticks_and_frame(ax)
    # somehow, set_ylim is not taken into account if it is set before set_yticks
    ax.set_ylim(c["current"]["ylim"][1], c["current"]["ylim"][0])  # inverse axis
    ax.set_xlim(0, xmax)


def plot_current_shares_with_bars(c, im0, rows_tot, n_colors, cmap):
    """Plot current percentages with barplots."""
    n_patterns = len(c["pattern"]["patterns"])
    mapper = create_mapper(n_colors, n_patterns)
    # outward currents
    ax = plt.subplot2grid((rows_tot, 1), (3, 0), rowspan=2)
    plot_currentscape_with_bars(ax, im0[0], cmap, c, mapper, True)
    remove_ticks_and_frame_for_bar_plot(ax)
    # labels
    if c["show"]["labels"]:
        ax.set_ylabel(c["currentscape"]["out_label"], labelpad=c["labelpad"])
    # legend
    if c["show"]["legend"]:
        set_legend_with_hatches(
            ax, cmap, c["legend"]["bgcolor"], c["legend"]["ypos"], n_colors, mapper
        )

    # inward currents
    ax = plt.subplot2grid((rows_tot, 1), (5, 0), rowspan=2)
    plot_currentscape_with_bars(ax, im0[1], cmap, c, mapper)
    remove_ticks_and_frame_for_bar_plot(ax)
    if c["show"]["labels"]:
        ax.set_ylabel(c["currentscape"]["in_label"], labelpad=c["labelpad"])


def plot_current_shares_with_imshow(c, im0, rowspan, rows_tot, cmap, xmax, N_curr):
    """Plot current percentage using imshow."""
    resy = c["currentscape"]["y_resolution"]
    black_line_size = int(resy * c["currentscape"]["black_line_thickness"] / 100.0)

    ax = plt.subplot2grid((rows_tot, 1), (3, 0), rowspan=rowspan)
    im = ax.imshow(
        im0[::1, ::1],
        interpolation="nearest",
        aspect="auto",
        cmap=cmap,
    )

    plt.gca().xaxis.set_major_locator(plt.NullLocator())
    plt.gca().yaxis.set_major_locator(plt.NullLocator())

    # set limits
    ax.set_ylim(2 * resy + black_line_size, 0)
    ax.set_xlim(0, xmax)
    # data + black for separating line + white for empty data
    im.set_clim(0, N_curr + 1)

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
            im,
            c["current"]["names"],
            c["legend"]["bgcolor"],
            c["legend"]["ypos"],
        )


def create_figure(voltage, im0, npPD, nnPD, c, N_curr):
    """Create the currentscape figure.

    Args:
        voltage (list of floats): voltage data
        im0 (1 or 2 numpy matrix): matrix containing the currentscapes
            there is 1 numpy matrix if plotting with imshow or 2 if plotting with bars
        npPD (nparray): sum of all positive currents at each time
        nnPD (nparray): sum of all (absolute values of) negative currents at each time
        c (dict): config
        N_curr (int): number of currents
    """
    use_patterns = c["pattern"]["use"]
    # set text size
    plt.rcParams["axes.labelsize"] = c["textsize"]
    plt.rcParams["ytick.labelsize"] = c["textsize"]
    plt.rcParams["legend.fontsize"] = c["legend"]["textsize"]
    # remove legend handles
    if use_patterns:
        plt.rcParams["hatch.linewidth"] = c["pattern"]["linewidth"]
        plt.rcParams["legend.handlelength"] = c["legend"]["handlelength"]
    else:
        plt.rcParams["legend.handletextpad"] = 0
        plt.rcParams["legend.labelspacing"] = 0
        plt.rcParams["legend.handlelength"] = 0

    n_colors = c["colormap"]["n_colors"]
    cmap = get_colormap(c["colormap"]["name"], n_colors, use_patterns, N_curr)

    if use_patterns:
        rowspan = 4
        rows_tot = 8
    else:
        rowspan = 3
        rows_tot = 7
    # START PLOT
    fig = plt.figure(figsize=c["figsize"])
    if c["title"]:
        fig.suptitle(c["title"], fontsize=c["titlesize"])

    xmax = len(voltage)

    # PLOT VOLTAGE TRACE
    plot_voltage_trace(c, voltage, rows_tot, xmax)

    # PLOT TOTAL INWARD CURRENT IN LOG SCALE
    plot_inward_current(c, npPD, rows_tot, xmax)

    # PLOT CURRENT SHARES
    if use_patterns:
        plot_current_shares_with_bars(c, im0, rows_tot, n_colors, cmap)
    else:
        plot_current_shares_with_imshow(c, im0, rowspan, rows_tot, cmap, xmax, N_curr)

    # PLOT TOTAL OUTWARD CURRENT IN LOG SCALE
    plot_outward_current(c, nnPD, rowspan, rows_tot, xmax)

    adjust(
        c["adjust"]["left"],
        c["adjust"]["right"],
        c["adjust"]["top"],
        c["adjust"]["bottom"],
    )

    return fig


def save_figure(fig, c):
    """Save figure in output according to config file."""
    if not os.path.exists(c["output"]["dir"]):
        os.makedirs(c["output"]["dir"])
    out_path = (
        os.path.join(c["output"]["dir"], c["output"]["fname"])
        + "."
        + c["output"]["extension"]
    )
    fig.savefig(
        out_path, dpi=c["output"]["dpi"], transparent=c["output"]["transparent"]
    )


def plot_currentscape(voltage, currents, config):
    """Returns a figure containing current scapes."""
    # load config and set default to unspecified terms
    c = set_default_config(config)

    # currenscape data processing
    print("processing data")
    im0, npPD, nnPD, N_curr = data_processing(currents, c)

    # plot currentscape
    print("producing figure")
    fig = create_figure(voltage, im0, npPD, nnPD, c, N_curr)

    if c["output"]["savefig"]:
        save_figure(fig, c)

    return fig
