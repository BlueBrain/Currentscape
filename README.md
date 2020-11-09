This package contain code based on [Leandro M. Alonso and Eve Marder, ”Visualization of the relative contributions of conductances in neuronal models with similar behavior and different conductance densities” (2018)](https://datadryad.org/stash/dataset/doi:10.5061/dryad.d0779mb).
The code in this package is able to reproduce the currentscape figure in the susmentioned article, including the labels, ticks and legend.

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

Here is an example of a config file containing all defaults values :

    {
        "show": {
            "labels": true,
            "ticklabels": true,
            "legend": true
        },
        "current": {
            # is not set by default. 
            # The current names should appear in the same order as in the currents argument.
            # is mandatory if ["show"]["legend"] is true
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
            # colormap
            "cmap": "Set1"
        },
        "voltage": {
            "ylim": [
                -90,
                30
            ],
            "ticks":[],
            "units": "[mV]",
            "color": "black"
        },
        "output": {
            "savefig": false,
            "dir": ".",
            "fname": "test_1",
            "extension": "png",
            "dpi": 400,
            "transparent": false
        },
        "figsize": [
            3,
            4
        ],
        "title": "",
        "labelpad": 1,
        "textsize": 6,
        "legendtextsize": 6,
        "legendbgcolor": "lightgrey",
        "titlesize": 12,
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


