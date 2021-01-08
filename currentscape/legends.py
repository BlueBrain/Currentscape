"""Legends related functions."""
# pylint: disable=wrong-import-position
import matplotlib

matplotlib.use("agg")  # to avoid tkinter error
from matplotlib.legend_handler import HandlerTuple

from currentscape.plotting import select_color


def base_legend(
    ax, curr_names, bg_color, ypos, idx_names=None, handlelength=None, lines=False
):
    """Returns a legend with all current names.

    Args:
        ax (matplotlib.axes): currentscape axis
        curr_names (list of str): legend labels / current names
        bg_color (color): background color for legend box
        ypos (float): y-axis position of legend box. 1 is top of axis.
        idx_names (ndarray of ints): indexes to new name order (new_names = names[idx_names])
        handlelength (float): size of the handles.
            Takes default value if None. No handles displayed if 0.
        lines (bool): if True, get lines as handles. if False, get patches as handles.
    """
    if idx_names is None:
        idx_names = range(len(curr_names))
    # create a patch (proxy artist) or a line for every current
    if lines:
        handles = [
            matplotlib.lines.Line2D([], [], label=curr_names[i]) for i in idx_names
        ]
    else:
        handles = [matplotlib.patches.Patch(label=curr_names[i]) for i in idx_names]
    # put those patched as legend-handles into the legend
    leg = ax.legend(
        handles=handles,
        bbox_to_anchor=(1.01, ypos),
        loc=2,
        borderaxespad=0.0,
        facecolor=bg_color,
        edgecolor="black",
        fancybox=False,  # disable round edges
        handlelength=handlelength,
    )
    leg.get_frame().set_linewidth(0.5)  # set border thickness

    return leg


def set_legend(ax, cmap, curr_names, bg_color, ypos, idx_names=None, handlelength=0):
    """Set each current name color-coded in legend.

    Args:
        ax (matplotlib.axes): currentscape axis
        cmap (matplotlib.colors.Colormap): colormap
        curr_names (list of str): legend labels / current names
        bg_color (color): background color for legend box
        ypos (float): y-axis position of legend box. 1 is top of axis.
        idx_names (ndarray of ints): indexes to new name order (new_names = names[idx_names])
        handlelength (float): size of the handles.
            Takes default value if None. No handles displayed if 0.
    """
    leg = base_legend(ax, curr_names, bg_color, ypos, idx_names, handlelength)

    # set legend label color & boldness
    for i_color, text in enumerate(leg.texts):
        # + 2 because there is black and white at the end of cmap
        text.set_color(select_color(cmap, i_color, len(curr_names)))
        text.set_weight("bold")


def set_legend_with_hatches(ax, cmap, mapper, c, idx_names):
    """Create legend and color each current name, and set handles color and pattern.

    Args:
        ax (matplotlib.axes): currentscape axis
        cmap (matplotlib.colors.Colormap): colormap
        mapper (int): number used to mix color and patterns
        c (dict): config
        idx_names (ndarray of ints): indexes to new name order (new_names = names[idx_names])
    """
    curr_names = c["current"]["names"]
    bg_color = c["legend"]["bgcolor"]
    ypos = c["legend"]["ypos"]

    leg = base_legend(ax, curr_names, bg_color, ypos, idx_names)

    # set legend label color & boldness, and handles color&pattern
    patterns = [x * c["pattern"]["density"] for x in c["pattern"]["patterns"]]
    n_colors = c["colormap"]["n_colors"]
    for i_color, (text, handle) in enumerate(zip(leg.texts, leg.legendHandles)):
        text.set_color(cmap((mapper * i_color) % n_colors))
        text.set_weight("bold")

        handle.set_facecolor(cmap((mapper * i_color) % n_colors))
        handle.set_hatch(patterns[((mapper * i_color) // n_colors) % len(patterns)])


def set_legend_with_lines(ax, cmap, mapper, c, idx_names, names, n_colors):
    """Create legend and color each current name, and set handles color and pattern.

    Args:
        ax (matplotlib.axes): currentscape axis
        cmap (matplotlib.colors.Colormap): colormap
        mapper (int): number used to mix color and patterns
        c (dict): config
        idx_names (ndarray of ints): indexes to new name order (new_names = names[idx_names])
        names (list of str): legend labels
        n_colors (int): number of colors (is not always equal to c["colormap"]["n_colors"])
    """
    bg_color = c["legend"]["bgcolor"]
    ypos = c["legend"]["ypos"]

    leg = base_legend(ax, names, bg_color, ypos, idx_names, lines=True)

    # set legend label color & boldness, and handles color&pattern
    ls = c["line"]["styles"]
    lw = c["lw"]
    for i_color, (text, handle) in enumerate(zip(leg.texts, leg.legendHandles)):
        text.set_color(cmap((mapper * i_color) % n_colors))
        text.set_weight("bold")

        handle.set_color(cmap((mapper * i_color) % n_colors))
        handle.set_linestyle(ls[((mapper * i_color) // n_colors) % len(ls)])
        handle.set_linewidth(lw)


def get_handles_with_hatches_and_linestyles(c, cmap, mapper, N_curr):
    """Return handles as a list of tuples (patch, line).

    With patch showing color and hatch and line showing the linestyle.

    Args:
        c (dict): config
        cmap (matplotlib.colors.Colormap): colormap
        mapper (int): number used to mix color and patterns
        N_curr (int): number of currents
    """
    patterns = [x * c["pattern"]["density"] for x in c["pattern"]["patterns"]]
    n_col = c["colormap"]["n_colors"]
    n_pat = len(patterns)
    ls = c["line"]["styles"]
    lw = c["lw"]

    # create a patch (proxy artist) for every current
    return [
        (
            matplotlib.patches.Patch(
                facecolor=cmap((mapper * i) % n_col),
                hatch=patterns[((mapper * i) // n_col) % n_pat],
            ),
            matplotlib.lines.Line2D(
                [],
                [],
                color=cmap((mapper * i) % n_col),
                ls=ls[((mapper * i) // n_col) % len(ls)],
                lw=lw,
            ),
        )
        for i in range(N_curr)
    ]


def set_legend_with_hatches_and_linestyles(ax, cmap, mapper, c, idx_names):
    """Create legend and color each current name, and set handles color and pattern.

    Args:
        ax (matplotlib.axes): currentscape axis
        cmap (matplotlib.colors.Colormap): colormap
        mapper (int): number used to mix color and patterns
        c (dict): config
        idx_names (ndarray of ints): indexes to new name order (new_names = names[idx_names])
    """
    bg_color = c["legend"]["bgcolor"]
    ypos = c["legend"]["ypos"]

    curr_names = c["current"]["names"]
    n_col = c["colormap"]["n_colors"]
    handlelength = c["legend"]["handlelength"]

    handles = get_handles_with_hatches_and_linestyles(c, cmap, mapper, len(idx_names))

    # put those patched as legend-handles into the legend
    leg = ax.legend(
        handles=handles,
        labels=[curr_names[i] for i in idx_names],
        bbox_to_anchor=(1.01, ypos),
        loc=2,
        borderaxespad=0.0,
        facecolor=bg_color,
        edgecolor="black",
        fancybox=False,  # disable round edges
        handler_map={tuple: HandlerTuple(ndivide=None, pad=0.2)},
        handlelength=2 * handlelength,
    )
    leg.get_frame().set_linewidth(0.5)  # set border thickness

    # set legend label color & boldness, and handles color&pattern
    for i_color, text in enumerate(leg.texts):
        text.set_color(cmap((mapper * i_color) % n_col))
        text.set_weight("bold")
