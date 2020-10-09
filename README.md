This package contain code based on [Leandro M. Alonso and Eve Marder, ”Visualization of the relative contributions of conductances in neuronal models with similar behavior and different conductance densities” (2018)](https://datadryad.org/stash/dataset/doi:10.5061/dryad.d0779mb).
The code in this package is able to reproduce the currentscape figure in the susmentioned article, including the labels, ticks and legend.

Given voltage and current data, as well as an adequate config json file, producing a currenscape figure should be as simple as

    from currentscape import plotCurrentscape

    ... loading voltage, current and config here

    fig = plotCurrentscape(voltage, currents, config)

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
            # is set automatically, but can be force to given values here
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
        "legendsize": 6,
        "titlesize": 12,
        "adjust": {
            "left": null,
            "right": 0.85,
            "top": null,
            "bottom": null
        }
    }

The config argument can be passed as a dictionnary, or as a path to a json file.

As data can vary greatly, it is recommended to adapt the config file consequently.

One may want to change the y axis limits, or the ticks, for example.

If the legend is cut, one may decrease the legendsize, the adjust right parameter or to increase the figsize.


