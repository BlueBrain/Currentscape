"""Useful functions to load mechanisms and parameters."""

import collections
import os

import json
import numpy as np

import bluepyopt.ephys as ephys

from extract_currs.protocols_func import create_protocols


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


def extract(config):
    """Main.

    Args:
        config (str or dict): dict or filename of json file containing config.
    """
    # load config if config is in a json file
    if isinstance(config, str):
        with open(config, "r") as f:
            config = json.load(f)

    emodel = config["emodel"]

    # output directory
    output_dir = config["output_dir"]
    if (
        "join_emodel_to_output_dir_name" in config
        and config["join_emodel_to_output_dir_name"]
    ):
        output_dir = "_".join((output_dir, emodel))
    # create output directory if needed
    if not os.path.isdir(output_dir):
        os.makedirs(output_dir)

    # a config folder with protocols, features and params files
    # should be present when recipe_path is set
    use_recipes = config["use_recipes"]
    if use_recipes:
        recipe_path = os.path.join(config["recipe_dir"], config["recipe_filename"])
        with open(recipe_path) as f:
            recipes = json.load(f)
        recipe = recipes[emodel]

    # ------------------------#
    # --- load morphology --- #
    # ------------------------#
    if use_recipes:
        morph_path = os.path.join(recipe["morph_path"], recipe["morphology"][0][1])
    else:
        morph_name = config["morph_name"]
        morph_filename = config["morph_filename"]
        apical_point_isec = config["apical_point_isec"]
        morph_dir = config["morph_dir"]

        morph_path = os.path.join(morph_dir, morph_filename)
        if apical_point_isec is not None:
            altmorph = [[morph_name, morph_filename, apical_point_isec]]
        else:
            altmorph = [[morph_name, morph_filename]]

    morph = ephys.morphologies.NrnFileMorphology(morph_path)

    # ------------------------#
    # --- load mechanisms --- #
    # ------------------------#
    if use_recipes:
        params_filename = recipe["params"]
    else:
        params_filename = os.path.join(config["params_dir"], config["params_filename"])
    mechs = load_mechanisms(params_filename)

    # ------------------------#
    # --- load parameters --- #
    # ------------------------#
    with open(
        os.path.join(config["final_params_dir"], config["final_params_filename"]), "r"
    ) as f:
        params_file = json.load(f)
    data = params_file[emodel]
    release_params = data["params"]

    params = define_parameters(params_filename)

    # --------------------------------#
    # --- create cell & simulator --- #
    # --------------------------------#
    cell = ephys.models.CellModel(name=emodel, morph=morph, mechs=mechs, params=params)
    sim = ephys.simulators.NrnSimulator(dt=0.025)

    # -------------------------#
    # --- create protocols --- #
    # -------------------------#
    # voltage and currents to be recorded
    # if a current is not found for a given location, it is discarded for this location.
    var_list = config["var_list"]

    # must always set: emodel var_list
    # either set: recipe
    # or set: altmorph, prot_path, feature_path (if "Main" in protocols)
    if use_recipes:
        etypetest = config["etypetest"]
        protocols_dict = create_protocols(
            emodel, var_list, recipe_path=recipe_path, etypetest=etypetest
        )
    else:
        prot_path = os.path.join(config["protocols_dir"], config["protocols_filename"])
        features_path = os.path.join(
            config["features_dir"], config["features_filename"]
        )
        protocols_dict = create_protocols(
            emodel,
            var_list,
            altmorph=altmorph,
            prot_path=prot_path,
            features_path=features_path,
        )

    protocols_list = list(protocols_dict.values())
    protocols = ephys.protocols.SequenceProtocol(
        "all protocols",
        protocols=protocols_list,
    )

    # ------------#
    # --- run --- #
    # ------------#
    print("Python Recordings Running...")

    responses = protocols.run(cell_model=cell, param_values=release_params, sim=sim)

    # ---------------------#
    # --- write output --- #
    # ---------------------#
    for key, resp in responses.items():
        if "holding_current" in key or "threshold_current" in key:
            print("{} : {}".format(key, resp))
        else:
            output_path = os.path.join(output_dir, key + ".dat")

            time = np.array(resp["time"])
            data = np.array(resp["voltage"])  # can be voltage or current

            np.savetxt(output_path, np.transpose(np.vstack((time, data))))

    print("Python Recordings Done")