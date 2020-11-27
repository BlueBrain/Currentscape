This package contain code based on [Leandro M. Alonso and Eve Marder, ”Visualization of the relative contributions of conductances in neuronal models with similar behavior and different conductance densities” (2018)](https://datadryad.org/stash/dataset/doi:10.5061/dryad.d0779mb).
The code in this package is able to reproduce the currentscape figure in the susmentioned article, including the labels, ticks and legend.


### Loading currentscape in Python

After installing currentscape, your PYTHONPATH environment variable should normally
contain the directory where the currentscape module is installed. Loading currentscape
in Python becomes then as easy as:

    import currentscape

### Plotting your first currentscape

Given voltage and current data, as well as an adequate config json file, producing a currenscape figure should be as simple as

    import os
    import numpy as np
    from currentscape.currentscape import plot_currentscape

    data_dir = "/gpfs/bbp.cscs.ch/home/ajaquier/Eve-Marder-style-module/output/memodel_dirs/L23_BP/bNAC/L23_BP_bNAC_150/python_recordings"
    currs = [
        "ihcn_Ih",
        "ica_Ca_HVA2",
        "ica_Ca_LVAst",
        "ik_SK_E2",
        "ik_SKv3_1",
        "ik_K_Pst",
        "ik_K_Tst",
        "ina_NaTg",
    ]

    # load voltage data
    v_path = os.path.join(data_dir, "_".join(("soma_step1", "v")) + ".dat")
    voltage = np.loadtxt(v_path)[:, 1] # load 2nd column. 1st column is time.

    # load currents from files
    currents = []
    for curr in currs:
        file_path = os.path.join(data_dir, "_".join(("soma_step1", curr)) + ".dat")
        currents.append(np.loadtxt(file_path)[:, 1]) # load 2nd column. 1st column is time.
    currents = np.array(currents)

    # define config
    config = "path/to/config"
    # can also pass config as a dictionnary, as commented below
    # curr_names = ["Ih", "Ca_HVA2", "Ca_LVAst", "SK_E2", "SKv3_1", "K_Pst", "K_Tst", "NaTg"]
    # config = {
    #     "current": {"names": curr_names},
    #     "legendtextsize": 5,
    # }

    # produce currentscape figure
    fig = plot_currentscape(voltage, currents, config)
    fig.show()

The voltage should be a list of floats corresponding to the voltage at each timestep.

The currents should be a list of lists of floats corresponding to each current at each timestep.

Each current list and the voltage list should have the same size.


### About the config


Here is an example of a config file containing all defaults values :

    {
        "show": {
            "labels": true,
            "ticklabels": true,
            "legend": true
        },
        "current": {
            "_comment1": "is not set by default.  The current names should appear in the same order as in the currents argument. is mandatory if ['show']['legend'] is true",
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
            "ticks": [
                5,
                50,
                500
            ],
            "ylim": [
                0.01,
                1500
            ],
            "units": "[pA]",
            "color": "black"
        },
        "currentscape": {
            "in_label": "inward %",
            "out_label": "outward %",
            "_comment1": "if too low, white pixels can appear at the bottom of currentscape plots because of rounding errors.",
            "y_resolution": 10000,
            "_comment2": "thickness of black line separating the two inward & outward currentscapes. in %age of y size of plot.",
            "black_line_thickness": 2,
            "_comment3": "data along x axis are summed up into chunks when pattern use is True. Put to 1 to disable.",
            "x_chunksize": 50
        },
        "colormap": {
            "name": "Set1",
            "_comment1": "color number. Taken into account only if pattern use is True",
            "n_colors": 8
        },
        "pattern": {
            "use": false,
            "patterns": ["", "/", "\\", "x", ".", "o", "+"],
            "density": 5,
            "linewidth": 0.2,
            "color": "black"
        },
        "voltage": {
            "ylim": [-90, 30],
            "ticks":[-50, -20],
            "units": "[mV]",
            "color": "black",
            "horizontal_lines": true
        },
        "output": {
            "savefig": false,
            "dir": ".",
            "fname": "test_1",
            "extension": "png",
            "dpi": 400,
            "transparent": false
        },
        "legend": {
            "textsize": 6,
            "bgcolor": "lightgrey",
            "_comment1": "1. : top of legend is at the same level as top of currentscape plot. higher value put legend higher in figure.",
            "ypos": 1.0,
            "_comment2": "forced to 0 if pattern use is False",
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
        "adjust": {
            "left": null,
            "right": 0.85,
            "top": null,
            "bottom": null
        }
    }

If you do not want to modify the default values, you should at least specify the current names if you want to plot with the legend.
Your configuration file could be as small as:

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


### Setting the colormap

Since each color of the colormap applies to one category (one current), using categorical / qualitative colormaps is recommended.
These colormaps have colors chosen to easily distinguish each category.

Also, be careful not to use any colormap that uses white, since white is the default color when there is no data (no inward or outward currents).
It would be then hard to know if there is a "white" current, or no current at all.
Using a colormap that uses black is also not advised, since the plots on top and bottom of currentscapes, 
as well as the line separating the inward and outward currentscapes, are black. 
If a black current end up near the top or bottom of the plot, it would decrease readability.

You can set your colormap using "colormap":{"name": "the_name_of_the_colormap"} in the config file.
The name of the colormap can be one of the matplotlib colormaps (https://matplotlib.org/3.1.0/tutorials/colors/colormaps.html), 
or one of the palettable module (https://jiffyclub.github.io/palettable/).
The palettable colormaps should be inputted in the form "origin.palette_N", N being the number of different colors (i.e. the number of currents if patterns are not used.)
Example:
    "cartocolors.qualitative.Safe_8"


### Using patterns

If you have a lot of currents to display and do not find a colormap with enough colors to distinguish them all, you can use patterns (also called hatches).
Note: if you are using a lot of currents, you may want to increase the "legend":"ypos" (e.g. to 1.5) in your config to have a legend higher in the figure.

By putting "pattern": {"use": True} in your config, currentscape will put patterns like stripes or dots on top of your currents, 
and it will mix colors and patterns so that two successive currents do not have the same pattern or color.
In the "pattern" key of your config, you can increase the 'density' (frequency) or your patterns, the pattern linewidth, color, etc.
You can also change the patterns or the number of different colors to use with the adequate config.

However, using patterns come with a cost: it takes more computing time (mainly because bar plots are used instead of imshow).
To decrease computing time, you have two possibilities: decrease the pattern density (default=5), or increase x_chunksize.
x_chunksize is related to the x resolution, with x_chunksize = 1 being maximum resolution. The default is x_chunksize=50.

You could also want to use pattern if you are using a non-qualitative colormap that do not have a lot of distinguishable colors.



