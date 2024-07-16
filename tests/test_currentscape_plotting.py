"""Test currentscape plotting functions."""

from logging import WARNING
import os

import matplotlib

matplotlib.use("agg")  # to avoid tkinter error
import matplotlib.pyplot as plt
import numpy as np
from pytest import LogCaptureFixture

from currentscape.ions import IonConcentrations
from currentscape.plotting import (
    configure_mpl_rcParams,
    get_rows_tot,
    get_colors,
    get_colormap,
    select_color,
    get_colors_hatches_lines_lists,
    save_figure,
)


def test_configure_mpl_rcParams():
    """Test configure_mpl_rcParams function."""
    config = {
        "textsize": 6,
        "legend": {"textsize": 4, "handlelength": 1.4},
        "pattern": {"use": False, "linewidth": 0.2},
    }

    configure_mpl_rcParams(config)
    assert plt.rcParams["axes.labelsize"] == 6
    assert plt.rcParams["xtick.labelsize"] == 6
    assert plt.rcParams["ytick.labelsize"] == 6
    assert plt.rcParams["legend.fontsize"] == 4
    assert plt.rcParams["legend.handletextpad"] == 0
    assert plt.rcParams["legend.labelspacing"] == 0
    assert plt.rcParams["legend.handlelength"] == 0

    config["pattern"]["use"] = True
    configure_mpl_rcParams(config)
    assert plt.rcParams["axes.labelsize"] == 6
    assert plt.rcParams["xtick.labelsize"] == 6
    assert plt.rcParams["ytick.labelsize"] == 6
    assert plt.rcParams["legend.fontsize"] == 4
    assert plt.rcParams["hatch.linewidth"] == 0.2
    assert plt.rcParams["legend.handlelength"] == 1.4


def test_get_rows_tot():
    """Test get_rows_tot function."""
    config = {
        "pattern": {"use": False, "patterns": []},
        "show": {"all_currents": False, "total_contribution": False},
        "ions": {"reorder": False, "names": None},
        "xaxis": {"xticks": None},
        "currentscape": {"legacy_method": True},
    }
    ions = IonConcentrations(None, config)

    rows = get_rows_tot(config, ions)
    assert rows == 7

    config["pattern"]["use"] = True
    rows = get_rows_tot(config, ions)
    assert rows == 8

    config["pattern"]["use"] = False
    config["currentscape"]["legacy_method"] = False
    rows = get_rows_tot(config, ions)
    assert rows == 8

    config["pattern"]["use"] = False
    config["show"]["all_currents"] = True
    rows = get_rows_tot(config, ions)
    assert rows == 10

    config["show"]["all_currents"] = False
    config["show"]["total_contribution"] = True
    rows = get_rows_tot(config, ions)
    assert rows == 10

    config["show"]["total_contribution"] = False
    ions.data = np.asarray([[1, 2], [3, 4]])
    rows = get_rows_tot(config, ions)
    assert rows == 9

    config["pattern"]["use"] = True
    config["show"]["all_currents"] = True
    config["show"]["total_contribution"] = True
    rows = get_rows_tot(config, ions)
    assert rows == 13


def test_get_colors():
    """Test get_colors function.

    Check that matplotlib and palettable cmap are acepted.
    Check the bool indicating a number of colors too big.
    """
    # matplotlib, enough colors
    l, cmap_too_small = get_colors("Set1", 8)
    assert not cmap_too_small
    assert len(l) == len(set(tuple(item) for item in l))  # no duplicates

    # matplotlib, not enough colors
    l, cmap_too_small = get_colors("Set1", 30)
    assert cmap_too_small
    assert len(l) > len(set(tuple(item) for item in l))  # no duplicates

    # palettable, enough colors
    _, cmap_too_small = get_colors("cartocolors.qualitative.Antique_8", 8)
    assert not cmap_too_small

    # palettable, not enough colors
    _, cmap_too_small = get_colors("cartocolors.qualitative.Antique_8", 9)
    assert cmap_too_small


def test_get_colormap(caplog: LogCaptureFixture):
    """Test get_colormap function.

    Check that black and white colors are present at the end of colormap.
    Check that warnings are launched.
    """
    cmap = get_colormap(
        cmap="Set1", n_colors=6, use_patterns=False, N_curr=6, N_ion=None
    )
    assert len(cmap.colors) == 8
    assert np.array_equal(cmap.colors[-2], [0, 0, 0, 1])
    assert np.array_equal(cmap.colors[-1], [1, 1, 1, 1])

    caplog.set_level(WARNING)
    get_colormap(cmap="Set1", n_colors=6, use_patterns=False, N_curr=30, N_ion=None)
    assert (
        "currentscape.plotting",
        WARNING,
        "The number of colors in the colormap "
        "is smaller than the number of currents. "
        "Please, choose a colormap with more colors "
        "or use patterns for optimal display.",
    ) in caplog.record_tuples

    get_colormap(cmap="Set1", n_colors=25, use_patterns=True, N_curr=30, N_ion=None)
    assert (
        "currentscape.plotting",
        WARNING,
        "'n_colors' in 'colormap' in config is larger than "
        "the number of colors in the colormap. "
        "Please, choose a colormap with more colors "
        "or decrease n_colors for optimal display.",
    ) in caplog.record_tuples


def test_select_color():
    """Test select_color function."""
    # colormap with 2 colors + black + white
    cmap = get_colormap(
        cmap="Set1", n_colors=None, use_patterns=False, N_curr=2, N_ion=None
    )
    assert len(cmap.colors) == 4

    # assert the two colors are different
    assert select_color(cmap, 0, 2) != select_color(cmap, 1, 2)
    # assert 3rd is black
    assert np.array_equal(select_color(cmap, 2, 2), (0, 0, 0, 1))
    # assert 4th is white
    assert np.array_equal(select_color(cmap, 3, 2), (1, 1, 1, 1))


def to_tuple(lst):
    return tuple(to_tuple(i) if isinstance(i, list) else i for i in lst)


def test_get_colors_hatches_lines_lists():
    """Test get_colors_and_hatches_lists function."""
    linestyles = [
        "solid",
        [0, [1, 1]],
        [0, [2, 1]],
        [0, [2, 1, 1, 1]],
        [0, [2, 1, 1, 1, 1, 1]],
        [0, [2, 1, 2, 1, 1, 1]],
        [0, [2, 1, 2, 1, 1, 1, 1, 1]],
    ]
    # do not use pattern case
    config = {"pattern": {"use": False}}
    curr_idxs = np.arange(4)
    cmap = get_colormap(
        cmap="Set1", n_colors=None, use_patterns=False, N_curr=4, N_ion=None
    )
    colors, hatches, lines = get_colors_hatches_lines_lists(
        config, curr_idxs, cmap, mapper=None
    )
    assert len(colors) == 4
    assert hatches is None
    assert np.array_equal(lines, np.full(4, "solid"))

    # use pattern case
    config = {
        "pattern": {
            "use": True,
            "density": 5,
            "patterns": ["", "/", "\\", "x", ".", "o", "+"],
        },
        "colormap": {"n_colors": 4},
        "line": {"styles": linestyles},
    }
    cmap = get_colormap(
        cmap="Set1", n_colors=4, use_patterns=True, N_curr=4, N_ion=None
    )
    colors, hatches, lines = get_colors_hatches_lines_lists(
        config, curr_idxs, cmap, mapper=9
    )
    assert len(colors) == 4
    assert len(hatches) == 4
    assert len(lines) == 4
    # no repetition because N_curr <= n_colors, and N_curr <= len(patterns)
    assert len(colors) == len(set(tuple(color) for color in colors))
    assert len(hatches) == len(set(tuple(hatch) for hatch in hatches))
    assert len(lines) == len(set(to_tuple(lines)))

    # now with n_curr > n_colors, n_currs > len(patterns)
    cmap = get_colormap(
        cmap="Set1", n_colors=4, use_patterns=True, N_curr=20, N_ion=None
    )
    curr_idxs = np.arange(20)
    colors, hatches, lines = get_colors_hatches_lines_lists(
        config, curr_idxs, cmap, mapper=9
    )
    assert len(colors) == 20
    assert len(hatches) == 20
    assert len(lines) == 20

    # colors and hatches get combined with (colors[i], hatches[i])
    # all combinations should be unique
    combinations = []
    for col, hatch in zip(colors, hatches):
        combinations.append((tuple(col), hatch))
    assert len(combinations) == len(set(combinations)) == 20
    combinations = []
    for col, line in zip(colors, lines):
        combinations.append((tuple(col), to_tuple(line)))
    assert len(combinations) == len(set(combinations)) == 20


def test_save_figure():
    """Test save_figure function."""
    fpath = "tests/output/test_savefig.png"
    config = {
        "output": {
            "dir": "tests/output",
            "fname": "test_savefig",
            "extension": "png",
            "dpi": 100,
            "transparent": False,
        }
    }

    fig = plt.figure()
    save_figure(fig, config)
    assert os.path.isfile(fpath)
