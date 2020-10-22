********
Tutorial
********

Loading currentscape in Python
==============================

After installing currentscape, your PYTHONPATH environment variable should normally
contain the directory where the currentscape module is installed. Loading currentscape
in Python becomes then as easy as:

.. code-block:: python

        import currentscape

Plotting your first currentscape
================================

In this example, we will need the module os (comes with python),
numpy (has been loaded with currentscape) and plot_currentscape, 
the main function from currentscape. In theory, plot_currentscape
is the only function you will need to load from the currentscape module.

.. code-block:: python

        import os
        import numpy as np
        from currentscape.currentscape import plot_currentscape

Then, you can load your data. You must select voltage and currents data.
The voltage data should be a list, and the currents data should be a list
containing one list for each current. Each voltage and current list should have the same size.
You can access the dataset in the example
below if you are on gpfs.

.. code-block:: python

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

        # load currents data
        currents = []
        for curr in currs:
            file_path = os.path.join(data_dir, "_".join(("soma_step1", curr)) + ".dat")
            currents.append(np.loadtxt(file_path)[:, 1]) # load 2nd column. 1st column is time.
        currents = np.array(currents)

Next, you need to load a configuration. The configuration can be provided as a json file:

.. code-block:: python

        config = "path/to/config"

Or as a dictionnary. The following dictionnary can be used for the example.

.. code-block:: python

        curr_names = ["Ih", "Ca_HVA2", "Ca_LVAst", "SK_E2", "SKv3_1", "K_Pst", "K_Tst", "NaTg"]
        config = {
            "current": {"names": curr_names},
            "legendtextsize": 5,
        }

More details on config dictionnary below.
Finally, call the plot_currentscape function
with voltage, currents and config as arguments, 
and show the figure:

.. code-block:: python

        fig = plot_currentscape(voltage, currents, config)
        fig.show()


About the config
================

The config file should be a json file containing a dictionnary.
Each value in the dictionnary can replace a default parameter of the plot.
Below is a complete dictionnary showing every default value that you can replace
(except "current":"names" that is not set by default but shown below anyway).
Each parameter name is self-explanatory.

.. code-block:: JSON

        {
            "show": {
                "labels": true,
                "ticklabels": true,
                "legend": true
            },
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

.. code-block:: JSON

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


As data can vary greatly, it is recommended to adapt the config file consequently.
One may want to change the y axis limits, or the ticks, for example.
If the legend is cut, one may decrease the legendsize, the adjust right parameter or to increase the figsize.
