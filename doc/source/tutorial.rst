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
numpy and plot_currentscape, 
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
If the legend is cut, one may decrease the legendsize, the adjust right parameter or increase the figsize.

Producing the voltage and currents data
=======================================

You may wonder how to produce the data needed by currentscape.
Below is an example script of how to extract these data using bluepyopt and neurom.
Bluepyopt runs the cell and records the voltage and current densities.
Neurom computes the soma area.
Then, the current data can be collected by multiplying the current densities by the soma area.

.. code-block:: python

        """Extract voltage and currents recordings."""

        import argparse
        import collections
        import logging
        import numpy as np
        import os

        import json
        import bluepyopt.ephys as ephys
        import neurom as nm

        logger = logging.getLogger(__name__)


        class RecordingCustom(ephys.recordings.CompRecording):
            """Response to stimulus with recording every 0.1 ms."""

            def __init__(self, name=None, location=None, variable="v"):
                """Constructor.

                Args:
                    name (str): name of this object
                    location (Location): location in the model of the recording
                    variable (str): which variable to record from (e.g. 'v')
                """
                super(RecordingCustom, self).__init__(
                    name=name, location=location, variable=variable
                )

            def instantiate(self, sim=None, icell=None):
                """Instantiate recording."""
                logger.debug(
                    "Adding compartment recording of %s at %s", self.variable, self.location
                )

                self.varvector = sim.neuron.h.Vector()
                seg = self.location.instantiate(sim=sim, icell=icell)
                self.varvector.record(getattr(seg, "_ref_%s" % self.variable), 0.1)

                self.tvector = sim.neuron.h.Vector()
                self.tvector.record(sim.neuron.h._ref_t, 0.1)  # pylint: disable=W0212

                self.instantiated = True


        def multi_locations(sectionlist):
            """Define mechanisms."""
            if sectionlist == "alldend":
                seclist_locs = [
                    ephys.locations.NrnSeclistLocation("apical", seclist_name="apical"),
                    ephys.locations.NrnSeclistLocation("basal", seclist_name="basal"),
                ]
            elif sectionlist == "somadend":
                seclist_locs = [
                    ephys.locations.NrnSeclistLocation("apical", seclist_name="apical"),
                    ephys.locations.NrnSeclistLocation("basal", seclist_name="basal"),
                    ephys.locations.NrnSeclistLocation("somatic", seclist_name="somatic"),
                ]
            elif sectionlist == "somaxon":
                seclist_locs = [
                    ephys.locations.NrnSeclistLocation("axonal", seclist_name="axonal"),
                    ephys.locations.NrnSeclistLocation("somatic", seclist_name="somatic"),
                ]
            elif sectionlist == "allact":
                seclist_locs = [
                    ephys.locations.NrnSeclistLocation("apical", seclist_name="apical"),
                    ephys.locations.NrnSeclistLocation("basal", seclist_name="basal"),
                    ephys.locations.NrnSeclistLocation("somatic", seclist_name="somatic"),
                    ephys.locations.NrnSeclistLocation("axonal", seclist_name="axonal"),
                ]
            else:
                seclist_locs = [
                    ephys.locations.NrnSeclistLocation(sectionlist, seclist_name=sectionlist)
                ]

            return seclist_locs


        def load_mechanisms(mechs_filename):
            """Define mechanisms."""
            with open(mechs_filename) as mechs_file:
                mech_definitions = json.load(
                    mechs_file, object_pairs_hook=collections.OrderedDict
                )["mechanisms"]

            mechanisms_list = []
            for sectionlist, channels in mech_definitions.items():

                seclist_locs = multi_locations(sectionlist)

                for channel in channels["mech"]:
                    mechanisms_list.append(
                        ephys.mechanisms.NrnMODMechanism(
                            name="%s.%s" % (channel, sectionlist),
                            mod_path=None,
                            suffix=channel,
                            locations=seclist_locs,
                            preloaded=True,
                        )
                    )

            return mechanisms_list


        def define_parameters(params_filename):
            """Define parameters."""
            parameters = []

            with open(params_filename) as params_file:
                definitions = json.load(params_file, object_pairs_hook=collections.OrderedDict)

            # set distributions
            distributions = collections.OrderedDict()
            distributions["uniform"] = ephys.parameterscalers.NrnSegmentLinearScaler()

            distributions_definitions = definitions["distributions"]
            for distribution, definition in distributions_definitions.items():

                if "parameters" in definition:
                    dist_param_names = definition["parameters"]
                else:
                    dist_param_names = None
                distributions[
                    distribution
                ] = ephys.parameterscalers.NrnSegmentSomaDistanceScaler(
                    name=distribution,
                    distribution=definition["fun"],
                    dist_param_names=dist_param_names,
                )

            params_definitions = definitions["parameters"]

            if "__comment" in params_definitions:
                del params_definitions["__comment"]

            for sectionlist, params in params_definitions.items():
                if sectionlist == "global":
                    seclist_locs = None
                    is_global = True
                    is_dist = False
                elif "distribution_" in sectionlist:
                    is_dist = True
                    seclist_locs = None
                    is_global = False
                    dist_name = sectionlist.split("distribution_")[1]
                    dist = distributions[dist_name]
                else:
                    seclist_locs = multi_locations(sectionlist)
                    is_global = False
                    is_dist = False

                bounds = None
                value = None
                for param_config in params:
                    param_name = param_config["name"]

                    if isinstance(param_config["val"], (list, tuple)):
                        is_frozen = False
                        bounds = param_config["val"]
                        value = None

                    else:
                        is_frozen = True
                        value = param_config["val"]
                        bounds = None

                    if is_global:
                        parameters.append(
                            ephys.parameters.NrnGlobalParameter(
                                name=param_name,
                                param_name=param_name,
                                frozen=is_frozen,
                                bounds=bounds,
                                value=value,
                            )
                        )
                    elif is_dist:
                        parameters.append(
                            ephys.parameters.MetaParameter(
                                name="%s.%s" % (param_name, sectionlist),
                                obj=dist,
                                attr_name=param_name,
                                frozen=is_frozen,
                                bounds=bounds,
                                value=value,
                            )
                        )

                    else:
                        if "dist" in param_config:
                            dist = distributions[param_config["dist"]]
                            use_range = True
                        else:
                            dist = distributions["uniform"]
                            use_range = False

                        if use_range:
                            parameters.append(
                                ephys.parameters.NrnRangeParameter(
                                    name="%s.%s" % (param_name, sectionlist),
                                    param_name=param_name,
                                    value_scaler=dist,
                                    value=value,
                                    bounds=bounds,
                                    frozen=is_frozen,
                                    locations=seclist_locs,
                                )
                            )
                        else:
                            parameters.append(
                                ephys.parameters.NrnSectionParameter(
                                    name="%s.%s" % (param_name, sectionlist),
                                    param_name=param_name,
                                    value_scaler=dist,
                                    value=value,
                                    bounds=bounds,
                                    frozen=is_frozen,
                                    locations=seclist_locs,
                                )
                            )

            return parameters


        def define_protocols(cell, var_list):
            """Define Protocols."""
            # load config
            cvcode_active = False

            # recording location
            soma_loc = ephys.locations.NrnSeclistCompLocation(
                name="soma", seclist_name="somatic", sec_index=0, comp_x=0.5
            )

            step_protocols = []

            # load config data
            total_duration = 3000
            step_delay = 700
            step_duration = 2000
            hold_step_delay = 0
            hold_step_duration = 3000

            # protocol names
            protocol_names = ["step{}".format(x) for x in range(1, 4)]

            # define current amplitude data
            amplitudes = [
                0.0378085112412,
                0.0504113483216,
                0.063014185402,
            ]  # do not take 1st value (hypamp)
            hypamp = -0.0144071499339
            for protocol_name, amplitude in zip(protocol_names, amplitudes):
                # use RecordingCustom to sample time, voltage every 0.1 ms.
                rec = []
                for var in var_list:
                    rec.append(
                        RecordingCustom(
                            name=protocol_name + "_" + var, location=soma_loc, variable=var
                        )
                    )

                # create step stimulus
                stim = ephys.stimuli.NrnSquarePulse(
                    step_amplitude=amplitude,
                    step_delay=step_delay,
                    step_duration=step_duration,
                    location=soma_loc,
                    total_duration=total_duration,
                )

                # create holding stimulus
                hold_stim = ephys.stimuli.NrnSquarePulse(
                    step_amplitude=hypamp,
                    step_delay=hold_step_delay,
                    step_duration=hold_step_duration,
                    location=soma_loc,
                    total_duration=total_duration,
                )

                # create protocol
                stims = [stim, hold_stim]
                protocol = ephys.protocols.SweepProtocol(
                    protocol_name, stims, rec, cvcode_active
                )

                step_protocols.append(protocol)

            return ephys.protocols.SequenceProtocol("twostep", protocols=step_protocols)


        def main():
            """Main."""

            # output directory
            output_dir = "output_example"
            # create output directory if needed
            if not os.path.isdir(output_dir):
                os.makedirs(output_dir)

            base_dir_1 = "/gpfs/bbp.cscs.ch/home/ajaquier/Eve-Marder-style-module/output"
            base_dir_2 = os.path.join(base_dir_1, "memodel_dirs/L23_BP/bNAC/L23_BP_bNAC_150")
            emodel = "bNAC_L23SBC"

            # load morphology
            morph_path = os.path.join(
                base_dir_2,
                "morphology",
                "C230998A-I3_-_Scale_x1.000_y0.975_z1.000_-_Clone_2.asc",
            )
            morph = ephys.morphologies.NrnFileMorphology(morph_path)

            # load mechanisms
            params_filename = os.path.join(base_dir_1, "config", "params", "int.json")
            mechs = load_mechanisms(params_filename)

            # load parameters
            with open(os.path.join(base_dir_1, "config", "params", "final.json"), "r") as f:
                params_file = json.load(f)
            data = params_file[emodel]
            release_params = data["params"]

            params = define_parameters(params_filename)

            # create cell
            cell = ephys.models.CellModel(name=emodel, morph=morph, mechs=mechs, params=params)

            # simulator
            sim = ephys.simulators.NrnSimulator(dt=0.025)

            # create protocols
            # voltage and currents to be recorded
            var_list = [
                "v",
                "ihcn_Ih",
                # "ica_Ca_HVA",
                "ica_Ca_HVA2",
                "ica_Ca_LVAst",
                "ik_K_Pst",
                "ik_K_Tst",
                # "ik_KdShu2007",
                # "ina_Nap_Et2",
                "ina_NaTg",
                # "ina_NaTg2",
                "ik_SK_E2",
                "ik_SKv3_1",
                # "ik_StochKv2",
                # "ik_StochKv3",
            ]
            protocols = define_protocols(cell, var_list)

            # run
            print("Python Recordings Running...")

            responses = protocols.run(cell_model=cell, param_values=release_params, sim=sim)

            # get soma area
            nrn = nm.load_neuron(morph_path)
            soma_area = nm.get("soma_surface_areas", nrn)[0]

            for key, resp in responses.items():
                output_path = os.path.join(output_dir, "soma_" + key + ".dat")

                time = np.array(resp["time"])
                soma_data = np.array(resp["voltage"])  # can be voltage or current density
                if key[-2:] != "_v":  # current, not voltage
                    soma_data = 10 * soma_area * soma_data  # turn mA/cm2 into pA

                np.savetxt(output_path, np.transpose(np.vstack((time, soma_data))))

            print("Python Recordings Done")


        if __name__ == "__main__":
            main()

