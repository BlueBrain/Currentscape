"""Functions to load data."""

import collections
from pathlib import Path
import json

import bluepyopt.ephys as ephys

from extract_currs.locations import multi_locations


def get_path_from_config(config, path_key, dir_key, filename_key):
    """Get path of a file from config."""
    if path_key in config:
        return Path(config[path_key])
    # legacy case
    elif dir_key in config and filename_key in config:
        return Path(config[dir_key]) / config[filename_key]
    raise KeyError(f"Could not find '{path_key}' in configuration file.")


def get_recipe(config, emodel):
    """Get recipe from json file."""
    recipe_path = get_path_from_config(
        config, "recipe_path", "recipe_dir", "recipe_filename"
    )

    # load recipe file
    with open(recipe_path) as f:
        recipes = json.load(f)

    # return emodel recipe data
    return recipes[emodel]


def get_morphology_from_recipe(recipe):
    """Load the morphology from recipe data."""
    morph_path = str(Path(recipe["morph_path"]) / recipe["morphology"][0][1])
    return ephys.morphologies.NrnFileMorphology(morph_path)


def get_morphology_from_config(config):
    """Load the morphology and morphology data from config."""
    morph_name = config["morph_name"]
    morph_filename = config["morph_filename"]
    apical_point_isec = config["apical_point_isec"]
    morph_dir = config["morph_dir"]

    morph_path = str(Path(morph_dir) / morph_filename)
    if apical_point_isec is not None:
        altmorph = [[morph_name, morph_filename, apical_point_isec]]
    else:
        altmorph = [[morph_name, morph_filename]]

    morph = ephys.morphologies.NrnFileMorphology(morph_path)

    return morph, altmorph


def get_parameters_path_from_config(config):
    """Get the parameters path from config."""
    return get_path_from_config(config, "params_path", "params_dir", "params_filename")


def get_final_parameters_path_from_config(config):
    """Get the final parameters path from config."""
    return get_path_from_config(
        config, "final_params_path", "final_params_dir", "final_params_filename"
    )


def get_protocols_path_from_config(config):
    """Get the protocols path from config."""
    return get_path_from_config(
        config, "protocols_path", "protocols_dir", "protocols_filename"
    )


def get_features_path_from_config(config):
    """Get the features path from config."""
    return get_path_from_config(
        config, "features_path", "features_dir", "features_filename"
    )


def get_apical_point_from_recipe_var_from_config(config):
    """Get apical_point_from_recipe boolean from config."""
    if "apical_point_from_recipe" in config:
        return config["apical_point_from_recipe"]
    elif "etypetest" in config:
        return bool(config["etypetest"])
    raise KeyError("Could not find 'apical_point_from_recipe' in configuration file")


def load_mechanisms(mechs_path):
    """Define mechanisms.

    The mechanism path is the same as the params path.
    """
    with open(mechs_path) as mechs_file:
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


def define_parameters(params_path):
    """Define parameters."""
    parameters = []

    with open(params_path) as params_file:
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
