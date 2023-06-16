"""Config-related functions."""

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

# pylint: disable=too-many-statements, too-many-locals
import logging

import json

logger = logging.getLogger(__name__)


def check_config(c):
    """Output a warning if something is wrong with the config.

    Args:
        c (dict): config
    """
    if (
        c["pattern"]["use"]
        and c["show"]["all_currents"]
        and len(c["line"]["styles"]) != len(c["pattern"]["patterns"])
    ):
        logger.warning("line:styles should have as many items as pattern:patterns.")


def replace_defaults(config, new_config):
    """Recursive fct. Replace defaults value with user input.

    Args:
        config (dict): default config
        new_config (dict): dict containing config items to be updated
    """
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
        with open(c, "r", encoding="utf-8") as f:
            c = json.load(f)

    config = {}
    show = {}
    show["currentscape"] = True
    show["ylabels"] = True
    show["yticklabels"] = True
    show["xlabels"] = False
    show["xticklabels"] = False
    show["xgridlines"] = False
    show["legend"] = True
    show["all_currents"] = False
    show["total_contribution"] = False
    config["show"] = show

    current = {}
    # if True, reorder currents with decreasing order of %.
    current["reorder"] = True
    # if True, do not take into account ticks and ylim below.
    current["autoscale_ticks_and_ylim"] = True
    # only taken into account if autoscale_ticks_and_ylim is False
    current["ticks"] = [5, 50, 500]
    # only taken into account if autoscale_ticks_and_ylim is False
    current["ylim"] = (0.01, 1500)
    current["units"] = "[pA]"
    # color for summed currents.
    current["color"] = "black"
    # True to plot absolute currents with stackplots, False to plot them with lines
    current["stackplot"] = False
    current["names"] = None
    # thickness of black line
    # separating the two inward & outward currentscapes / current stackplot.
    # in %age of y size of plot.
    current["black_line_thickness"] = 2
    current["legacy_method"] = False
    config["current"] = current

    currentscape = {}
    currentscape["in_label"] = "inward %"
    currentscape["out_label"] = "outward %"
    # Used with imshow.
    # if too low, white pixels can appear at the bottom of currentscape plots
    # because of rounding errors.
    currentscape["y_resolution"] = 10000
    currentscape["legacy_method"] = False
    config["currentscape"] = currentscape

    ions = {}
    ions["autoscale_ticks_and_ylim"] = True
    ions["ticks"] = [0.0005, 0.05, 5]
    ions["ylim"] = (0.00001, 100)
    ions["units"] = "[mM]"
    ions["reorder"] = True
    ions["names"] = None
    config["ions"] = ions

    colormap = {}
    colormap["name"] = "Set1"
    # color number. Taken into account only if pattern use is True
    colormap["n_colors"] = 8
    config["colormap"] = colormap

    # data along x axis are summed up into chunks when pattern use is True. Put to 1 to disable.
    config["stackplot"] = {"x_chunksize": 50}

    pattern = {}
    pattern["use"] = False
    pattern["patterns"] = ["", "/", "\\", "x", ".", "o", "+"]
    pattern["density"] = 5
    pattern["linewidth"] = 0.2
    # since the pattern color is defined by the edgecolor,
    # this parameter also changes the edgecolor of the pie charts
    pattern["color"] = "black"
    config["pattern"] = pattern

    # is used when pattern:use and show:all_currents are True and current:stackplot is False
    # Should have the same length as pattern:patterns
    line = {
        "styles": [
            "solid",
            (0, (1, 1)),
            (0, (2, 1)),
            (0, (2, 1, 1, 1)),
            (0, (2, 1, 1, 1, 1, 1)),
            (0, (2, 1, 2, 1, 1, 1)),
            (0, (2, 1, 2, 1, 1, 1, 1, 1)),
        ]
    }
    config["line"] = line

    voltage = {}
    voltage["ticks"] = (-50, -20)
    voltage["ylim"] = (-90, 30)
    voltage["units"] = "[mV]"
    voltage["color"] = "black"
    voltage["horizontal_lines"] = True
    config["voltage"] = voltage

    xaxis = {}
    xaxis["units"] = "[ms]"
    # if None, xticks are generated automatically. Can put a list of xticks to force custom xticks.
    xaxis["xticks"] = None
    xaxis["gridline_width"] = 1
    xaxis["gridline_color"] = "black"
    xaxis["gridline_style"] = "--"
    config["xaxis"] = xaxis

    output = {}
    output["savefig"] = False
    output["dir"] = "."
    output["fname"] = "fig"
    output["extension"] = "pdf"
    output["dpi"] = 400
    output["transparent"] = False
    config["output"] = output

    legend = {}
    legend["textsize"] = 4
    legend["bgcolor"] = "lightgrey"
    # 1. : top of legend is at the same level as top of currentscape plot.
    # higher value put legend higher in figure.
    legend["ypos"] = 1.0
    # forced to 0 if pattern:use is False and current:stackplot is False
    legend["handlelength"] = 1.4
    config["legend"] = legend

    adjust_ = {}
    adjust_["left"] = 0.15
    adjust_["right"] = 0.85
    adjust_["top"] = 0.95
    adjust_["bottom"] = 0.0
    config["adjust"] = adjust_

    config["title"] = None
    config["figsize"] = (3, 4)
    config["labelpad"] = 1
    config["textsize"] = 6
    config["titlesize"] = 12
    config["lw"] = 0.5

    new_config = replace_defaults(config, c)

    # for compatibility with older versions
    if "cmap" in new_config["currentscape"]:
        new_config["colormap"]["name"] = new_config["currentscape"]["cmap"]
    if "legendtextsize" in new_config:
        new_config["legend"]["textsize"] = new_config["legendtextsize"]
    if "legendbgcolor" in config:
        new_config["legend"]["bgcolor"] = new_config["legendbgcolor"]
    if "x_chunksize" in new_config["currentscape"]:
        new_config["stackplot"]["x_chunksize"] = new_config["currentscape"][
            "x_chunksize"
        ]
    if "black_line_thickness" in new_config["currentscape"]:
        new_config["current"]["black_line_thickness"] = new_config["currentscape"][
            "black_line_thickness"
        ]
    if "labels" in new_config["show"]:
        new_config["show"]["ylabels"] = new_config["show"]["labels"]
    if "ticklabels" in new_config["show"]:
        new_config["show"]["yticklabels"] = new_config["show"]["ticklabels"]

    check_config(new_config)

    return new_config
