"""Module to plot currentscapes.

As in https://datadryad.org/stash/dataset/doi:10.5061/dryad.d0779mb.
The main function is based on scripts from the susmentioned article,
that are under the CC0 1.0 Universal (CC0 1.0) Public Domain Dedication license.
"""

# pylint: disable=too-many-statements, wrong-import-position
import numpy as np
import matplotlib

matplotlib.use("agg")  # to avoid tkinter error
import matplotlib.pyplot as plt

from currentscape.data_processing import (
    autoscale_ticks_and_ylim,
)
from currentscape.plotting import (
    get_colormap,
    adjust,
    save_figure,
)
from currentscape.subplots import (
    plot_voltage_trace,
)
from currentscape.currents import Currents
from currentscape.ions import IonConcentrations
from currentscape.config_parser import set_default_config


def create_figure(voltage, currs, c, ions):
    """Create the currentscape figure.

    Args:
        voltage (list of floats): voltage data
        currs (Currents): object containing currents data
        c (dict): config
        ions (IonConcentrations): object containing ionic concentration data
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

    cmap = get_colormap(
        c["colormap"]["name"], c["colormap"]["n_colors"], use_patterns, currs.N
    )

    # get adequate ticks and ylim
    # put into classes
    if c["current"]["autoscale_ticks_and_ylim"]:
        autoscale_ticks_and_ylim(c, currs.pos_sum, currs.neg_sum)
    if ions.data is not None and c["ions"]["autoscale_ticks_and_ylim"]:
        autoscale_ticks_and_ylim(c, np.max(ions.data), abs(np.min(ions.data)), "ions")

    rows_tot = 7
    if use_patterns:
        rows_tot += 1
    if c["show"]["all_currents"]:
        rows_tot += 2
    if ions.data is not None:
        rows_tot += 1
    row = 0

    # START PLOT
    fig = plt.figure(figsize=c["figsize"])
    if c["title"]:
        fig.suptitle(c["title"], fontsize=c["titlesize"])

    # PLOT VOLTAGE TRACE
    plot_voltage_trace(c, voltage, row, rows_tot)
    row += 2

    # PLOT TOTAL INWARD CURRENT IN LOG SCALE
    currs.plot_sum(c, row, rows_tot, True)
    row += 1

    # PLOT CURRENT SHARES
    if use_patterns:
        # mapper = create_mapper(c["colormap"]["n_colors"], len(c["pattern"]["patterns"]))
        currs.plot_shares_with_bars(c, row, rows_tot, cmap)
        row += 4
    else:
        # mapper = None
        currs.plot_shares_with_imshow(c, row, rows_tot, cmap)
        row += 3

    # PLOT TOTAL OUTWARD CURRENT IN LOG SCALE
    currs.plot_sum(c, row, rows_tot, False)
    row += 1

    # PLOT ALL CURRENTS
    if c["show"]["all_currents"]:
        # plot all positive currents
        currs.plot(c, row, rows_tot, cmap, True)
        row += 1
        # plot all negative currents
        currs.plot(c, row, rows_tot, cmap, False)
        row += 1

    # PLOT IONIC CONCENTRATION
    if ions.data is not None:
        ions.plot(c, row, rows_tot, cmap)
        row += 1

    adjust(
        c["adjust"]["left"],
        c["adjust"]["right"],
        c["adjust"]["top"],
        c["adjust"]["bottom"],
    )

    return fig


def plot_currentscape(voltage, currents_data, config, ions_data=None):
    """Returns a figure containing current scapes.

    Args:
        voltage (list): voltage data
        currents_data (list of lists): currents data
        config (dict or str): dict or path to json file containing config
        ions_data (list of lists): ion concentrations data
    """
    # load config and set default to unspecified terms
    c = set_default_config(config)

    # currenscape data processing
    print("processing data")

    currs = Currents(currents_data, c)
    ions = IonConcentrations(ions_data, c["ions"]["names"], c["ions"]["reorder"])

    # plot currentscape
    print("producing figure")
    fig = create_figure(voltage, currs, c, ions)

    if c["output"]["savefig"]:
        save_figure(fig, c)

    return fig
