"""Module for plotting currentscapes as in https://datadryad.org/stash/dataset/doi:10.5061/dryad.d0779mb."""
"""The main function is based on scripts from the susmentioned article
    that are under the CC0 1.0 Universal (CC0 1.0) Public Domain Dedication license."""

from pylab import *
import json
import os


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
        f = open(c, "r")
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
    voltage["ticks"] = None
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
    config["legendsize"] = 6
    config["titlesize"] = 12

    adjust = {}
    adjust["left"] = None
    adjust["right"] = 0.85
    adjust["top"] = None
    adjust["bottom"] = None
    config["adjust"] = adjust

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
    subplots_adjust(wspace=0, hspace=0)
    if adjust_left:
        subplots_adjust(left=adjust_left)
    if adjust_right:
        subplots_adjust(right=adjust_right)
    if adjust_top:
        subplots_adjust(top=adjust_top)
    if adjust_bottom:
        subplots_adjust(bottom=adjust_bottom)


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


def set_legend(ax, im, curr_names):
    """Set each current name color-coded in legend."""
    # create a patch (proxy artist) for every current
    patches = [
        matplotlib.patches.Patch(label=curr_names[i]) for i in range(len(curr_names))
    ]
    # put those patched as legend-handles into the legend
    leg = ax.legend(
        handles=patches, bbox_to_anchor=(1.01, 1), loc=2, borderaxespad=0.0,
    )
    # set legend label color
    for i_color, text in enumerate(leg.texts):
        text.set_color(im.cmap(im.norm(i_color)))


def plotCurrentscape(voltage, currents, config):
    """Returns a figure containing current scapes."""
    # load config and set default to unspecified terms
    c = set_default_config(config)
    # make a copy of currents
    # CURRENTSCAPE CALCULATION STARTS HERE.
    curr = array(currents)
    cpos = curr.copy()
    cpos[curr < 0] = 0
    cneg = curr.copy()
    cneg[curr > 0] = 0

    normapos = sum(abs(array(cpos)), axis=0)
    normaneg = sum(abs(array(cneg)), axis=0)
    npPD = normapos
    nnPD = normaneg
    cnorm = curr.copy()
    cnorm[curr > 0] = (abs(curr) / normapos)[curr > 0]
    cnorm[curr < 0] = -(abs(curr) / normaneg)[curr < 0]

    resy = 1000
    impos = zeros((resy, shape(cnorm)[-1]))
    imneg = zeros((resy, shape(cnorm)[-1]))

    times = arange(0, shape(cnorm)[-1])
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
    im0 = vstack((impos, imneg))
    # CURRENTSCAPE CALCULATION ENDS HERE.

    # PLOT CURRENTSCAPE
    # adjust_left = None
    # adjust_right = 0.82
    # adjust_top = None
    # adjust_bottom = None
    # curr_names = [
    #     "Ih",
    #     "Ca_HVA2",
    #     "Ca_LVAst",
    #     "SK_E2",
    #     "SKv3_1",
    #     "K_Pst",
    #     "K_Tst",
    #     "NaTg",
    # ]
    # voltage_ticks = [-50, -20]
    # voltage_ylim = (-90, 30)
    # voltage_units = "[mV]"
    # voltage_color = "black"
    # current_ticks = [5, 50, 500]
    # current_ylim = (0.01, 1500)
    # current_units = "[pA]"
    # current_color = "black"
    # in_label = "inward %"
    # out_label = "outward %"

    # labelpad = 1
    # elcolormap = "Set1"
    # title = "XX pA"
    # figsize = (3, 4)
    # textsize = 6
    # legendsize = 6
    # titlesize = 12

    # set voltage ticks if not forced by config
    if not c["voltage"]["ticks"]:
        low_tick = int(voltage[0])  # round down
        high_tick = round(low_tick + 30, -1)
        c["voltage"]["ticks"] = [low_tick, high_tick]
    # set text size
    rcParams["axes.labelsize"] = c["textsize"]
    rcParams["ytick.labelsize"] = c["textsize"]
    rcParams["legend.fontsize"] = c["legendsize"]
    # remove legend handles
    rcParams["legend.handletextpad"] = 0
    rcParams["legend.labelspacing"] = 0
    rcParams["legend.handlelength"] = 0

    # print(c)
    resy = c["currentscape"]["y_resolution"]

    # START PLOT
    fig = figure(figsize=c["figsize"])
    if c["title"]:
        fig.suptitle(c["title"], fontsize=c["titlesize"])

    # PLOT VOLTAGE TRACE
    xmax = len(voltage)
    ax = subplot2grid((7, 1), (0, 0), rowspan=2)
    t = arange(0, len(voltage))
    plot(t, voltage, color=c["voltage"]["color"], lw=1.0)
    plot(
        t, ones(len(t)) * c["voltage"]["ticks"][0], ls="dashed", color="black", lw=0.75
    )
    vlines(1, c["voltage"]["ticks"][0], c["voltage"]["ticks"][-1], lw=1, color="black")
    ylim(c["voltage"]["ylim"])
    xlim(0, xmax)
    if c["show"]["labels"]:
        ax.set_ylabel(c["voltage"]["units"], labelpad=c["labelpad"])
    if c["show"]["ticklabels"]:
        ax.set_yticks(c["voltage"]["ticks"])
    remove_ticks_and_frame(ax)

    # PLOT TOTAL INWARD CURRENT IN LOG SCALE
    ax = subplot2grid((7, 1), (2, 0), rowspan=1)
    fill_between(arange(len((npPD))), (npPD), color=c["current"]["color"])
    for tick in c["current"]["ticks"]:
        plot(tick * ones(len(nnPD)), color="black", ls=":", lw=1)
    yscale("log")
    ylim(c["current"]["ylim"])
    xlim(0, xmax)
    if c["show"]["labels"]:
        ax.set_ylabel("+" + c["current"]["units"], labelpad=c["labelpad"])
    if c["show"]["ticklabels"]:
        ax.set_yticks(c["current"]["ticks"])
        ax.get_yaxis().set_major_formatter(matplotlib.ticker.ScalarFormatter())
    remove_ticks_and_frame(ax)

    # PLOT CURRENT SHARES
    ax = subplot2grid((7, 1), (3, 0), rowspan=3)
    im = imshow(
        im0[::1, ::1],
        interpolation="nearest",
        aspect="auto",
        cmap=c["currentscape"]["cmap"],
    )
    ylim(2 * resy, 0)
    plot(resy * ones(len(npPD)), color="black", lw=2)
    plt.gca().xaxis.set_major_locator(plt.NullLocator())
    plt.gca().yaxis.set_major_locator(plt.NullLocator())
    xlim(0, xmax)
    clim(0, len(cnorm))  # not sure about the vmax
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
        set_legend(ax, im, c["current"]["names"])

    # PLOT TOTAL OUTWARD CURRENT IN LOG SCALE
    ax = subplot2grid((7, 1), (6, 0), rowspan=1)
    fill_between(arange(len((nnPD))), (nnPD), color=c["current"]["color"])
    for tick in c["current"]["ticks"]:
        plot(tick * ones(len(nnPD)), color="black", ls=":", lw=1)
    yscale("log")
    ylim(c["current"]["ylim"][1], c["current"]["ylim"][0])  # inverse axis
    xlim(0, xmax)
    if c["show"]["labels"]:
        ax.set_ylabel("-" + c["current"]["units"], labelpad=c["labelpad"])
    if c["show"]["ticklabels"]:
        ax.set_yticks(c["current"]["ticks"])
        ax.get_yaxis().set_major_formatter(matplotlib.ticker.ScalarFormatter())
    remove_ticks_and_frame(ax)

    adjust(
        c["adjust"]["left"],
        c["adjust"]["right"],
        c["adjust"]["top"],
        c["adjust"]["bottom"],
    )

    if c["output"]["savefig"]:
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

    return fig
