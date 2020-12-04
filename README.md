This package contain code based on [Leandro M. Alonso and Eve Marder, ”Visualization of the relative contributions of conductances in neuronal models with similar behavior and different conductance densities” (2018)](https://datadryad.org/stash/dataset/doi:10.5061/dryad.d0779mb).
The code in this package is able to reproduce the currentscape figure in the susmentioned article, including the labels, ticks and legend.


### Loading currentscape in Python

After installing currentscape, your PYTHONPATH environment variable should normally
contain the directory where the currentscape module is installed. Loading currentscape
in Python becomes then as easy as:

    import currentscape

### Plotting your first currentscape

Given voltage and current data (see 'Extracting currents' section below for how to get voltage and currents from a cell), as well as an adequate config json file, producing a currenscape figure should be as simple as

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


### Extracting currents

You can now use the currentscape module to easily extract currents at different locations with custom protocols.
This should be as simple as:

    from extract_currs.main_func import extract
    extract("extraction_config_filename")

Where you have a config file (not the same as for the ploting module) in a json format. The config file can also be passed as a dictionary.
The segment area from neuron is used in the module to output the currents (and not the current densities).

#### The config file for extractng currents

Below is an example of a config file used to extract currents.

    {
        "emodel": "bNAC_L23SBC",
        "output_dir": "output",
        "join_emodel_to_output_dir_name": true,
        "use_recipes": false,
        "recipe_dir": "/gpfs/bbp.cscs.ch/home/ajaquier/Eve-Marder-style-module/output/config/recipes",
        "recipe_filename": "recipes.json",
        "morph_name": "_",
        "morph_filename": "C230998A-I3_-_Scale_x1.000_y0.975_z1.000_-_Clone_2.asc",
        "apical_point_isec": null,
        "morph_dir": "/gpfs/bbp.cscs.ch/home/ajaquier/Eve-Marder-style-module/output/memodel_dirs/L23_BP/bNAC/L23_BP_bNAC_150/morphology",
        "params_dir": "/gpfs/bbp.cscs.ch/home/ajaquier/Eve-Marder-style-module/output/config/params",
        "params_filename": "int.json",
        "final_params_dir": "/gpfs/bbp.cscs.ch/home/ajaquier/Eve-Marder-style-module/output/config/params",
        "final_params_filename": "final.json",
        "var_list": [
            "v",
            "ihcn_Ih",
            "ica_Ca_HVA",
            "ica_Ca_HVA2",
            "ica_Ca_LVAst",
            "ik_K_Pst",
            "ik_K_Tst",
            "ik_KdShu2007",
            "ina_Nap_Et2",
            "ina_NaTg",
            "ina_NaTg2",
            "ik_SK_E2",
            "ik_SKv3_1",
            "ik_StochKv2",
            "ik_StochKv3",
            "i_pas"
        ],
        "etypetest": "",
        "protocols_dir": ".",
        "protocols_filename": "protocol_test.json",
        "features_dir": "/gpfs/bbp.cscs.ch/home/ajaquier/Eve-Marder-style-module/output/config/features",
        "features_filename": "bNAC.json"
    }

The following keys are mandatory: emodel, output_dir, var_list, use_recipes.
Protocols can now record in multiple places in the neuron, the available variables on those places can differ. So now, if a current that is in the var_list is not present in the recording location, the script does not crash, and the variable is simply ignored for this location.

The extract currents module has two main modes: using recipes, or using custom protocols and parameters.

###### recipe mode

When you set use_recipes to true, the script will retrieve the default protocols, features and parameters in the recipes file.
When use_recipes is set to true, recipe_dir, recipe_filename and etypetest should also be present in the config file. 
If etypetest is not an empty string, the script will retrieve the apical point section index from recipes. 
Depending on the emodel, you might have an error if you set use_recipes to true, but leave etypetest to an empty string.
When use_recipes, the recipe file expects that you have the following folder structure in the directory you launched the script from:

./
    config/
        features/
        params/
        protocols/

with a config folder filled as in /gpfs/bbp.cscs.ch/project/proj38/singlecell/optimization/config/ . You can also find there the recipes file.

###### custom mode

When use_recipes is set to false, the following keys should be filled in the config:

morph_name, morph_filename, morph_dir, apical_point_isec, params_dir, params_filename, final_params_dir (usually the same as params_dir), final_params_filename (usually final.json), protocols_dir, protocols_filename, features_dir, features_filename

with protocols_dir and protocols_filename pointing to your cutomized protocols file. If there is no "Main" key in your protocols file, features are not used and features_dir and features_filename can both be set to an empty string (""). morph_name is used solely for the naming of the output files.

Your protocols file should follow the same structure as in /gpfs/bbp.cscs.ch/project/proj38/singlecell/optimization/config/protocols/ .
Note that all protocols are recorded in the soma by default, but you can add recording locations using the extra_recordings key.

Below is an example of a simple custom protocol, recording a step protocol in the soma and in the ais.

    {
        "test": {
            "type": "StepProtocol",
            "stimuli": {
                "step": {
                    "delay": 700.0,
                    "amp": 0.063014185402,
                    "duration": 2000.0,
                    "totduration": 3000.0
                },
                "holding": {
                    "delay": 0.0,
                    "amp": -0.0144071499339,
                    "duration": 3000.0,
                    "totduration": 3000.0
                }
            },
            "extra_recordings": [
                {
                    "comp_x": 0.5,
                    "type": "nrnseclistcomp",
                    "name": "ais",
                    "seclist_name": "axon",
                    "sec_index": 0
                }
            ]
        }
    }

Note that if you want to use a "StepThresholdProtocol", you should follow the same procedure as in a protocol from /gpfs/bbp.cscs.ch/project/proj38/singlecell/optimization/config/protocols/ with a "Main" protocol calling the others, in order to collect threshold data needed for the Step Threshold Protocol.