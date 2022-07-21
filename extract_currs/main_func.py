"""Useful functions to load mechanisms and parameters."""

import logging
import os

import json

import bluepyopt.ephys as ephys

from extract_currs.load import (
    define_parameters,
    get_apical_point_from_recipe_var_from_config,
    get_features_path_from_config,
    get_final_parameters_path_from_config,
    get_morphology_from_config,
    get_morphology_from_recipe,
    get_parameters_path_from_config,
    get_protocols_path_from_config,
    get_recipe,
    load_mechanisms,
)
from extract_currs.protocols_func import create_protocols
from extract_currs.output import write_output

logger = logging.getLogger(__name__)


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
        recipe = get_recipe(config, emodel)

    # ------------------------#
    # --- load morphology --- #
    # ------------------------#
    # altmorph is only used when recipes are not used
    if use_recipes:
        morph = get_morphology_from_recipe(recipe)
    else:
        morph, altmorph = get_morphology_from_config(config)

    # ------------------------#
    # --- load mechanisms --- #
    # ------------------------#
    if use_recipes:
        params_path = recipe["params"]
    else:
        params_path = get_parameters_path_from_config(config)
    mechs = load_mechanisms(params_path)
    logger.info("mechanisms are loaded")

    # ------------------------#
    # --- load parameters --- #
    # ------------------------#
    with open(get_final_parameters_path_from_config(config), "r") as f:
        params_file = json.load(f)
    data = params_file[emodel]
    release_params = data["params"]

    params = define_parameters(params_path)

    logger.info("parameters are loaded")

    # --------------------------------#
    # --- create cell & simulator --- #
    # --------------------------------#
    cell = ephys.models.CellModel(name=emodel, morph=morph, mechs=mechs, params=params)
    logger.info("cell is loaded")
    sim = ephys.simulators.NrnSimulator(dt=0.025, cvode_active=False)

    logger.info("simulator is loaded")

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
        apical_point_from_recipe = get_apical_point_from_recipe_var_from_config(config)
        protocols_dict = create_protocols(
            var_list,
            recipe=recipe,
            apical_point_from_recipe=apical_point_from_recipe,
        )
    else:
        prot_path = get_protocols_path_from_config(config)
        features_path = get_features_path_from_config(config)
        protocols_dict = create_protocols(
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
    logger.info("Python Recordings Running...")

    responses = protocols.run(cell_model=cell, param_values=release_params, sim=sim)

    logger.info("Python Recordings Done. Writing down Recordings...")

    # ---------------------#
    # --- write output --- #
    # ---------------------#
    write_output(responses, output_dir)

    logger.info("Recordings written.")
