About the config
================

Here is an example of a config file containing all defaults values :

.. code-block:: json

    {
        "show": {
            "currentscape": true,
            "ylabels": true,
            "yticklabels": true,
            "xlabels": false,
            "xticklabels": false,
            "_comment1": "If enabled, xgridlines plot vertical lines in all plots at xticks positions.",
            "xgridlines": false,
            "legend": true,
            "all_currents": false,
            "_comment2": "total contribution plots two pie charts (positive and negative) showing the contribution of each current over the whole simulation.",
            "total_contribution": false
        },
        "current": {
            "_comment1": "is not set by default.  The current names should appear in the same order as in the currents argument. Is mandatory if ['show']['legend'] is true",
            "names": [
                "Na",
                "CaT",
                "CaS",
                "A",
                "KCa",
                "Kd",
                "H",
                "L"
            ],
            "_comment2": "if True, reorder currents with decreasing order of %.",
            "reorder": true,
            "_comment3": "if True, do not take into account ticks and ylim below.",
            "autoscale_ticks_and_ylim": true,
            "_comment4": "only taken into account if autoscale_ticks_and_ylim is False",
            "ticks": [
                5,
                50,
                500
            ],
            "_comment5": "only taken into account if autoscale_ticks_and_ylim is False",
            "ylim": [
                0.01,
                1500
            ],
            "units": "[pA]",
            "_comment6": "color for summed currents.",
            "color": "black",
            "_comment7": "True to plot absolute currents with stackplots, False to plot them with lines",
            "stackplot": false,
            "_comment8": "thickness of black line separating the inward & outward stackplots. in %age of y size of plot.",
            "black_line_thickness": 2,
            "_comment9": "only used if stackplot is True",
            "legacy_method": false
        },
        "currentscape": {
            "in_label": "inward %",
            "out_label": "outward %",
            "_comment1": "only used when legacy_method is true. if too low, white pixels can appear at the bottom of Currentscape plots because of rounding errors. Only used when use_legacy_method is True.",
            "y_resolution": 10000,
            "legacy_method": false
        },
        "ions": {
            "_comment1": "if True, do not take into account ticks and ylim below.",
            "autoscale_ticks_and_ylim": true,
            "_comment2": "only taken into account if autoscale_ticks_and_ylim is False",
            "ticks": [
                0.0005,
                0.05,
                5
            ],
            "_comment3": "only taken into account if autoscale_ticks_and_ylim is False",
            "ylim": [
                0.00001,
                100
            ],
            "units": "[mM]",
            "_comment4": "if True, reorder currents with decreasing order",
            "reorder": true,
            "_comment5": "is not set by default.  The ions concentration names should appear in the same order as in the ions argument. Is mandatory if ['show']['legend'] is true",
            "names": [
                "cai",
                "ki",
                "nai"
            ]
        },
        "colormap": {
            "name": "Set1",
            "_comment1": "color number. Taken into account only if pattern use is True",
            "n_colors": 8
        },
        "stackplot": {
            "_comment1": "only used when ['currentscape']['legacy_method'] is true. data along x axis are summed up into chunks when pattern use is True. Put to 1 to disable.",
            "x_chunksize": 50
        },
        "pattern": {
            "use": false,
            "patterns": ["", "/", "\\", "x", ".", "o", "+"],
            "density": 5,
            "linewidth": 0.2,
            "_comment1": "since the pattern color is defined by the edgecolor, this parameter also changes the edgecolor of the pie charts",
            "color": "black"
        },
        "line": {
            "_comment1": "Is used when ['pattern']['use'] and ['show']['all_currents'] are True and ['current']['stackplot'] is False. Should have the same length as ['pattern']['patterns']",
            "styles": [
                "solid",
                [0, [1, 1]],
                [0, [2, 1]],
                [0, [2, 1, 1, 1]],
                [0, [2, 1, 1, 1, 1, 1]],
                [0, [2, 1, 2, 1, 1, 1]],
                [0, [2, 1, 2, 1, 1, 1, 1, 1]]
            ]
        },
        "voltage": {
            "ylim": [-90, 30],
            "ticks":[-50, -20],
            "units": "[mV]",
            "color": "black",
            "horizontal_lines": true
        },
        "xaxis": {
            "units": "[ms]",
            "_comment1": "if None, xticks are generated automatically. Can put a list of xticks to force custom xticks.",
            "xticks": null,
            "gridline_width": 1,
            "gridline_color": "black",
            "gridline_style": "--"
        },
        "output": {
            "savefig": false,
            "dir": ".",
            "fname": "test_1",
            "extension": "pdf",
            "dpi": 400,
            "transparent": false
        },
        "legend": {
            "textsize": 4,
            "bgcolor": "lightgrey",
            "_comment1": "1. : top of legend is at the same level as top of Currentscape plot. higher value put legend higher in figure.",
            "ypos": 1.0,
            "_comment2": "forced to 0 if ['pattern']['use'] is False and ['current']['stackplot'] is False",
            "handlelength": 1.4
        },
        "figsize": [
            3,
            4
        ],
        "title": null,
        "titlesize": 12,
        "labelpad": 1,
        "textsize": 6,
        "lw": 0.5,
        "adjust": {
            "left": 0.15,
            "right": 0.85,
            "top": 0.95,
            "bottom": 0.0
        }
    }

If you do not want to modify the default values, you should at least specify the current names if you want to plot with the legend.
Your configuration file could be as small as:

.. code-block:: json

    {
        "current": {
            "names": [
                "Na",
                "CaT",
                "CaS",
                "A",
                "KCa",
                "Kd",
                "H",
                "L"
            ],
    }

The config argument can be passed as a dictionnary, or as a path to a json file.
As data can vary greatly, it is recommended to adapt the config file consequently.
One may want to change the y axis limits, or the ticks, for example.
If the legend is cut, one may decrease the legendsize, the adjust right parameter or increase the figsize.


Setting the colormap
====================

Since each color of the colormap applies to one category (one current), using categorical / qualitative colormaps is recommended.
These colormaps have colors chosen to easily distinguish each category.

Also, be careful not to use any colormap that uses white, since white is the default color when there is no data (no inward or outward currents).
It would be then hard to know if there is a 'white' current, or no current at all.
Using a colormap that uses black is also not advised, since the plots on top and bottom of currentscapes, 
as well as the line separating the inward and outward currentscapes, are black. 
If a black current ends up near the top or bottom of the plot, it would decrease readability.

You can set your colormap using :code:`"colormap":{"name": "the_name_of_the_colormap"}` in the config file.
The name of the colormap can be one of the `matplotlib colormaps <https://matplotlib.org/3.1.0/tutorials/colors/colormaps.html>`_, 
or one of the `palettable module <https://jiffyclub.github.io/palettable/>`_.
The palettable colormaps should be inputted in the form :code:`"origin.palette_N"`, N being the number of different colors (i.e. the number of currents if patterns are not used.)

Example: :code:`"cartocolors.qualitative.Safe_8"`


Showing x axis label, ticklabel, gridlines
==========================================

You can use the configuration to show x axis label, ticklabels and vertical gridlines. 
If you choose to display them, the label and ticklabels will only show on the bottom plot, and the vertical gridlines will show on all plots, and correspond to the x ticks (generated automatically, if not set in the config). 
However, to show ticklabels and gridlines, you have to also input time as an argument to the :code:`currentscape.plot` function. Here is an example:

.. code-block:: python

    # load voltage data
    data_dir = "path/to/data/dir"
    v_path = os.path.join(data_dir, "v.dat")
    time = np.loadtxt(v_path)[:, 0]
    voltage = np.loadtxt(v_path)[:, 1]

    currents = load_current_fct(data_dir)
    config = "path/to/config.json"

    # produce Currentscape figure
    fig = currentscape.plot(voltage, currents, config, time=time)

Be aware that the time data are expected to grow monotonically.

Also, when setting custom x ticks through the config, try to stick with ticks within time data limits for optimal display.

Using patterns
==============

If you have a lot of currents to display and do not find a colormap with enough colors to distinguish them all, you can use patterns (also called hatches).
Note: if you are using a lot of currents, you may want to increase the :code:`"legend": {"ypos"}` (e.g. to :code:`1.5`) in your config to have a legend higher in the figure.

By putting :code:`"pattern": {"use": True}` in your config, Currentscape will put patterns like stripes or dots on top of your currents, 
and it will mix colors and patterns so that two successive currents do not have the same pattern or color.
In the :code:`"pattern"` key of your config, you can increase the 'density' (frequency) or your patterns, change the pattern linewidth, color, etc.
You can also change the patterns or the number of different colors to use with the adequate config.

You could also want to use pattern if you are using a non-qualitative colormap that do not have a lot of distinguishable colors.

Showing all absolute currents
=============================

By putting :code:`"show":{"all_currents": True}` in the config file, two subplots showing all the positive and negative currents are added at the bottom of the figure.
The currents can be displayed as stackplots by putting :code:`"current":{"stackplot": True}` in the config, or as lines, by putting :code:`"current":{"stackplot": False}` in the config. In case they are displayed with lines, while using patterns for the current shares, the lines will be displayed with styles (dashed, dotted, etc.). In such a case, the number of line styles should be equal to the number of patterns (which they are, by default). Keep this in mind when changing either the line styles or the patterns.

Using legacy methods
====================

You can use Currentscape legacy methods by setting :code:`"currentscape": {"legacy_method": True}` in the config.
If case you are displaying absolute currents with a stackplot, you can also use its legacy method by setting :code:`"current": {"legacy_method": True}` in the config.
The legacy methods can take longer to compute, take more memory during computation and
the legacy barplot method (used when :code:`"pattern": {"use": True}`, or when both :code:`"current": {"stackplot": True}` and :code:`"show": {"all_currents": True}`) has a bad display when the figure is saved in the pdf format.

However, these methods can be useful to display the main features of the plots, without having the details blurred by e.g. low resolution.


Showing ionic concentrations
============================

You can plot the ionic concentrations in a subplot at the bottom of the figure by passing your ionic concentration data to the main function: :code:`currentscape.plot(voltage, currents, config, ions)`, and by passing the ion names to the config under: :code:`"ions":{"names":your_list}`. Note that, as for the currents, the ion names should correspond to the ion data (i.e. be listed in the same order).

Showing overall contribution pie charts
=======================================

By setting :code:`"show":{"total_contribution": True}` in the configuration, two pie charts are added at the bottom of the figure, each showing the overall contribution of each current over the whole simulation, one for the outward currents, and the other one for the inward currents.

Examples
========

The examples repository contains two examples: one from the original paper from Alsonso and Marder, and one to run a cell, record its currents, and plot them into a Currentscape figure. Remember that these examples need extra dependencies that can be installed with:

.. code-block:: bash

    pip install currentscape[example]


Original paper example
======================

This is a code example from the original paper code, adapted to use this Currentscape module. It generates data, implements the model from the paper, and uses the Currentscape module to make a plot. You can run it with this command after going to :code:`examples/original_paper_plot`:

.. code-block:: bash

    python integrate_single_compartment_and_plot_currentscape.py 

It will produce the Currentscape figure and save it under :code:`examples/original_paper_plot/output/example.png`.


Run cell and plot Currentscape
==============================

You can see an example of how to extract currents and ionic concentractions with bluepyopt and emodelrunner in the example folder: :code:`examples/use_case`.
Please note that you should have `bluepyopt <https://github.com/BlueBrain/BluePyOpt>`_, `emodelrunner <https://github.com/BlueBrain/EModelRunner>`_ and `NEURON <https://neuron.yale.edu/neuron/>`_ installed in order to run the example.
The example folder contains
a cell,
a script to run the cell by applying to it a step stimulus and record its voltage, current and ionic concentration traces,
and another script to plot its Currentscape.

To run the cell, go to :code:`examples/use_case` and do

.. code-block:: bash

    sh run_py.sh

It should record the currents under the :code:`python_recordings` folder. Once this is done, you can plot the Currentscape by doing:

.. code-block:: bash

    python plot.py

It should open a matplotlib window with the Currentscape figure.
You can adjust the Currentscape plot by modifying the configuration that is hard-coded in :code:`plot.py`.


Known caveats
=============

Since Currentscape can deal with a lot of data, it sometimes crashes with an error message such as :code:`Bus error` or :code:`Killed` when it runs out of memory. You can solve this error by allocating more memory. Note that this error is prone to happen more frequently when legacy methods are used.
