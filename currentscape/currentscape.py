"""Module to plot currentscapes.

As in https://datadryad.org/stash/dataset/doi:10.5061/dryad.d0779mb.
The main function is based on scripts from the susmentioned article,
that are under the CC0 1.0 Universal (CC0 1.0) Public Domain Dedication license.
"""

# pylint: disable=too-many-statements
import json
import os
import numpy as np
import matplotlib
import matplotlib.pyplot as plt


def replace_defaults(config, new_config):
    """Recursive fct. Replace defaults value with user input."""
    for key, item in new_config.items():
        if isinstance(item, dict):
            item = replace_defaults(config[key], item)
        config[key] = item

    return config


def set_default_config(c):
    """Set non-specified values in config to default."""
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
    currentscape["cmap"] = "Set1"
    currentscape["y_resolution"] = 1000
    config["currentscape"] = currentscape

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
    output["fname"] = ""
    output["extension"] = "png"
    output["dpi"] = 400
    output["transparent"] = False
    config["output"] = output

    config["title"] = None
    config["figsize"] = (3, 4)
    config["labelpad"] = 1
    config["textsize"] = 6
    config["legendtextsize"] = 6
    config["legendbgcolor"] = "lightgrey"
    config["titlesize"] = 12

    adjust_ = {}
    adjust_["left"] = None
    adjust_["right"] = 0.85
    adjust_["top"] = None
    adjust_["bottom"] = None
    config["adjust"] = adjust_

    return replace_defaults(config, c)


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


def set_legend(ax, im, curr_names, bg_color):
    """Set each current name color-coded in legend."""
    # create a patch (proxy artist) for every current
    patches = [
        matplotlib.patches.Patch(label=curr_names[i]) for i in range(len(curr_names))
    ]
    # put those patched as legend-handles into the legend
    leg = ax.legend(
        handles=patches,
        bbox_to_anchor=(1.01, 1),
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


def create_cscape_image(cnorm, resy):
    """Create currentscape image."""
    impos = np.zeros((resy, np.shape(cnorm)[-1]))
    imneg = np.zeros((resy, np.shape(cnorm)[-1]))

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
    return np.vstack((impos, imneg))


def data_processing(currents, resy=1000):
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

    im0 = create_cscape_image(cnorm, resy)

    N_curr = len(cnorm)  # number of currents

    return im0, npPD, nnPD, N_curr


def create_figure(voltage, im0, npPD, nnPD, c, N_curr, resy=1000):
    """Create the currentscape figure."""
    # set text size
    plt.rcParams["axes.labelsize"] = c["textsize"]
    plt.rcParams["ytick.labelsize"] = c["textsize"]
    plt.rcParams["legend.fontsize"] = c["legendtextsize"]
    # remove legend handles
    plt.rcParams["legend.handletextpad"] = 0
    plt.rcParams["legend.labelspacing"] = 0
    plt.rcParams["legend.handlelength"] = 0

    # START PLOT
    fig = plt.figure(figsize=c["figsize"])
    if c["title"]:
        fig.suptitle(c["title"], fontsize=c["titlesize"])

    # PLOT VOLTAGE TRACE
    xmax = len(voltage)
    ax = plt.subplot2grid((7, 1), (0, 0), rowspan=2)
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

    # PLOT TOTAL INWARD CURRENT IN LOG SCALE
    ax = plt.subplot2grid((7, 1), (2, 0), rowspan=1)
    ax.fill_between(np.arange(len((npPD))), (npPD), color=c["current"]["color"])
    for tick in c["current"]["ticks"]:
        ax.plot(tick * np.ones(len(nnPD)), color="black", ls=":", lw=1)
    ax.set_yscale("log")
    ax.set_ylim(c["current"]["ylim"])
    ax.set_xlim(0, xmax)
    if c["show"]["labels"]:
        ax.set_ylabel("+" + c["current"]["units"], labelpad=c["labelpad"])
    if c["show"]["ticklabels"]:
        ax.set_yticks(c["current"]["ticks"])
        ax.get_yaxis().set_major_formatter(matplotlib.ticker.ScalarFormatter())
    remove_ticks_and_frame(ax)

    # PLOT CURRENT SHARES
    ax = plt.subplot2grid((7, 1), (3, 0), rowspan=3)
    im = ax.imshow(
        im0[::1, ::1],
        interpolation="nearest",
        aspect="auto",
        cmap=c["currentscape"]["cmap"],
    )
    ax.set_ylim(2 * resy, 0)
    ax.plot(resy * np.ones(len(npPD)), color="black", lw=2)
    plt.gca().xaxis.set_major_locator(plt.NullLocator())
    plt.gca().yaxis.set_major_locator(plt.NullLocator())
    ax.set_xlim(0, xmax)
    im.set_clim(0, N_curr)  # not sure about the vmax
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
        set_legend(ax, im, c["current"]["names"], c["legendbgcolor"])

    # PLOT TOTAL OUTWARD CURRENT IN LOG SCALE
    ax = plt.subplot2grid((7, 1), (6, 0), rowspan=1)
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
    resy = c["currentscape"]["y_resolution"]  # y resolution for current shares

    # currenscape data processing
    print("processing data")
    im0, npPD, nnPD, N_curr = data_processing(currents, resy)

    # plot currentscape
    print("producing figure")
    fig = create_figure(voltage, im0, npPD, nnPD, c, N_curr, resy)

    if c["output"]["savefig"]:
        save_figure(fig, c)

    return fig
