"""Module to plot currentscapes.

As in https://datadryad.org/stash/dataset/doi:10.5061/dryad.d0779mb.
The main function is based on scripts from the susmentioned article,
that are under the CC0 1.0 Universal (CC0 1.0) Public Domain Dedication license.
"""

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

# pylint: disable=too-many-statements, wrong-import-position
import logging
import numpy as np
import matplotlib

matplotlib.use("agg")  # to avoid tkinter error
import matplotlib.pyplot as plt

from currentscape.data_processing import (
    autoscale_ticks_and_ylim,
)
from currentscape.plotting import (
    configure_mpl_rcParams,
    get_colormap,
    adjust,
    save_figure,
    get_rows_tot,
    plot_x_labels,
)
from currentscape.voltages import Voltages
from currentscape.currents import Currents
from currentscape.ions import IonConcentrations
from currentscape.config_parser import set_default_config

logger = logging.getLogger(__name__)


def create_figure(voltage, currs, c, ions):
    """Create the currentscape figure.

    Args:
        voltage (list of floats): voltage data
        currs (Currents): object containing currents data
        c (dict): config
        ions (IonConcentrations): object containing ionic concentration data
    """
    configure_mpl_rcParams(c)
    use_patterns = c["pattern"]["use"]

    cmap = get_colormap(
        c["colormap"]["name"], c["colormap"]["n_colors"], use_patterns, currs.N, ions.N
    )

    # get adequate ticks and ylim
    # put into classes
    if c["current"]["autoscale_ticks_and_ylim"]:
        autoscale_ticks_and_ylim(c, currs.pos_sum, currs.neg_sum)
    if (
        ions.data is not None
        and ions.data.size
        and c["ions"]["autoscale_ticks_and_ylim"]
    ):
        autoscale_ticks_and_ylim(c, np.max(ions.data), abs(np.min(ions.data)), "ions")

    rows_tot = get_rows_tot(c, ions)
    row = 0

    # START PLOT
    fig = plt.figure(figsize=c["figsize"])
    if c["title"]:
        fig.suptitle(c["title"], fontsize=c["titlesize"])

    # PLOT OVERALL CONTRIBUTIONS
    # plot this first.
    # cannot be at the bottom, because it would plot on top of xlabels if enabled.
    if c["show"]["total_contribution"]:
        currs.plot_overall_contributions(c, row, rows_tot, cmap)
        row += 2

    # PLOT VOLTAGE TRACE
    voltage.plot(c, row, rows_tot)
    row += 2

    # PLOT TOTAL OUTWARD CURRENT IN LOG SCALE
    currs.plot_sum(c, row, rows_tot, True)
    row += 1

    # PLOT CURRENT SHARES
    if (
        c["show"]["currentscape"]
        and c["currentscape"]["legacy_method"]
        and not use_patterns
    ):
        currs.plot_shares_with_imshow(c, row, rows_tot, cmap)
        row += 3
    elif c["show"]["currentscape"]:
        currs.plot_shares(c, row, rows_tot, cmap)
        row += 4

    # PLOT TOTAL INWARD CURRENT IN LOG SCALE
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

    # PLOT IONIC CONCENTRATIONS
    if ions.data is not None and ions.data.size:
        if use_patterns:
            ions.plot_with_linestyles(c, row, rows_tot, cmap)
        else:
            ions.plot(c, row, rows_tot, cmap)
        row += 1

    # ADD X LABEL & X TICK LABELS
    # add labels only on bottom subplot
    # time is identical for every dataset here, so currs can be used, even for ions xticks.
    plot_x_labels(fig.axes[-1], c, currs.xticks)

    adjust(
        c["adjust"]["left"],
        c["adjust"]["right"],
        c["adjust"]["top"],
        c["adjust"]["bottom"],
    )

    return fig


def plot_currentscape(voltage_data, currents_data, config, ions_data=None, time=None):
    """Returns a figure containing current scapes.

    Args:
        voltage_data (list): voltage data
        currents_data (list of lists): currents data
        config (dict or str): dict or path to json file containing config
        ions_data (list of lists): ion concentrations data
        time (list): time data
    """
    # load config and set default to unspecified terms
    c = set_default_config(config)

    # currenscape data processing
    logger.info("processing data")

    voltage = Voltages(voltage_data, c, time)
    currs = Currents(currents_data, c, time)
    ions = IonConcentrations(ions_data, c, time)

    # plot currentscape
    logger.info("producing figure")
    fig = create_figure(voltage, currs, c, ions)

    # saving matplotlib figure needs a lot of memory
    # so delete data that will not be used anymore before
    currs = None
    voltage = None
    ions = None

    if c["output"]["savefig"]:
        save_figure(fig, c)

    return fig
