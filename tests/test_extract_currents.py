"""Test extract currents functions."""

from contextlib import contextmanager
import os
import shutil
import subprocess

import json

from extract_currs.protocols_func import create_protocols
from extract_currs.main_func import extract


@contextmanager
def cwd(path):
    """Cwd function that can be used in a context manager."""
    old_dir = os.getcwd()
    os.chdir(path)
    yield
    os.chdir(old_dir)


def compare_step_prot(p_class, p_dict):
    """Assert that the values in protocol dictionary corresponds to values in protocol class."""
    if "holding" in p_dict:
        assert p_class.holding_stimulus.step_amplitude == p_dict["holding"]["amp"]
        assert p_class.holding_stimulus.step_delay == p_dict["holding"]["delay"]
        assert p_class.holding_stimulus.step_duration == p_dict["holding"]["duration"]
        assert (
            p_class.holding_stimulus.total_duration == p_dict["holding"]["totduration"]
        )
    else:
        assert p_class.holding_stimulus is None

    assert p_class.step_stimuli[0].step_amplitude == p_dict["step"]["amp"]
    assert p_class.step_stimuli[0].step_delay == p_dict["step"]["delay"]
    assert p_class.step_stimuli[0].step_duration == p_dict["step"]["duration"]
    assert p_class.step_stimuli[0].total_duration == p_dict["step"]["totduration"]


def compare_stepthreshold_prot(p_class, p_dict):
    """Assert that the values in protocol dictionary corresponds to values in protocol class."""
    assert p_class.holding_stimulus.step_delay == 0
    assert p_class.holding_stimulus.step_duration == p_dict["step"]["totduration"]
    assert p_class.holding_stimulus.total_duration == p_dict["step"]["totduration"]

    assert p_class.step_stimuli[0].step_delay == p_dict["step"]["delay"]
    assert p_class.step_stimuli[0].step_duration == p_dict["step"]["duration"]
    assert p_class.step_stimuli[0].total_duration == p_dict["step"]["totduration"]

    assert p_class.thresh_perc == p_dict["step"]["thresh_perc"]


def test_create_protocols():
    """Test create_protocols function."""
    emodel = "bNAC_L23SBC"

    var_list = [
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
        "i_pas",
    ]

    base_dir = os.path.join("tests", "config")

    morph_name = "_"
    morph_filename = "C230998A-I3_-_Scale_x1.000_y0.975_z1.000_-_Clone_2.asc"
    altmorph = [[morph_name, os.path.join(base_dir, "morphology", morph_filename)]]

    prot_path = os.path.join(base_dir, "protocol_test.json")
    features_path = ""

    protocols_dict = create_protocols(
        emodel,
        var_list,
        altmorph=altmorph,
        prot_path=prot_path,
        features_path=features_path,
    )

    step_prot = protocols_dict["test"]
    with open(prot_path, "r") as f:
        original_prot = json.load(f)
    orig_stim = original_prot["test"]["stimuli"]

    # rec.name is, e.g., '_.test.soma.v'
    locs = [rec.name.split(".") for rec in step_prot.recordings]
    locs = [item for sublist in locs for item in sublist]  # convert to a flat list
    assert "soma" in locs
    assert "ais" in locs

    compare_step_prot(step_prot, orig_stim)


def test_output():
    """Checks output from extract."""
    subprocess.call(["nrnivmodl", "mechanisms"])

    dir_ = os.path.join("tests", "output_bNAC_L23SBC")

    if os.path.isdir(dir_):
        shutil.rmtree(dir_)
    config = "tests/extract_bNAC_config.json"

    extract(config)

    # here: use only vars that are both in soma and ais
    var_list = [
        "v",
        "ica_Ca_HVA2",
        "ica_Ca_LVAst",
        "ik_K_Pst",
        "ik_K_Tst",
        "ina_NaTg",
        "ik_SK_E2",
        "ik_SKv3_1",
        "i_pas",
    ]
    loc_list = ["soma", "ais"]

    for loc in loc_list:
        for var in var_list:
            filename = ".".join(("_.test", loc, var, "dat"))
            assert os.path.isfile(os.path.join(dir_, filename))

    # this var is in soma but not in ais
    assert os.path.isfile(os.path.join(dir_, "_.test.soma.ihcn_Ih.dat"))


def get_prot_from_recipe(recipe_path, emodel):
    """Get protocol json file data from recipe."""
    with open(recipe_path) as f:
        recipes = json.load(f)
    recipe = recipes[emodel]

    prot_path = recipe["protocol"]
    with open(prot_path, "r") as f:
        return json.load(f)


def test_create_protocols_with_recipes():
    """Test create_protocols function using recipes.

    Assumes that there is a 'Main' in dictionary.
    Does not check anything specific to 'extra-recordings' or to 'pre-protocols'.
    """
    emodel = "cADpyr_L5TPC"

    var_list = [
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
        "i_pas",
    ]

    recipe_path = os.path.join("config", "recipes", "recipes.json")

    with cwd("tests"):
        protocols_dict = create_protocols(
            emodel, var_list, recipe_path=recipe_path, etypetest="get_apical_points"
        )

        # protocol from function
        prot = protocols_dict["main_protocol"]

        # protocol from json file
        orig_prot = get_prot_from_recipe(recipe_path, emodel)

    # RMP
    compare_step_prot(prot.rmp_protocol, orig_prot["RMP"]["stimuli"])

    # RinHold
    assert (
        prot.rinhold_protocol.holdi_precision
        == orig_prot["RinHoldcurrent"]["holdi_precision"]
    )
    assert (
        prot.rinhold_protocol.holdi_max_depth
        == orig_prot["RinHoldcurrent"]["holdi_max_depth"]
    )

    # Threshold Detection
    compare_step_prot(
        prot.thdetect_protocol.step_protocol_template,
        orig_prot["ThresholdDetection"]["step_template"]["stimuli"],
    )

    # other protocols
    for protocol in prot.other_protocols:
        assert protocol.name in orig_prot["Main"]["other_protocols"]

        if orig_prot[protocol.name]["type"] == "StepProtocol":
            compare_step_prot(
                protocol,
                orig_prot[protocol.name]["stimuli"],
            )
        elif orig_prot[protocol.name]["type"] == "StepThresholdProtocol":
            compare_stepthreshold_prot(
                protocol,
                orig_prot[protocol.name]["stimuli"],
            )
